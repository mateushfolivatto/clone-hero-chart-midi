# Skillet, Imagine Dragons e League of Legends

Acrescentados **137 charts de bateria em 10 lotes (31–40)**:
71 Pro Drums e 66 Drums comuns, todos em Expert.
São todas as seleções obtidas e validadas nesta busca; há lacunas de disponibilidade.
Edições ao vivo contam separadamente. Isso não comprova a discografia integral.

| Seleção | Charts novos | Total incluindo os anteriores |
| --- | ---: | ---: |
| Skillet | 133 | 143 |
| Imagine Dragons | 2 | 16 |
| League of Legends | 2 | 16 |

Os grupos podem compartilhar uma música: “Enemy” é Imagine Dragons e LoL, mas
é recuperada uma única vez. A união tem **174 charts**.
As receitas anteriores, as escolhas já publicadas e as correções do Onyx continuam
preservadas. A coleção completa agora tem 655 charts;
a cobertura das 744 entradas do Qobuz permanece como antes.

## Baixar e adicionar sem repetir

O bloco abaixo baixa as três seleções, incluindo faixas antigas que possam estar
faltando, para Downloads. Depois compara com sua biblioteca atual e gera
`Novas-musicas.zip` somente com as músicas ausentes. Não instala automaticamente.

**Ajuste `$biblioteca` para a pasta Songs realmente configurada no jogo.**
O padrão usa Documentos do Windows, inclusive com redirecionamento. Se houver
várias raízes escaneadas, a comparação deve incluir todas as músicas instaladas.
Mantenha Downloads e backups fora de todas essas raízes.

Requer Windows 10/11 x64 e Python 3.11+. Não exige uv, FFmpeg, Mido, login,
WSL ou permissões administrativas. Reserve **14 GB livres** para a união:
fontes, conversão temporária, pastas, ZIPs e a cópia instalada.
Os leitores portáteis 7-Zip/Onyx têm versões e hashes fixos; o instalador 7-Zip
é lido como arquivo. SNG é extraído pelo próprio Python, sem instalar programas.

