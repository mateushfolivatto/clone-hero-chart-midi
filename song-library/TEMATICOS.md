# Novos lotes de bateria — 2026-10-25

Foram preparados **45 charts novos em 6 lotes**:
11 de League of Legends/projetos associados, 13 de
Imagine Dragons e 21 de bandas próximas de Linkin Park.
São 39 Pro Drums e 6 Drums comuns.

| Lote | Seleção | Modo / Expert | Charts | ZIP |
| --- | --- | --- | ---: | ---: |
| 13 | League of Legends | Pro Drums | 9 | 65.8 MiB |
| 14 | League of Legends | Drums comuns | 2 | 6.9 MiB |
| 15 | Imagine Dragons | Pro Drums | 11 | 90.1 MiB |
| 16 | Imagine Dragons | Drums comuns | 2 | 12.4 MiB |
| 17 | Bandas semelhantes a Linkin Park | Pro Drums | 19 | 205.5 MiB |
| 18 | Bandas semelhantes a Linkin Park | Drums comuns | 2 | 26.9 MiB |

League of Legends inclui temas do jogo, K/DA, Pentakill e “Enemy”, de Arcane.
“Enemy” aparece somente nessa seleção, evitando duplicá-la em Imagine Dragons.
As bandas semelhantes são Papa Roach, Breaking Benjamin, Three Days Grace,
Evanescence, P.O.D., Limp Bizkit e Bring Me the Horizon; a escolha combina
proximidade musical e disponibilidade de bateria verificada.

O piloto e os lotes 02–12 foram comparados por artista/título normalizados,
ID de pacote, hash da origem e conjunto de hashes de chart/áudio. Nenhuma música
desses lotes foi repetida. “Heavy Is the Crown”, do Linkin Park, já está no
**lote 09** e foi excluída. A biblioteca antiga particular ainda depende do
comparador [SEM-REPETIDAS.md](SEM-REPETIDAS.md).

As receitas antigas, áudios, escolhas e o relatório das 744 entradas do Qobuz
permanecem intactos. Esta é uma curadoria temática independente: não foram
inventados IDs do Qobuz nem aumentada artificialmente a cobertura daquela playlist.
[lotes-tematicos.csv](reports/lotes-tematicos.csv) registra a seleção preparada,
as tentativas bloqueadas e as exclusões. Não é um levantamento integral das
discografias. “Warriors”, “GODS” e “STAR WALKIN” ficaram sem correspondência
de bateria nos catálogos pesquisados; isso não prova inexistência global.

## Baixar somente estes novos lotes no Windows

Espere qualquer baixador anterior terminar ou encerre-o com Ctrl+C antes de
executar este bloco. Ele usa um baixador separado em `Baixador-Tematicos`, mantém
o destino `Downloads\MixDrumRock` e seleciona somente os lotes novos.
Para escolher alguns, altere apenas `$lotes`. Se usa outro destino, ajuste `$pasta`.

