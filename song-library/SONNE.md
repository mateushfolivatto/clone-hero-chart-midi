# Sonne — Rammstein para Clone Hero

Foi preparado **um chart de Sonne, do Rammstein, no lote 43**, para
**Pro Drums / Expert**. A seleção padrão agora contém 676 charts; os 675
anteriores e a alternativa opcional de Nightmare permanecem intactos.

A [publicação escolhida](https://rhythmverse.co/songfile/fb2e16c957934a20b716c9f651b41dc7)
é a revisão com bateria alternativa, ajustes de sincronismo e áudio MT creditada
a beard216, Mastergox, Furiouss, Imitable e GeeForce11. Esses ajustes são descritos
pelo autor; não foi medido melhor sincronismo no jogo. O arquivo convertido tem
**1.294 notas Expert, 464 bumbos e 82 marcadores de tom**; seis áudios foram
decodificados e o pacote foi reconstruído com o Onyx da versão já usada no projeto.

## Dois pedais

A preferência por dois pedais foi aplicada à busca. **Não foi obtida uma versão
de estúdio com 2x Kick confirmado.** As duas fontes inspecionadas não têm notas
extras MIDI 95 nem trilha PART DRUMS_2X, também antes da exportação pelo Onyx.
A outra fonte de estúdio não pôde ser preparada. Isso não prova que os bumbos
normais representam uma redução para um pedal; a fidelidade do bumbo duplo não
foi medida. A ausência de confirmação fica explícita na receita e no
[relatório das cinco opções](reports/sonne.csv).

O modificador 2x Kick habilita notas extras já chartadas; ele não inventa bumbos
num chart sem essas notas. Versões ao vivo ficaram fora deste pedido de estúdio.
Não alteramos áudio, tempos ou notas manualmente para anunciar suporte 2x.

## Baixar e adicionar sem repetir

**Ajuste `$biblioteca` para a Songs realmente configurada no seu Clone Hero.**
O comando baixa só o lote 43 em Downloads, compara com sua biblioteca e cria
um ZIP contendo somente músicas ausentes. Não instala nem modifica sua
Songs automaticamente. Precisa de Python 3.11+ em Windows 10/11 x64 e
**2 GB livres**. O original tem cerca de 33 MB; o Onyx portátil, 63 MB.
Não precisa de uv, Mido, FFmpeg, WSL, login ou permissões administrativas.

Espere outro baixador terminar ou encerre-o com Ctrl+C. Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\Sonne'
    $biblioteca = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Clone Hero\Songs'
    $baixador = Join-Path $pasta 'Baixador'
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    $lotes = @($indice.batches | Where-Object { $_.number -eq 43 })
    if ($lotes.Count -eq 0) { throw 'Lote 43 de Sonne nao encontrado. Atualize e tente novamente.' }
    foreach ($lote in $lotes) {
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
    $downloadsPendentes = $false
    foreach ($lote in $lotes) {
        py -3 (Join-Path $baixador 'recover_pilot.py') --restante --lote $lote.number --destino $pasta
        if ($LASTEXITCODE -eq 130) { throw 'Interrompido. Execute novamente para retomar.' }
        if ($LASTEXITCODE -ne 0) { $downloadsPendentes = $true }
    }
    $saida = Join-Path $pasta ('Para-adicionar-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    py -3 (Join-Path $baixador 'additions.py') --candidatas (Join-Path $pasta 'Songs') --biblioteca $biblioteca --destino $saida
    if ($LASTEXITCODE -ne 0) { throw 'Comparacao pendente. Confira o caminho de Songs e a mensagem acima.' }
    if ($downloadsPendentes) { Write-Warning 'Ha downloads pendentes. Execute novamente para retomar e comparar as novas pastas prontas.' }
    Invoke-Item $saida
}
```

Na pasta aberta, confira `comparacao.csv`. Extraia **Novas-musicas** do ZIP na
Songs uma única vez, execute **Scan Songs** e escolha **Pro Drums / Expert**.
Se o relatório marcar `ja_na_biblioteca`, não precisa instalar outra cópia.
Não copie também o lote baixado: ele contém a mesma música usada na comparação.
Mantenha Downloads e backups fora de todas as raízes escaneadas. Pastas renomeadas
são reconhecidas por metadados e conteúdo; casos incertos ficam em revisão.

As correções do Onyx foram preservadas: Windows sem RTS, logs persistentes em
`Logs\Onyx`, mensagens de espera e retomada com o mesmo comando. O original e
a identidade do MIDI são fixados por hash; cada conversão registra hashes locais
dos áudios para preservar arquivos e edições na retomada. Mantenha notas e áudio
desta edição juntos. Veja [CONTINUACAO.md](CONTINUACAO.md) para os detalhes do Onyx.

A validação ocorreu em Linux/Python 3.12. A execução nativa no Windows, Scan Songs,
sincronismo percebido e teste com seus pedais ainda precisam do seu resultado.
As fontes públicas podem mudar ou atingir cotas; uma falha é registrada para
retomada, sem substituir arquivos existentes. Nenhuma mídia é versionada no Git.

## Próxima sessão

```text
No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
BACKLOG.md, lessons.md e .agents/skills/drum-audio-diagnostics/SKILL.md.
Leia song-library/SONNE.md e song-library/CONTINUACAO.md. Sonne, do Rammstein,
foi adicionada no lote 43 como Pro Drums / Expert, com 464 bumbos e zero notas
opcionais 2x nas fontes inspecionadas. Dois pedais continuam sendo prioridade,
mas essa edição não tem 2x confirmado. Não invente bumbos ou misture notas/áudio;
preserve receitas anteriores, Nightmare opcional, correções Onyx e estudos de áudio.
Compare novos downloads com a Songs real e peça o teste no jogo antes de afirmar
aceitação ou sincronismo. Consulte BACKLOG.md DCF-LIB-018 para o estado da preparação.
```
