# Baixar o lote de 12 músicas no seu PC

A pasta `data` é gerada na máquina que executa a preparação. Ela é ignorada pelo
Git, então não aparece no GitHub e não existe automaticamente no seu computador.
Na retomada de 2026-10-17, a máquina da nuvem voltou ao checkout inicial e os
arquivos locais do lote anterior não estavam mais presentes. O link do chat
apontava para esse arquivo ausente; ele não era um endereço público de download.

O lote foi recuperado e sua receita de fontes/hashes agora está no repositório.
Use o baixador abaixo para obter as mesmas 12 músicas diretamente das fontes no
seu Windows, sem depender da pasta da nuvem. Ele precisa somente de Python 3.11
ou mais recente. Não precisa instalar uv, FFmpeg, Mido ou modelos para recuperar
este lote já verificado.

## No PowerShell

Cole este bloco inteiro. Ele cria `Downloads\MixDrumRock`, baixa o programa e sua
receita e prepara as músicas. São aproximadamente 140 MiB de downloads originais;
o ZIP final tem aproximadamente 139 MiB. Há também cópias dos originais e pastas
extraídas, então reserve cerca de 500 MiB no computador.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\MixDrumRock'
    New-Item -ItemType Directory -Path $pasta -Force | Out-Null
    Invoke-WebRequest -Uri "$base/recover_pilot.py" -OutFile (Join-Path $pasta 'baixar_piloto.py') -UseBasicParsing
    Invoke-WebRequest -Uri "$base/pilot_01.json" -OutFile (Join-Path $pasta 'pilot_01.json') -UseBasicParsing
    py -3 (Join-Path $pasta 'baixar_piloto.py') --destino $pasta
}
```

Quando aparecer **Concluido!**, você encontrará:

```text
Downloads\MixDrumRock\
├── MixDrumRock-piloto-12.zip
├── Songs\
│   └── MixDrumRock - Lote teste 01\
│       └── [12 pastas de músicas]
└── Originais\
```

Copie `MixDrumRock - Lote teste 01` para a pasta de músicas configurada no Clone
Hero e execute **Scan Songs**. Escolha **Pro Drums / Expert** em uma versão atual
do jogo. O ZIP inclui `LEIA-ME.txt`, a lista das músicas e a receita com fontes,
autores e checksums.

Se houver uma interrupção de rede, execute o mesmo bloco novamente: músicas já
preparadas e conferidas são reaproveitadas. O programa recusa sobrescrever uma
música alterada e recusa pacotes que diferem dos hashes verificados. Ele não
altera políticas administrativas nem precisa de login no Qobuz ou Google Drive.

## O que foi verificado

As 12 músicas foram recuperadas novamente, com 78 arquivos de uso no jogo.
Na nuvem, os 11 MIDI e um `.chart` passaram pela inspeção de bateria Expert de
quatro pistas e marcações de Pro Drums, e os 40 áudios foram decodificados.
O baixador foi executado fora do projeto, com bibliotecas externas desativadas,
e criou o ZIP com todos os arquivos iguais aos hashes da receita. Uma segunda
execução reaproveitou o lote completo sem modificar seu conteúdo.

O programa usa apenas a biblioteca padrão de Python e preserva áudio/notas;
reproduz somente o ajuste já verificado de `pro_drums=True` em Requiem. Nenhum
arquivo de música foi incluído no Git. O teste em Windows nativo, Scan Songs,
gameplay, seu e-kit e o sincronismo percebido ainda aguardam sua confirmação.

## Fontes originais, se preferir baixar pelo navegador

Os pacotes originais podem conter arquivos auxiliares. O baixador seleciona os
arquivos verificados e organiza tudo automaticamente. Os links abaixo são as
fontes usadas, independentes do armazenamento deste ambiente.

| Artista | Música | Pacote original |
| --- | --- | --- |
| Linkin Park | Numb | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/6524a935c49844cc843919db988dbba2/Linkin%20Park%20-%20Numb.zip) |
| Linkin Park | Lying From You | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/3e2397b44c5549ac98fa4dbfb6f08568/Linkin%20Park%20-%20Lying%20From%20You.zip) |
| Linkin Park | From The Inside | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/0415a5cb53e24e98ab47b45508be147c/Linkin%20Park%20-%20From%20The%20Inside.zip) |
| Nirvana | Come As You Are | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/00fea0c67b034277a07c877115fe6efd/Nirvana%20-%20Come%20as%20you%20Are.zip) |
| Nirvana | Dumb | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/2ba9b778f9cf4de2b24eafccd1a4662d/Nirvana%20-%20Dumb.zip) |
| Nirvana | All Apologies | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/473f6755bdd64d75a5a690df3e49b7d4/Nirvana%20-%20All%20Apologies.zip) |
| Iron Maiden | Fear of the Dark | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/4fc698548df44d31a2669c161922fa94/Iron%20Maiden%20-%20Fear%20of%20The%20Dark.zip) |
| Iron Maiden | Hallowed Be Thy Name | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/ef6143f015d4425498751fa02d740f11/Iron%20Maiden%20-%20Hallowed%20Be%20Thy%20Name.zip) |
| Iron Maiden | The Number of the Beast | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/19300087ad5549a0a5033e3760bb2079/Iron%20Maiden%20-%20The%20Number%20of%20the%20Beast.zip) |
| The Beatles | Come Together | [Baixar ZIP](https://rhythmverse.co/download_file/zak-chayette/c620c633812b4914b7014bd75233e2b2/cometogether_thv2_chps.zip) |
| The Beatles | Here Comes the Sun | [Baixar ZIP](https://rhythmverse.co/download_file/daniel-lugo/cf1f21edcae54d3abfb1818f78d5930b/The%20Beatles%20-%20Here%20Comes%20the%20Sun.zip) |
| Avenged Sevenfold | Requiem | [Baixar ZIP](https://rhythmverse.co/download_file/fernando-ahumada/d74d0dc7acc54cd09aea30794bd37acd/Avenged%20Sevenfold%20-%20Requiem%20%28Fernandinsky%29.zip) |