Precisa de Python 3.11+ e Windows 10/11 x64. As origens somam aproximadamente
**0,44 GiB**, e os ZIPs **0,40 GiB**.
Reserve **4 GB livres** para estes lotes,
originais, conversão e ZIPs. Não exige uv, Mido, FFmpeg, login de provedor ou
permissão administrativa. Os leitores portáteis têm versão e SHA256 fixos.

Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\MixDrumRock'
    $baixador = Join-Path $pasta 'Baixador-Tematicos'
    $lotes = @(13, 14, 15, 16, 17, 18)
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    foreach ($numero in $lotes) {
        $lote = @($indice.batches | Where-Object { $_.number -eq $numero })
        if ($lote.Count -ne 1 -or $lote[0].manifest -notmatch '^collection_[0-9]{2,}\.json$') {
            throw "Receita do lote $numero invalida ou ausente"
        }
        $receita = $lote[0].manifest
        Invoke-WebRequest -Uri "$base/$receita" -OutFile (Join-Path $baixador $receita) -UseBasicParsing
    }
    $pendentes = @()
    foreach ($numero in $lotes) {
        py -3 (Join-Path $baixador 'recover_pilot.py') --restante --lote $numero --destino $pasta
        if ($LASTEXITCODE -eq 130) { throw 'Interrompido pelo teclado. Execute o mesmo bloco para retomar.' }
        if ($LASTEXITCODE -ne 0) { $pendentes += $numero }
    }
    if ($pendentes.Count -gt 0) { throw "Lotes com pendencias: $pendentes. Execute novamente para retomar." }
    Write-Host "Pastas prontas em $(Join-Path $pasta 'Songs')"
}
```

O baixador verifica índice, receitas, ferramentas, origens e arquivos preparados.
O mesmo bloco retoma falhas e reaproveita downloads e músicas conferidos;
arquivos locais alterados são preservados. Uma falha não impede tentar os demais
lotes. Os arquivos `*-falhas.json` identificam pendências e pode haver ZIP parcial.
Links de terceiros podem mudar ou atingir cotas; as receitas não garantem acesso
permanente. O comando geral de CONTINUACAO.md agora inclui também estes lotes;
o bloco acima seleciona apenas a nova curadoria.

## Onyx e uso no jogo

As correções recentes foram preservadas: nenhum argumento RTS no Onyx CLI do
Windows, logs persistentes em `Logs\Onyx`, feedback a cada 15 segundos,
criação do processo medida separadamente e limites de espera de 180/900 segundos
na importação/exportação. Os arquivos `.tempos.jsonl` continuam disponíveis.
Ctrl+C encerra a execução com instruções de retomada. Não foi prometida aceleração
nem diagnosticada a causa da demora anterior no Windows.

Copie as novas pastas de dentro de `Songs` para a biblioteca do Clone Hero e
execute **Scan Songs**. Use **Pro Drums / Expert** ou **Drums / Expert** conforme
a tabela e o nome da pasta. Mantenha o áudio de cada chart. Pacotes nativos
mantêm notas/áudios; entradas de Rock Band foram convertidas pelo Onyx fixado.
Cinco pistas não foram disfarçadas como quatro e Drums comuns não foram
promovidos a Pro Drums. Autores, fontes e hashes estão nas receitas e em cada ZIP.

Todos os arquivos foram inspecionados na nuvem Linux/Python 3.12. A execução no
Windows, sincronismo percebido e jogabilidade ainda precisam do seu teste;
`game_verified` permanece falso. A causa da demora anterior do Windows não foi
inferida dos tempos da nuvem.

## Músicas por lote

### Lote 13 — Pro Drums

- Imagine Dragons — Enemy (feat. JID)
- K/DA — PopStars (ft Madison Beer, (G)I-DLE, Jaira Burns)
- League of Legends — Legends Never Die
- League of Legends, Cailin Russo, Chrissy Costanza — Phoenix
- Nicki Taylor — Here Comes Vi
- Pentakill — Lightbringer
- Pentakill — Lost Chapter
- Pentakill — Mortal Reminder
- Pentakill — Tear of the Goddess

### Lote 14 — Drums comuns

- Riot & Djerv — Get Jinxed
- The Glitch Mob, Mako, and The Word Alive — RISE

### Lote 15 — Pro Drums

- Imagine Dragons — Amsterdam
- Imagine Dragons — Battle Cry
- Imagine Dragons — Bones
- Imagine Dragons — Demons
- Imagine Dragons — It's Time
- Imagine Dragons — Lonely
- Imagine Dragons — Nothing Left to Say/Rocks
- Imagine Dragons — Sharks
- Imagine Dragons — Shots
- Imagine Dragons — Tiptoe
- Imagine Dragons — Whatever It Takes

### Lote 16 — Drums comuns

- Imagine Dragons — On Top of the World
- Imagine Dragons — Radioactive

### Lote 17 — Pro Drums

- Breaking Benjamin — Blow Me Away
- Breaking Benjamin — Dance With the Devil
- Bring Me the Horizon — Can You Feel My Heart
- Bring Me The Horizon — Drown
- Bring Me the Horizon — Sleepwalking
- Evanescence — My Heart is Broken
- Evanescence — Sweet Sacrifice
- Evanescence — Tourniquet
- Limp Bizkit — Break Stuff
- Limp Bizkit — My Way
- P.O.D. — Satellite
- P.O.D. — Sleeping Awake
- P.O.D. — Southtown
- Papa Roach — Getting Away with Murder
- Papa Roach — Last Resort
- Papa Roach — Scars
- Three Days Grace — I Hate Everything About You
- Three Days Grace — Never Too Late
- Three Days Grace — Riot

### Lote 18 — Drums comuns

- Breaking Benjamin — The Diary of Jane
- Limp Bizkit — Rollin' (Air Raid Vehicle)

## Prompt para a próxima sessão

> No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
> BACKLOG.md e lessons.md; depois song-library/CONTINUACAO.md,
> song-library/TEMATICOS.md e docs/library-themed-verification.md. Continue somente
> a biblioteca. Há 45 novos charts temáticos nos lotes 13–18,
> além dos 266 anteriores; as receitas são imutáveis, sem mídia no Git.
> Preserve as correções do Onyx, o piloto, as escolhas anteriores e o relatório
> Qobuz de 744 entradas; a curadoria temática tem IDs Qobuz vazios. Compare novas
> músicas contra todos os lotes por identidade, fonte e conteúdo antes de acrescentar
> receitas. Revise o resultado do usuário no Windows/Scan Songs/playtest e marque
> game_verified apenas com confirmação real. Se houver demora, use o .log e o
> .tempos.jsonl locais; não atribua causa com base no Linux. Consulte
> reports/lotes-tematicos.csv para bloqueios, sem repetir origens indisponíveis
> sem nova evidência. Trabalhe em branch a partir de main, rode os gates de
> docs/testing.md, atualize status/evidências e conclua com commit, merge --no-ff,
> push e verificação da sincronização, preservando commits se o push falhar.