Espere outro baixador terminar ou encerre-o com Ctrl+C. Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\Skillet-Imagine-LoL'
    $biblioteca = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Clone Hero\Songs'
    $baixador = Join-Path $pasta 'Baixador'
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json', 'pilot_01.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    foreach ($lote in $indice.batches) {
        if ($lote.manifest -notmatch '^collection_[0-9]{2,}\.json$') { throw 'Nome de receita invalido' }
        Invoke-WebRequest -Uri "$base/$($lote.manifest)" -OutFile (Join-Path $baixador $lote.manifest) -UseBasicParsing
    }
    foreach ($arquivo in @('additions.py', 'complement.py', 'local_library.py')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
        $esperado = $indice.addition_helpers.PSObject.Properties[$arquivo].Value
        if ($esperado -notmatch '^[a-f0-9]{64}$' -or (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $baixador $arquivo)).Hash -ne $esperado) {
            throw 'Comparador diferente do indice. Execute novamente para atualizar.'
        }
    }
    $selecao = $indice.selections.'skillet-imagine-lol'
    if (-not $selecao) { throw 'Indice sem esta selecao. Atualize o baixador.' }
    if ($selecao.manifest -ne 'selection_skillet_imagine_lol.json' -or $selecao.helper -ne 'recover_selections.py') { throw 'Nome de selecao invalido' }
    foreach ($arquivo in @('selection_skillet_imagine_lol.json', 'recover_selections.py')) {
        $esperado = if ($arquivo -eq $selecao.manifest) { $selecao.sha256 } else { $selecao.helper_sha256 }
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
        if ($esperado -notmatch '^[a-f0-9]{64}$' -or (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $baixador $arquivo)).Hash -ne $esperado) {
            throw 'Selecao diferente do indice. Execute novamente para atualizar.'
        }
    }
    py -3 (Join-Path $baixador 'recover_selections.py') --destino $pasta
    if ($LASTEXITCODE -eq 130) { throw 'Interrompido. Execute o mesmo bloco para retomar.' }
    $downloadsPendentes = $LASTEXITCODE -ne 0
    $saida = Join-Path $pasta ('Para-adicionar-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    py -3 (Join-Path $baixador 'additions.py') --candidatas (Join-Path $pasta 'Songs') --biblioteca $biblioteca --destino $saida
    if ($LASTEXITCODE -ne 0) { throw 'Comparacao pendente. Confira o caminho de Songs e a mensagem acima.' }
    if ($downloadsPendentes) { Write-Warning 'Ha downloads pendentes. A comparacao usou as musicas presentes; execute novamente para retomar.' }
    Invoke-Item $saida
}
```

Na pasta aberta, confira `comparacao.csv`. **Extraia a pasta `Novas-musicas` do
ZIP diretamente em Songs uma única vez** e execute **Scan Songs**. Escolha
Pro Drums / Expert ou Drums / Expert conforme o lote. Não copie também os lotes
de Downloads: essas são as mesmas músicas usadas pela comparação.

Músicas reconhecidas e repetições entre candidatas ficam fora do ZIP. Versões
incertas ou o mesmo chart com áudio diferente ficam em `revisar`. O comparador
preserva os arquivos de entrada e reconhece pastas renomeadas.
Veja [ADICIONAR-SEM-REPETIR.md](ADICIONAR-SEM-REPETIR.md).

Para escolher só uma seleção, acrescente `--grupos skillet`, `--grupos imagine`
ou `--grupos lol` à linha de `recover_selections.py`. Pode combinar nomes.
Para baixar apenas os lotes novos, acrescente `--novas` nessa mesma linha.
Use uma pasta `$pasta` diferente para uma seleção menor se já tiver baixado as
três: a comparação lê todas as pastas prontas presentes naquele destino.

Repita o bloco para retomar downloads pendentes. Ele verifica fontes, receitas
e arquivos existentes e recusa substituir edições locais. Interromper com Ctrl+C
não passa para a faixa seguinte; sai com instruções de retomada. Falhas de origem
ficam em `*-falhas.json` e não impedem tentar os outros lotes. A comparação usa
somente músicas presentes; compare novamente depois que os downloads terminarem.

## Alcance e pendências

A pesquisa percorreu os catálogos de bateria do RhythmVerse (CH, Phase Shift,
RB3 e all), sondou pacotes nativos de Skillet e Imagine Dragons sem filtro de instrumento e consultou
o catálogo público Encore com bateria Expert. Metadados de catálogo não bastam:
cada seleção pronta tem notas Expert de quatro pistas, bumbo, áudio decodificado
e fontes/arquivos conferidos por SHA256. Pro exige evidência no pacote.

LoL inclui projetos oficiais como Pentakill, K/DA e temas de Worlds, além de
Arcane. Participações, versões ao vivo e covers encontrados ficam identificados;
artistas ou músicas de mesmo nome sem essa ligação foram excluídos.
[skillet-imagine-lol.csv](reports/skillet-imagine-lol.csv) registra as edições
pesquisadas, as anteriores e os bloqueios. A
[referência de títulos](reports/skillet-imagine-lol-referencias.csv) mantém também
buscas sem correspondência, incluindo sucessos conhecidos e temas de LoL.
“Não encontrado” descreve estes catálogos e filtros, sem provar inexistência global.
Links públicos podem ser removidos, mudar ou atingir cotas.

Os pacotes nativos conservam notas e áudio. SNG guarda metadados no cabeçalho:
o leitor gera song.ini de forma determinística e restaura os outros arquivos
sem recodificar. Tags de cor no título são ignoradas na comparação com o catálogo,
mas permanecem no arquivo original; rótulos de gravação continuam distintos.
Drums comuns não foram promovidos artificialmente a Pro.

Onyx mantém Windows CLI sem RTS, logs persistentes em Logs/Onyx, feedback de
espera a cada 15 s, abertura separada da espera e prazos de 180/900 s. As receitas
do piloto e dos lotes 02–30, helpers anteriores e resultados dos experimentos de
áudio permaneceram intactos. Músicas e modelos não entram no Git.

Esta é validação de arquivos na nuvem Linux. Execução nativa no Windows,
sincronismo percebido e jogabilidade ainda dependem do teste de cada chart;
`game_verified` permanece falso. Veja a
[verificação técnica](../docs/library-skillet-imagine-lol-verification.md).

## Músicas por lote

### Lote 31 — Skillet — Pro Drums / Expert

- Skillet — A Little More
- Skillet — Alien Youth
- Skillet — American Noise
- Skillet — Anchor
- Skillet — Back From The Dead
- Skillet — Back To Life
- Skillet — Battle Cry
- Skillet — Believe
- Skillet — Better Than Drugs
- Skillet — Beyond Incredible
- Skillet — Burn It Down
- Skillet — Circus For A Psycho
- Skillet — Collide
- Skillet — Cycle Down
- Skillet — Dead Inside
- Skillet — Don't Wake me
- Skillet — Energy
- Skillet — Everything Goes Black
- Skillet — Falling Inside The Black
- Skillet — Fingernails
- Skillet — Fire And Fury
- Skillet — Forgiven
- Skillet — Forsaken
- Skillet — Freakshow
- Skillet — Good To Be Alive

### Lote 32 — Skillet — Pro Drums / Expert

- Skillet — Hard To Find
- Skillet — I Want To Live
- Skillet — Imperfection
- Skillet — It's Not Me, It's You
- Skillet — Last Day Of Summer
- Skillet — Legendary
- Skillet — Live Free Or Let Me Die
- Skillet — Looking For Angels
- Skillet — Lucy
- Skillet — Madness In Me
- Skillet — Monster
- Skillet — My Obsession
- Skillet — My Religion
- Skillet — Never Surrender
- Skillet — Not Afraid
- Skillet — O Come, O Come Emmanuel
- Skillet — One Day Too Late
- Skillet — Open Wounds
- Skillet — Out Of Hell
- Skillet — Psycho In My Head
- Skillet — Reach
- Skillet — Rebirthing
- Skillet — Salvation
- Skillet — Save Me
- Skillet — Savior

### Lote 33 — Skillet — Pro Drums / Expert

- Skillet — Say Goodbye
- Skillet — Scream
- Skillet — Should've When You Could've
- Skillet — Sometimes
- Skillet — Stand
- Skillet — Stars
- Skillet — Surviving The Game
- Skillet — The Older I Get
- Skillet — Those Nights
- Skillet — Under My Skin
- Skillet — Unpopular
- Skillet — Victorious
- Skillet — What I Believe
- Skillet — Would It Matter
- Skillet — You Ain't Ready
- Skillet — Yours To Hold

### Lote 34 — Skillet — Drums comuns / Expert

- Skillet — Always The Same
- Skillet — Angels Fall Down
- Skillet — Best Kept Secret
- Skillet — Boundaries
- Skillet — Come on to The Future
- Skillet — Coming Down
- Skillet — Deeper
- Skillet — Dive Over In
- Skillet — Each Other
- Skillet — Earth Invasion
- Skillet — Eating Me Away
- Skillet — Gasoline
- Skillet — Heaven In My Veins
- Skillet — Hey You, I Love Your Soul
- Skillet — How Deep the Father's Love for Us
- Skillet — I Can
- Skillet — Jesus Be Glorified
- Skillet — Jesus, Jesus (Holy and Anointed One)
- Skillet — Kill Me Heal Me
- Skillet — Locked In A Cage
- Skillet — More Faithful
- Skillet — My Beautiful Robe
- Skillet — One Real Thing
- Skillet — Paint
- Skillet — Podcast Song

### Lote 35 — Skillet — Drums comuns / Expert

- Skillet — Pour
- Skillet — Promise Blender
- Skillet — Rest
- Skillet — Rippin' Me Off
- Skillet — Safe With You
- Skillet — Saturn
- Skillet — Scarecrow
- Skillet — Shout To The Lord
- Skillet — Sing To The Lord
- Skillet — Splinter
- Skillet — Stronger
- Skillet — Suspended In You
- Skillet — Take
- Skillet — The Fire Breathes
- Skillet — The One
- Skillet — The Thirst Is Taking Over
- Skillet — Vapor
- Skillet — Whirlwind
- Skillet — Who Is Like Our God
- Skillet — Will You Be There? (Falling Down)
- Skillet — You Are My Hope
- Skillet — You Take My Rights Away
- Skillet — You Thought
- Skillet — You're In My Brain
- Skillet — You're Powerful

### Lote 36 — Skillet — Drums comuns / Expert

- Skillet — Your Love (Keeps Me Alive)
- Skillet — Your Name Is Holy

### Lote 37 — Skillet — Pro Drums / Expert

- Skillet — The Last Night (iTunes Session)

### Lote 38 — Skillet — Drums comuns / Expert

- Skillet — Angels Fall Down (Live)
- Skillet — Best Kept Secret (Live)
- Skillet — Better Than Drugs (Live)
- Skillet — Collide (Live)
- Skillet — Comatose (Live)
- Skillet — Forsaken (Live)
- Skillet — My Obsession (Live)
- Skillet — Rebirthing (Live)
- Skillet — Savior (Live)
- Skillet — The Last Night (Live)
- Skillet — The Older I Get (Live)
- Skillet — Those Nights (Live)
- Skillet — Whispers in the Dark (Live)
- Skillet — Yours To Hold (Live)

### Lote 39 — Imagine Dragons — Pro Drums / Expert

- Imagine Dragons — I Bet My Life
- Imagine Dragons — Take Me To The Beach (feat. Ado)

### Lote 40 — League of Legends — Pro Drums / Expert

- Mike Shinoda — Heavy Is the Crown (Original Score) (from the series Arcane League of Legends) (feat. Emily Armstrong)
- Stromae, Pomme — Ma Meilleure Ennemie

## Próxima sessão

```text
No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
BACKLOG.md e lessons.md. Leia song-library/CONTINUACAO.md,
song-library/SKILLET-IMAGINE-LOL.md e docs/library-skillet-imagine-lol-verification.md.
Aplique a skill local drum-audio-diagnostics quando trabalhar com música/chart.
Continue somente DCF-LIB-015 a partir de um erro ou resultado concreto do usuário:
recuperação seletiva Windows, Scan Songs e teste individual. Preserve todas as
receitas publicadas, escolhas Pro/Drums, Onyx/7-Zip/MEGA, comparador local e
experimentos/perfil de áudio. Não republique músicas, não confunda disponibilidade
com discografia completa e não coloque mídia/modelos/logs privados no Git.
Se investigar uma pendência de catálogo, confirme o pacote real antes de anexar
outro lote e compare com toda a coleção. Crie branch, valide, documente, commit,
merge --no-ff em main, push e verifique origin/main conforme AGENTS.md.
```
