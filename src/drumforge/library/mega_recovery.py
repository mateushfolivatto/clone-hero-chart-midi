"""Read public MEGA links with their supplied keys, using Python's OpenSSL library.

No login, quota workarounds, third-party Python installation or key discovery.
The public-link format uses AES-CTR, AES-CBC attributes and a chunked CBC MAC.
"""

from __future__ import annotations

import base64
import ctypes
import ctypes.util
import json
import re
import struct
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@cache
def library() -> ctypes.CDLL:
    candidates = [
        Path(sys.base_prefix) / "DLLs" / "libcrypto-3.dll",
        Path(sys.base_prefix) / "DLLs" / "libcrypto-1_1.dll",
    ]
    names = [str(path) for path in candidates if path.is_file()]
    system = ctypes.util.find_library("crypto")
    if system:
        names.append(system)
    for name in names:
        try:
            return ctypes.CDLL(name)
        except OSError:
            continue
    raise OSError("Biblioteca OpenSSL do Python nao encontrada para ler o link MEGA")


@contextmanager
def aes(
    key: bytes, iv: bytes, mode: str, encrypt: bool = False
) -> Iterator[Callable[[bytes], bytes]]:
    if len(key) != 16 or len(iv) != 16 or mode not in {"cbc", "ctr"}:
        raise ValueError("Parametros AES invalidos")
    lib = library()
    pointer = ctypes.c_void_p
    lib.EVP_CIPHER_CTX_new.restype = pointer
    lib.EVP_CIPHER_CTX_free.argtypes = [pointer]
    algorithm = getattr(lib, "EVP_aes_128_" + mode)
    algorithm.restype = pointer
    prefix = "EVP_Encrypt" if encrypt else "EVP_Decrypt"
    initialize = getattr(lib, prefix + "Init_ex")
    initialize.argtypes = [pointer, pointer, pointer, ctypes.c_char_p, ctypes.c_char_p]
    update = getattr(lib, prefix + "Update")
    update.argtypes = [
        pointer,
        pointer,
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p,
        ctypes.c_int,
    ]
    finalize = getattr(lib, prefix + "Final_ex")
    finalize.argtypes = [pointer, pointer, ctypes.POINTER(ctypes.c_int)]
    lib.EVP_CIPHER_CTX_set_padding.argtypes = [pointer, ctypes.c_int]
    context = lib.EVP_CIPHER_CTX_new()
    if not context:
        raise ValueError("Falha ao iniciar AES")
    try:
        if initialize(context, algorithm(), None, key, iv) != 1:
            raise ValueError("Falha ao iniciar AES")
        if lib.EVP_CIPHER_CTX_set_padding(context, 0) != 1:
            raise ValueError("Falha ao configurar AES")

        def transform(content: bytes) -> bytes:
            output = ctypes.create_string_buffer(len(content) + 16)
            length = ctypes.c_int()
            if update(context, output, ctypes.byref(length), content, len(content)) != 1:
                raise ValueError("Falha ao processar AES")
            if length.value != len(content):
                raise ValueError("Bloco AES incompleto")
            return bytes(output.raw[: length.value])

        yield transform
        output = ctypes.create_string_buffer(16)
        length = ctypes.c_int()
        if finalize(context, output, ctypes.byref(length)) != 1 or length.value:
            raise ValueError("Dados AES incompletos")
    finally:
        lib.EVP_CIPHER_CTX_free(context)


def decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def download(url: str, target: Path, limit: int) -> None:
    if target.exists():
        raise FileExistsError("Destino MEGA existente; arquivo preservado")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"mega.nz", "mega.co.nz"}:
        raise ValueError("Link publico MEGA invalido")
    old = re.fullmatch(r"!([A-Za-z0-9_-]{8})!([A-Za-z0-9_-]+)", parsed.fragment)
    modern = re.fullmatch(r"/file/([A-Za-z0-9_-]{8})", parsed.path)
    if old:
        identity, encoded_key = old.groups()
    elif modern:
        identity, encoded_key = modern[1], parsed.fragment
    else:
        raise ValueError("Este baixador aceita links publicos MEGA de um arquivo")
    raw_key = decode(encoded_key)
    if len(raw_key) != 32:
        raise ValueError("Chave do link publico MEGA invalida")
    words = struct.unpack(">8I", raw_key)
    key = struct.pack(">4I", *(words[i] ^ words[i + 4] for i in range(4)))
    nonce = struct.pack(">2I", words[4], words[5])
    payload = json.dumps([{"a": "g", "g": 1, "p": identity, "ssl": 2}]).encode()
    request = Request(
        "https://g.api.mega.co.nz/cs?id=1",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=60) as response:
        metadata = json.load(response)[0]
    if not isinstance(metadata, dict):
        raise ValueError(f"MEGA indisponivel ou limite do provedor: {metadata}")
    size = metadata["s"]
    if not isinstance(size, int) or not 0 < size <= limit:
        raise ValueError("Arquivo MEGA excede o tamanho permitido")
    with aes(key, bytes(16), "cbc") as decrypt:
        attributes = decrypt(decode(metadata["at"])).rstrip(b"\0")
    if not attributes.startswith(b"MEGA{"):
        raise ValueError("Chave MEGA nao corresponde aos atributos do arquivo")
    json.loads(attributes[4:])
    if urlparse(metadata["g"]).scheme != "https":
        raise ValueError("Origem MEGA nao oferece HTTPS")
    tag = bytes(16)
    received = 0
    chunk_size = 128 * 1024
    with urlopen(metadata["g"], timeout=90) as response, target.open("xb") as output:
        with aes(key, nonce + bytes(8), "ctr") as decrypt, aes(key, bytes(16), "cbc", True) as mac:
            while received < size:
                amount = min(chunk_size, size - received)
                encrypted = response.read(amount)
                if len(encrypted) != amount:
                    raise ValueError("Download MEGA incompleto")
                plain = decrypt(encrypted)
                output.write(plain)
                padded = plain + bytes(-len(plain) % 16)
                with aes(key, nonce * 2, "cbc", True) as chunk_mac:
                    tag = mac(chunk_mac(padded)[-16:])
                received += amount
                chunk_size = min(chunk_size + 128 * 1024, 1024 * 1024)
            if response.read(1):
                raise ValueError("Tamanho MEGA mudou durante o download")
    mac_words = struct.unpack(">4I", tag)
    if (mac_words[0] ^ mac_words[1], mac_words[2] ^ mac_words[3]) != words[6:8]:
        target.unlink(missing_ok=True)
        raise ValueError("Verificacao de autenticidade MEGA falhou")
