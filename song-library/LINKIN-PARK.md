# Linkin Park — ampliação da biblioteca

**“Given Up” já está no lote 02, em Pro Drums / Expert.** A faixa original foi
mantida naquele lote, sem criar outra cópia. “The Emptiness Machine” continua no
lote 07; “Heavy Is the Crown”, no lote 09.

Foram acrescentados **207 charts em 12 lotes novos
(19–30)**: 172 Pro Drums e
35 Drums comuns. Com os 33 charts de Linkin Park já
publicados, são 240 títulos/edições da banda e colaborações.
Demos, remixes e versões ao vivo contam como edições diferentes; isso não significa
240 composições de estúdio nem a discografia integral.

| Lote | Edições | Modo / Expert | Charts |
| --- | --- | --- | ---: |
| 19 | Faixas e raridades | Pro Drums | 25 |
| 20 | Faixas e raridades | Pro Drums | 25 |
| 21 | Faixas e raridades | Pro Drums | 25 |
| 22 | Faixas e raridades | Pro Drums | 1 |
| 23 | Faixas e raridades | Drums comuns | 16 |
| 24 | Demos | Pro Drums | 25 |
| 25 | Demos | Pro Drums | 17 |
| 26 | Demos | Drums comuns | 17 |
| 27 | Ao vivo | Pro Drums | 25 |
| 28 | Ao vivo | Pro Drums | 25 |
| 29 | Ao vivo | Pro Drums | 4 |
| 30 | Ao vivo | Drums comuns | 2 |

## Baixar e comparar com o que já está instalado

O bloco recupera as seleções de Linkin Park, antigas e novas, para `Downloads\LinkinPark`,
fora da biblioteca escaneada. Depois compara as músicas prontas com **sua pasta
Songs atual** e gera `Novas-musicas.zip` com as ausentes, preservando as escolhas
instaladas. Mantenha a biblioteca e os downloads em pastas separadas.

**Ajuste `$biblioteca` se o Clone Hero usa outro caminho.** O padrão localiza
Documentos pelo Windows, inclusive quando redirecionado ao OneDrive. Se tiver
mais de uma raiz configurada no jogo, reúna as referências antes de instalar;
a comparação só cobre a pasta indicada e suas subpastas.

Precisa de Windows 10/11 x64 e Python 3.11+. Não exige uv, Mido, FFmpeg, login ou
permissão administrativa. São cerca de **3,68 GiB de
origens novas**; incluindo as 33 antigas, são cerca de **4,15 GiB**. Reserve
**22 GB livres** para originais, conversão,
pastas, ZIPs e a cópia final instalada. Para recuperar somente a ampliação, acrescente `--novas` ao comando
`recover_linkin_park.py`. Demos/ao vivo ficam identificados em lotes separados;
você pode conferir a lista antes de instalar.

