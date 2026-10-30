# Kevin Sherwood / CoD Zombies — lote 44

As dez músicas pedidas estão juntas no **lote 44**, todas com **Pro Drums / Expert**.
O ZIP preparado tem cerca de **101 MB**. Há **seis edições com dois pedais
confirmados**; as outras quatro têm essa informação não confirmada.

Como você pediu, este download inclui as dez músicas sem filtrar o que já existe
na sua Songs. A conferência das cópias adicionadas antes do projeto fica para
depois do Scan Songs e do envio do seu relatório de repetidas.

| Música | Bumbos básicos | Extras com 2x Kick | Dois pedais |
| --- | ---: | ---: | --- |
| [Abracadavre (ft. Elena Siegman)](https://rhythmverse.co/songfile/621bf67adc7ce6.17216388) | 858 | 674 | Confirmado: 1.532 com 2x |
| [Beauty of Annihilation](https://rhythmverse.co/songfile/e0f2f58a52a4457586430ede7a4574f0) | 590 | 0 | Edição 2x do autor, já nas notas normais |
| [Lullaby for a Deadman](https://rhythmverse.co/songfile/bb2713e5e030456baccdb7121a4bbd0f) | 437 | 0 | Não confirmado |
| [The One](https://rhythmverse.co/songfile/74ba0340007c439fa68ad1d46c9dafbd) | 400 | 0 | Não confirmado |
| [Pareidolia (ft. Elena Siegman)](https://rhythmverse.co/songfile/5f79124c400510.64578110) | 1.100 | 0 | Não confirmado |
| [Coming Home (ft. Elena Siegman)](https://rhythmverse.co/songfile/63695fce7fb010.94605471) | 722 | 509 | Confirmado: 1.231 com 2x |
| [Archangel](https://rhythmverse.co/songfile/a1b4e09746104806bd765b6f79ecfeeb) | 1.494 | 1.007 | Confirmado: 2.501 com 2x |
| [I am the Well](https://rhythmverse.co/songfile/66124c4f4c1f421d89286c105bd99a63) | 1.074 | 648 | Confirmado: 1.722 com 2x |
| [Undone](https://rhythmverse.co/songfile/65c0a3960a754054985a29e729be314b) | 235 | 0 | Não confirmado |
| [Dead Again](https://drive.google.com/drive/folders/18NARgaJ-r5FwkWO5iPwNsxbuvkYRHToc) | 1.086 | 630 | Confirmado: 1.716 com 2x |

Ative **Modifiers → 2x Kick** para aparecerem os ataques da coluna “Extras”.
Beauty of Annihilation já guarda o bumbo duplo em notas normais: a edição 2x tem
27 ataques adicionais em relação à edição 1x do mesmo autor, sem remover outras
notas. O modificador não cria notas em um chart que não as contém.
Zero extras também não prova uma redução para um pedal; nas quatro faixas
marcadas como não confirmadas, a fidelidade do bumbo duplo não foi estabelecida.

“Lullaby of a Deadman” foi localizada também sob o título **“Lullaby for a
Deadman”**, com créditos a Kevin Sherwood e Elena Siegman. Coming Home aqui é a
música de Kevin Sherwood, diferente da faixa de Avenged Sevenfold no lote 04.
**115** e **Not Ready to Die** já estavam nos lotes anteriores e continuam lá.
A seleção padrão passa a **686 charts**, além da alternativa opcional de Nightmare.

## Baixar somente este lote no Windows

Precisa de **Python 3.11+**, Windows 10/11 x64 e **2 GB livres**. O baixador
reconstrói as pastas e o ZIP em `Downloads\CoD-Zombies`; depois você copia a pasta
do lote para a Songs configurada no jogo. Mantenha Downloads fora das raízes
escaneadas. O comando não precisa de uv, Mido, FFmpeg, WSL, login ou administrador.
O Onyx portátil é baixado para as três fontes Rock Band; suas correções recentes
de argumentos no Windows, limites de espera e logs persistentes foram mantidas.

Espere outro baixador terminar ou encerre-o com Ctrl+C. Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\CoD-Zombies'
    $baixador = Join-Path $pasta 'Baixador'
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    $lotes = @($indice.batches | Where-Object { $_.number -eq 44 })
    if ($lotes.Count -ne 1) { throw 'Lote 44 de CoD Zombies nao encontrado. Atualize e tente novamente.' }
    $lote = $lotes[0]
    if ($lote.manifest -ne 'collection_44.json') { throw 'Nome de receita invalido' }
    Invoke-WebRequest -Uri "$base/$($lote.manifest)" -OutFile (Join-Path $baixador $lote.manifest) -UseBasicParsing
    py -3 (Join-Path $baixador 'recover_pilot.py') --restante --lote 44 --destino $pasta
    if ($LASTEXITCODE -eq 130) { throw 'Interrompido. Execute novamente para retomar.' }
    if ($LASTEXITCODE -ne 0) { throw 'Ha musicas pendentes. Leia as mensagens e execute novamente para retomar.' }
    Invoke-Item (Join-Path $pasta 'Songs')
}
```

Na pasta aberta, copie **`MixDrumRock - Lote 44 - CoD Zombies`** uma única vez
para a Songs do Clone Hero. Você também pode extrair a pasta de dentro de `Songs`
no ZIP `MixDrumRock-lote-44.zip`; escolha uma das duas formas para instalar.
Execute **Scan Songs**, selecione **Pro Drums / Expert** e ative **2x Kick**.

Se o jogo indicar repetidas, envie o **badsongs.txt** para identificarmos as cópias.
Charts diferentes da mesma música podem não ser apontados como duplicados pelo
scanner; nesses casos, a comparação pelo título complementa o log. Preserve as
cópias antigas até a conferência e guarde backups fora de todas as raízes escaneadas.

Repita o bloco para retomar downloads interrompidos. As músicas já conferidas
são reaproveitadas; arquivos editados são preservados. Falhas ficam explícitas
em `*-falhas.json`. Logs e medições do Onyx ficam em `Logs\Onyx`.
Mantenha o áudio que acompanha cada chart. Nas conversões, os hashes locais
protegem a retomada; não se exige identidade dos identificadores Ogg entre PCs.

## Fontes e validação

Foram conferidos **55 arquivos, 24 áudios completos e 20.348 notas Expert
básicas**, além de **3.468 bumbos opcionais**. As fontes nativas preservam notas
e áudio; Abracadavre, Coming Home e Pareidolia usam o Onyx fixado no projeto.
Uma alternativa de Abracadavre estava com cota do Drive esgotada e foi substituída
por outra fonte 2x obtida. A edição 1x de Beauty foi usada apenas na comparação.
Fontes, autores e resultados estão no [relatório](reports/cod-zombies.csv).

A validação de arquivos ocorre em Linux/Python 3.12. Execução nativa no Windows,
Scan Songs, sincronismo percebido e teste com seus pedais precisam do seu resultado.
Os arquivos de música ficam fora do Git; receitas e hashes permitem recuperá-los
no PC. A disponibilidade dos links públicos pode mudar.

## Próxima sessão

```text
No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
BACKLOG.md, lessons.md e .agents/skills/drum-audio-diagnostics/SKILL.md.
Leia song-library/COD-ZOMBIES.md e song-library/CONTINUACAO.md. O lote 44 contém
os dez títulos Kevin Sherwood / CoD Zombies pedidos, todos Pro Drums / Expert;
seis edições têm 2x confirmado. Por pedido do usuário, a comparação com músicas
instaladas antes do projeto foi adiada até o envio do badsongs.txt. Analise o log
sem publicar caminhos pessoais e preserve os arquivos até identificar as cópias.
Charts diferentes da mesma música podem precisar de comparação por título.
Mantenha receitas anteriores, correções Onyx, Nightmare opcional e estudos de
áudio. Priorize dois pedais sem inventar notas; ative Modifiers > 2x Kick nas
cinco faixas com extras. Consulte BACKLOG.md DCF-LIB-019 e não declare aceitação
no Windows/jogo sem o teste do usuário.
```
