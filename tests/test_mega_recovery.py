"""NIST AES vectors and provider failure cases, using only synthetic bytes."""

import base64
import io
import json
import struct
from pathlib import Path

import pytest

from drumforge.library import mega_recovery as mega


@pytest.mark.parametrize(
    ("mode", "iv", "ciphertext"),
    [
        ("ctr", "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff", "874d6191b620e3261bef6864990db6ce"),
        ("cbc", "000102030405060708090a0b0c0d0e0f", "7649abac8119b246cee98e9b12e9197d"),
    ],
)
def test_openssl_aes_matches_nist_sp800_38a(mode: str, iv: str, ciphertext: str) -> None:
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    plain = bytes.fromhex("6bc1bee22e409f96e93d7e117393172a")
    with mega.aes(key, bytes.fromhex(iv), mode) as decrypt:
        assert decrypt(bytes.fromhex(ciphertext)) == plain
    with mega.aes(key, bytes.fromhex(iv), mode, True) as encrypt:
        assert encrypt(plain) == bytes.fromhex(ciphertext)


def test_mega_quota_error_never_writes_a_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mega, "urlopen", lambda *a, **kw: io.BytesIO(b"[-509]"))
    key = base64.urlsafe_b64encode(bytes(32)).decode().rstrip("=")
    target = tmp_path / "source"
    with pytest.raises(ValueError, match="limite do provedor"):
        mega.download("https://mega.nz/#!abcdefgh!" + key, target, 1000)
    assert not target.exists()


def test_mega_wrong_mac_is_rejected_and_existing_files_are_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    nonce = bytes.fromhex("0001020304050607")
    trailer = nonce + bytes(8)  # deliberately wrong, zero expected authentication tag
    words = struct.unpack(">4I", key)
    extra = struct.unpack(">4I", trailer)
    full_key = struct.pack(">8I", *(tuple(words[i] ^ extra[i] for i in range(4)) + extra))
    link = "https://mega.nz/#!abcdefgh!" + base64.urlsafe_b64encode(full_key).decode().rstrip("=")
    attributes = b'MEGA{"n":"synthetic"}'
    with mega.aes(key, bytes(16), "cbc", True) as encrypt:
        at = encrypt(attributes + bytes(-len(attributes) % 16))
    plain = b"authored synthetic data, no media" * 3
    with mega.aes(key, nonce + bytes(8), "ctr", True) as encrypt:
        encrypted = encrypt(plain)
    responses = iter(
        [
            json.dumps(
                [
                    {
                        "s": len(plain),
                        "at": base64.urlsafe_b64encode(at).decode(),
                        "g": "https://example.com/synthetic",
                    }
                ]
            ).encode(),
            encrypted,
        ]
    )
    monkeypatch.setattr(mega, "urlopen", lambda *a, **kw: io.BytesIO(next(responses)))
    target = tmp_path / "source"
    with pytest.raises(ValueError, match="autenticidade"):
        mega.download(link, target, 1000)
    assert not target.exists()
    target.write_bytes(b"user file")
    with pytest.raises(FileExistsError, match="preservado"):
        mega.download(link, target, 1000)
    assert target.read_bytes() == b"user file"