Espere outro baixador terminar ou encerre-o com Ctrl+C. Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\LinkinPark'
    $biblioteca = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Clone Hero\Songs'
    $baixador = Join-Path $pasta 'Baixador-LinkinPark'
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json', 'pilot_01.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    $lotes = @($indice.batches)
    if ($lotes.Count -eq 0) { throw 'Nenhum lote Linkin Park no indice. Atualize e tente novamente.' }
    foreach ($lote in $lotes) {
        if ($lote.manifest -notmatch '^collection_[0-9]{2,}\.json$') { throw 'Nome de receita invalido' }
        Invoke-WebRequest -Uri "$base/$($lote.manifest)" -OutFile (Join-Path $baixador $lote.manifest) -UseBasicParsing
    }
    foreach ($arquivo in @('additions.py', 'complement.py', 'local_library.py', 'recover_linkin_park.py')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
        $esperado = $indice.addition_helpers.PSObject.Properties[$arquivo].Value
        if ($esperado -notmatch '^[a-f0-9]{64}$' -or (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $baixador $arquivo)).Hash -ne $esperado) {
            throw 'Comparador diferente do indice. Execute novamente para atualizar.'
        }
    }
    py -3 (Join-Path $baixador 'recover_linkin_park.py') --destino $pasta
    if ($LASTEXITCODE -eq 130) { throw 'Interrompido pelo teclado. Execute o mesmo bloco para retomar.' }
    $downloadsPendentes = $LASTEXITCODE -ne 0
    $saida = Join-Path $pasta ('Para-adicionar-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    py -3 (Join-Path $baixador 'additions.py') --candidatas (Join-Path $pasta 'Songs') --biblioteca $biblioteca --destino $saida
    if ($LASTEXITCODE -ne 0) { throw 'Comparacao pendente. Confira o caminho de Songs e a mensagem acima.' }
    if ($downloadsPendentes) { Write-Warning 'Ha downloads pendentes. A comparacao usou as musicas presentes; execute novamente para retomar.' }
    Invoke-Item $saida
}
```

Na pasta aberta, confira `comparacao.csv`. **Extraia a pasta `Novas-musicas` do
ZIP diretamente em `Songs`, uma única vez**, depois execute **Scan Songs**.
Use Pro Drums / Expert ou Drums / Expert conforme o lote. Não copie também os
lotes baixados: eles são as mesmas músicas que alimentaram a comparação.
Mantenha os downloads e backups fora de todas as raízes escaneadas. O comparador
não instala, apaga ou move a biblioteca.

`ja_na_biblioteca` e `repetida_candidata` ficam fora do ZIP; `revisar` também fica
fora, para conferir versões/duração ou chart idêntico com áudio diferente.
Pastas renomeadas continuam reconhecíveis. Rótulos como `(RB3 Version)` podem
ser enviados à revisão quando já existe o título sem esse rótulo.
[ADICIONAR-SEM-REPETIR.md](ADICIONAR-SEM-REPETIR.md) explica o comparador e a
execução separada depois dos downloads.

O mesmo bloco retoma pendências e reaproveita músicas verificadas, sem substituir
edições locais. Falhas de origem aparecem em `*-falhas.json`; os outros lotes
continuam e a comparação usa apenas pastas presentes. Uma nova execução gera
outro resultado datado; compare novamente depois que os downloads terminarem.
Links públicos podem mudar ou atingir cotas. Para recuperar o lote 02, que contém
Given Up, este bloco já seleciona a receita original; se ela estiver instalada,
a comparação a deixa fora do ZIP. [CONTINUACAO.md](CONTINUACAO.md) continua
disponível para recuperar os lotes completos de outras bandas.

## Alcance da busca e músicas pendentes

Foram pesquisados os catálogos de bateria CH, Phase Shift, RB3 e “all” do
RhythmVerse: **475 pacotes**, agrupados em **255 títulos/edições** da banda ou
colaborações creditadas. Pacotes alternativos do mesmo título não viram novas
músicas. Mashups de terceiros ficaram fora. Combinações de introdução com uma
música já publicada também foram excluídas para não repetir a faixa principal.

[linkin-park.csv](reports/linkin-park.csv) registra o resultado de cada edição,
incluindo fontes bloqueadas, ausência de bateria Expert utilizável e sobreposições.
Como referência adicional, [linkin-park-albuns.csv](reports/linkin-park-albuns.csv)
compara 97 faixas dos oito álbuns principais e três extras de From Zero Deluxe,
segundo os [metadados oficiais](https://linkinpark.com/music). **85 de 100
entradas** têm título/edição representado, individualmente ou em chart combinado.
Isso não comprova o mesmo master do álbum. As lacunas dessa referência são:

- Meteora — Foreword (`not_found`)
- Minutes to Midnight — What I've Done (`blocked`)
- Minutes to Midnight — In Between (`blocked`)
- A Thousand Suns — Waiting for the End (`blocked`)
- A Thousand Suns — Wisdom, Justice, and Love (`not_found`)
- A Thousand Suns — Fallout (`not_found`)
- A Thousand Suns — The Messenger (`not_found`)
- Living Things — Burn It Down (`blocked`)
- Living Things — Tinfoil (`not_found`)
- The Hunting Party — The Summoning (`not_found`)
- One More Light — Nobody Can Save Me (`not_found`)
- One More Light — Good Goodbye (feat. Pusha T) (`no_usable_drums`)
- One More Light — Sorry for Now (`not_found`)
- One More Light — One More Light (`no_usable_drums`)
- From Zero — From Zero (Intro) (`blocked`)

“Não encontrado” descreve esta busca, sem provar inexistência global. Faixas sem
bateria utilizável, fontes indisponíveis e edições incertas não foram anunciadas
como prontas. Esta curadoria não altera o relatório anterior das 744 entradas do
Qobuz; os novos lotes têm identificadores Qobuz vazios.

## Onyx e validação

As receitas anteriores e o helper do Onyx foram preservados: Windows CLI sem
argumentos RTS, logs em `Logs\Onyx`, feedback a cada 15 segundos, abertura
separada da espera e prazos de 180/900 segundos na importação/exportação.
Os arquivos `.tempos.jsonl` e a retomada após Ctrl+C continuam disponíveis.
A escolha de conversão agora usa o formato real do pacote recebido.

Notas, bateria Expert de quatro pistas, indicação Pro quando comprovada, áudio
decodificado e hashes dos arquivos/ZIPs foram conferidos na nuvem Linux.
Drums comuns não foram promovidos artificialmente a Pro Drums. Os arquivos de
música ficam fora do Git; as receitas permitem reconstruí-los no PC.
Execução nativa no Windows, sincronismo e jogabilidade dos novos charts ainda
dependem do teste no jogo; `game_verified` permanece falso.
Veja [a verificação técnica](../docs/library-linkin-park-verification.md).

## Músicas por lote


### Lote 19 — Faixas e raridades / Pro Drums

- Jay-Z & Linkin Park — Points of Authority / 99 Problems / One Step Closer
- Linkin Park — 26 Lettaz In Da Alphabet
- Linkin Park — A Light That Never Comes (ft. Steve Aoki)
- Linkin Park — A Line in the Sand
- Linkin Park — A Place for My Head
- Linkin Park — Across the Line
- Linkin Park — All For Nothing (ft. Page Hamilton)
- Linkin Park — And One
- Linkin Park — Blackout
- Linkin Park — Blackout (Acid Rain Version)
- Linkin Park — Burning in the Skies
- Linkin Park — By Myself
- Linkin Park — Casualty
- Linkin Park — Chali/Frgt/10
- Linkin Park — Cut the Bridge
- Linkin Park — Debris
- Linkin Park — Easier To Run
- Linkin Park — Empty Spaces/When They Come for Me
- Linkin Park — Final Masquerade
- Linkin Park — Forgotten
- Linkin Park — Guilty All The Same (feat. Rakim)
- Linkin Park — Halfway Right
- Linkin Park — Hands Held High
- Linkin Park — High Voltage
- Linkin Park — I'll Be Gone


### Lote 20 — Faixas e raridades / Pro Drums

- Linkin Park — In My Remains
- Linkin Park — In Pieces
- Linkin Park — Invisible
- Linkin Park — Iridescent
- Linkin Park — Keys to the Kingdom
- Linkin Park — Krwlng
- Linkin Park — Let You Fade
- Linkin Park — Lies Greed Misery
- Linkin Park — Lost
- Linkin Park — Mark the Graves
- Linkin Park — Massive
- Linkin Park — More the Victim
- Linkin Park — No More Sorrow
- Linkin Park — No Roads Left
- Linkin Park — Nobodys Listening
- Linkin Park — Not Alone
- Linkin Park — One Step Closer (RB3 Version)
- Linkin Park — Overflow
- Linkin Park — P5hng Me Awy
- Linkin Park — Pictureboard
- Linkin Park — Points Of Authority
- Linkin Park — Points Of Authority (Remixed by Jay Gordon)
- Linkin Park — Primo
- Linkin Park — Pushing Me Away
- Linkin Park — Rebellion (ft. Daron Malakian)


### Lote 21 — Faixas e raridades / Pro Drums

- Linkin Park — Resolution
- Linkin Park — Rnw@y
- Linkin Park — Roads Untraveled
- Linkin Park — Robot Boy/Jornada del Muerto
- Linkin Park — Runaway
- Linkin Park — Session
- Linkin Park — Shadow of the Day
- Linkin Park — Sharp Edges
- Linkin Park — Skin To Bone
- Linkin Park — Stained
- Linkin Park — Stick N Move
- Linkin Park — Talkin to Myself
- Linkin Park — The Little Things Give You Away
- Linkin Park — The Requiem/The Radiance
- Linkin Park — Unshatter
- Linkin Park — Until It Breaks
- Linkin Park — Until It's Gone
- Linkin Park — Up From The Bottom
- Linkin Park — Victimized
- Linkin Park — Wake
- Linkin Park — War
- Linkin Park — White Noise
- Linkin Park — With You
- Linkin Park — Wretches and Kings
- Linkin Park — Wth You


### Lote 22 — Faixas e raridades / Pro Drums

- Linkin Park, Brian Howes — What Are You Worth


### Lote 23 — Faixas e raridades / Drums comuns

- Linkin Park — Asbestos
- Linkin Park — Blackbirds
- Linkin Park — Broken Foot
- Linkin Park — Castle of Glass
- Linkin Park — Could Have Been
- Linkin Park — Cure For The Itch
- Linkin Park — Drawbar
- Linkin Park — ENTH E ND
- Linkin Park — Healing Foot
- Linkin Park — Hit The Floor
- Linkin Park — My December
- Linkin Park — Ntr_Mssion/PPr:Kut
- Linkin Park — PB N' Jellyfish
- Linkin Park — Robot Boy (Test Mix, Optional Voice Take)
- Linkin Park — So Far Away
- Linkin Park — Wesside


### Lote 24 — Demos / Pro Drums

- Linkin Park — A6 (Meteora|20 Demo)
- Linkin Park — Bang Three (What I've Done Original Demo)
- Linkin Park — Blanka (2008 Demo)
- Linkin Park — Bleed It Out Demo
- Linkin Park — Can't Hurt Me (2014 Demo)
- Linkin Park — Carousel (8-Track Demo)
- Linkin Park — Carousel (9-Track Demo)
- Linkin Park — Chance of Rain (2006 Demo)
- Linkin Park — Clarity (Minutes To Midnight Demo)
- Linkin Park — Crawling (6-Track Demo)
- Linkin Park — Crawling (8-Track Demo)
- Linkin Park — Crawling (9-Track Demo)
- Linkin Park — Cumulus (2002 Demo)
- Linkin Park — Drawing (Breaking The Habit Demo 2002)
- Linkin Park — Dust Brothers (With You Demo)
- Linkin Park — Esaul (2-Track Demo)
- Linkin Park — Esaul (A Place for My Head Demo)
- Linkin Park — Esaul (Hybrid Theory Demo)
- Linkin Park — Esaùl (A Place For My Head Demo 1999) (9-Track Demo)
- Linkin Park — Faint (Demo 2002)
- Linkin Park — Faint (Demo 2002) [Extended]
- Linkin Park — Figure.09 (2002 Demo)
- Linkin Park — Forgotten (Demo)
- Linkin Park — Frgt/10 Demo
- Linkin Park — In The End (Demo)


### Lote 25 — Demos / Pro Drums

- Linkin Park — Now I See (With You Demo)
- Linkin Park — Ominous (Meteora Demo)
- Linkin Park — Pale (Unreleased Demo 2006)
- Linkin Park — Papercut (6 Track Demo)
- Linkin Park — Part Of Me (7-Track & 8-Track Demo)
- Linkin Park — Part Of Me (9-Track Demo)
- Linkin Park — Plaster (6 Track Demo)
- Linkin Park — Plaster 2 (Figure.09 Demo)
- Linkin Park — Points Of Authority (6-Track Demo)
- Linkin Park — Points Of Authority Demo (Vertical Limit)
- Linkin Park — Pretend To Be (Unreleased Demo 2008)
- Linkin Park — Pretty Birdy (Somewhere I Belong 2002 Demo)
- Linkin Park — Primo (I'll Be Gone, Longform 2010 Demo)
- Linkin Park — Shifter (From the Inside Demo)
- Linkin Park — The Catalyst (2010 Demo)
- Linkin Park — Untitled (In The End Demo)
- Linkin Park — What We Don't Know (Unreleased Demo 2007)


### Lote 26 — Demos / Drums comuns

- Linkin Park — Asbestos (Minutes to Midnight Demo)
- Linkin Park — Attached (2003 Demo)
- Linkin Park — Blackout (Demo)
- Linkin Park — Blue (1998 Unreleased Hybrid Theory Demo)
- Linkin Park — Breaking the Habit (Original Mike 2002 Demo)
- Linkin Park — Dedicated (1999) - LPU Rarities
- Linkin Park — Dialate (Xero Demo)
- Linkin Park — Divided (2005 Demo)
- Linkin Park — Homecoming (Minutes To Midnight Demo)
- Linkin Park — Husky (Hit The Floor Demo)
- Linkin Park — Oh No (Points of Authority Demo)
- Linkin Park — Pepper (Meteora Demo)
- Linkin Park — Program (Meteora Demo)
- Linkin Park — Slip (1998 Unreleased Hybrid Theory Demo)
- Linkin Park — Soundtrack (Meteora Demo)
- Linkin Park — YO (MTM Demo) (Rhythm Version)
- X-Ecutioners — It's Goin' Down (feat. Linkin Park) (Demo)


### Lote 27 — Ao vivo / Pro Drums

- Jay-Z, Linkin Park — Points Of Authority / 99 Problems / One Step Closer (Live)
- Linkin Park — 2025 UEFA Champions League Final Kick Off Show
- Linkin Park — A Line In The Sand (Live in Beijing 2015)
- Linkin Park — Bleed It Out (Live in Munchen, Germany 2011)
- Linkin Park — By Myself (Live In Texas)
- Linkin Park — Casualty (Live)
- Linkin Park — Catalyst/Requiem Intro/Guilty All The Same (Live In Rock am Ring 2014)
- Linkin Park — Cut the Bridge (Live In Frankfurt)
- Linkin Park — Don't Stay (Live In Texas)
- Linkin Park — Don't Stay - Live In Nottingham 2003
- Linkin Park — Easier To Run (Live In Nottingham 2003)
- Linkin Park — Faint (Live In Texas)
- Linkin Park — Faint - Unshatter Film Soundtrack - Live in São Paulo
- Linkin Park — Figure.09 (Live in Texas)
- Linkin Park — From The Inside (Live In Texas)
- Linkin Park — Given Up (Third Encore Session)
- Linkin Park — Good Things Go (Live)
- Linkin Park — Guilty All The Same (Live In Fandom Awards 2014)
- Linkin Park — Heavy Is the Crown (Live)
- Linkin Park — Heavy Is the Crown - Unshatter Film Soundtrack - Live in São Paulo
- Linkin Park — In My Remains (Live In Monterrey)
- Linkin Park — Iridescent (Live from Paris, 2010)
- Linkin Park — Leave Out All The Rest [Live at Milton Keynes]
- Linkin Park — Let You Fade (Live Drums Version)
- Linkin Park — Lost In The Echo (Live In Monterrey)


### Lote 28 — Ao vivo / Pro Drums

- Linkin Park — Lying from You (Live In Texas)
- Linkin Park — New Divide (Live from Rio, 2012)
- Linkin Park — No More Sorrow (Live In New York)
- Linkin Park — One Step Closer (Live In Texas)
- Linkin Park — Over Each Other (Live)
- Linkin Park — Overflow (Live)
- Linkin Park — P5hng Me A*wy (Live in Texas)
- Linkin Park — Papercut (Live from Paris, 2010)
- Linkin Park — Papercut (Live In Texas)
- Linkin Park — Points of Authority (Live In Texas)
- Linkin Park — Points of Authority (Live)
- Linkin Park — QWERTY (Live in Tokyo, 2006)
- Linkin Park — Reading My Eyes (Live)
- Linkin Park — Runaway (Live in Texas)
- Linkin Park — Somewhere I Belong - Unshatter Film Soundtrack - Live in São Paulo
- Linkin Park — Stained (Live In Bridgestone Arena)
- Linkin Park — Step Up/Nobody's Listening/It's Goin' Down - Live
- Linkin Park — The Catalyst (Live from Paris, 2010)
- Linkin Park — The Emptiness Machine (Live)
- Linkin Park — Two Faced (Live In São Paulo)
- Linkin Park — Until It's Gone (Live From The KROQ Red Bull Sound Space)
- Linkin Park — Up From The Bottom (Live In Los Angeles)
- Linkin Park — Waiting for the End (Live from Berlin, 2010)
- Linkin Park — Waiting for the End (Live In Rio, 2012)
- Linkin Park — What I've Done (Live in Red Square 2011)


### Lote 29 — Ao vivo / Pro Drums

- Linkin Park — What I've Done - Unshatter Film Soundtrack - Live in São Paulo
- Linkin Park — Wish - Live Projekt Revolution 2004
- Linkin Park — With You (Live In Texas)
- Linkin Park / JAY-Z — Numb Encore (Live)


### Lote 30 — Ao vivo / Drums comuns

- Linkin Park — High Voltage (Live at Docklands Arena, London)
- Linkin Park — Two Faced (Live)


## Prompt para a próxima sessão

> No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
> BACKLOG.md e lessons.md; depois song-library/LINKIN-PARK.md,
> song-library/ADICIONAR-SEM-REPETIR.md e docs/library-linkin-park-verification.md.
> Continue somente a biblioteca. A ampliação acrescentou 207 charts de
> Linkin Park nos lotes 19–30, além dos 311 charts anteriores.
> Given Up permanece no lote 02; não repita as receitas antigas nem as combinações
> com faixas já publicadas. Preserve os helpers/correções do Onyx, hashes, escolhas
> anteriores e cobertura Qobuz de 744 entradas. Consulte os dois CSVs Linkin Park
> para lacunas e não repita origens bloqueadas sem evidência nova. Revise o relato
> do usuário no Windows, resultado da comparação local e Scan Songs/playtest;
> marque game_verified somente com confirmação individual. Para demora no Onyx,
> use .log/.tempos.jsonl locais. Trabalhe em branch a partir de main, rode os gates
> de docs/testing.md, revise o staged diff e conclua com commit, merge --no-ff,
> push e verificação da sincronização, preservando commits se o push falhar.
