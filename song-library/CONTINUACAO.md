# Baixar a continuação da MixDrumRock

**Linkin Park:** [LINKIN-PARK.md](LINKIN-PARK.md) traz 207 charts novos nos
lotes 19–30 e a recuperação seletiva da banda, incluindo Given Up já no
lote 02. O fluxo compara com sua biblioteca atual antes de gerar o ZIP a instalar.
As receitas anteriores e correções do Onyx foram preservadas.

**Novos lotes temáticos 13–18:** [TEMATICOS.md](TEMATICOS.md) traz 45 charts
adicionais de League of Legends, Imagine Dragons e bandas semelhantes a Linkin Park,
sem repetir o piloto/lotes 02–12. Use o bloco dessa página para baixar somente
os novos lotes. O comando geral abaixo agora percorre todos os lotes 02–30 e
reaproveita os já conferidos. As receitas antigas e correções do Onyx foram mantidas.

Os números a seguir descrevem a preparação anterior da playlist Qobuz:

Foram preparados **254 charts novos em 11 lotes**: 246 Pro Drums nos lotes 02–11
e oito Drums comuns no lote 12. O piloto de 12 músicas permanece separado.
A playlist atual tem 744 entradas; as repetições compartilham um chart quando
cabível. Com o piloto, 275 entradas estão cobertas. As outras 469 estão no relatório:
358 sem correspondência conservadora, 50 versões para revisar e 61 bloqueios de
acesso/preparação. Isso não representa disponibilidade integral da playlist.

Os downloads originais somam aproximadamente **3,7 GiB**. Reserve pelo menos
**13 GB livres** para originais, pastas, ZIPs e conversão temporária. Os ZIPs finais
somam aproximadamente 3,1 GiB. Alguns originais incluem vídeo/arquivos extras que
ficam fora das pastas entregues ao jogo.

Para executar o comando geral com **todos os lotes 02–30**, incluindo a curadoria
temática, reserve **25 GB livres**. Para somente os lotes 13–18, TEMATICOS.md
oferece o comando seletivo e recomenda 4 GB livres.

Use a mesma pasta do piloto. As novas músicas ficam em `Songs\MixDrumRock - Lote XX`,
com até 25 charts por lote. O piloto permanece na pasta dele. Cada lote também gera
um ZIP com pastas extraídas, lista de músicas, fontes, autores e verificações.

Este comando precisa de Python 3.11 ou mais recente e Windows 10/11 x64. Não exige
uv, Mido, FFmpeg, login no Qobuz/Drive nem permissões administrativas. Para RAR/7z,
baixa um leitor portátil oficial de 7-Zip; para pacotes Rock Band, baixa a versão
portátil oficial do Onyx (~60 MiB). As versões e os SHA256 são fixos. O instalador
do 7-Zip é lido como arquivo compactado; ele não é executado.

Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\MixDrumRock'
    $baixador = Join-Path $pasta 'Baixador'
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'sevenzip.py', 'mega_recovery.py', 'collection_index.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    $indice = Get-Content -LiteralPath (Join-Path $baixador 'collection_index.json') -Raw | ConvertFrom-Json
    foreach ($lote in $indice.batches) {
        if ($lote.manifest -notmatch '^collection_[0-9]{2,}\.json$') { throw 'Nome de lote invalido' }
        Invoke-WebRequest -Uri "$base/$($lote.manifest)" -OutFile (Join-Path $baixador $lote.manifest) -UseBasicParsing
    }
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/song-library/reports/cobertura.csv' -OutFile (Join-Path $pasta 'cobertura.csv') -UseBasicParsing
    py -3 (Join-Path $baixador 'recover_pilot.py') --restante --destino $pasta
    if ($LASTEXITCODE -ne 0) { throw 'Algumas musicas ficaram pendentes. Leia as mensagens e execute novamente para retomar.' }
}
```

O comando confere o índice, cada receita, os programas auxiliares e os pacotes de
origem. Reaproveita músicas conferidas e recusa sobrescrever músicas alteradas.
Uma falha de download não impede tentar as outras faixas: o programa registra
`*-falhas.json`, gera um ZIP parcial quando possível e continua os outros lotes.
Execute o mesmo bloco para retomar. As pastas já prontas em `Songs` podem ser usadas.

## Se o Onyx parou na importação

O baixador anterior passava `+RTS -N2 -RTS` ao Onyx do Windows. A versão portátil
de linha de comando usada aqui é compilada sem suporte a essa opção de paralelismo.
Isso foi corrigido em 2026-10-17. O log enviado pelo usuário mostra o lote 08;
as conversões Onyx começam nesse lote e também aparecem nos lotes 09–12.

Espere a execução anterior terminar ou interrompa com **Ctrl+C** antes de atualizar.
Se já executou o bloco acima, basta atualizar estes três arquivos e retomar:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\MixDrumRock'
    $baixador = Join-Path $pasta 'Baixador'
    foreach ($arquivo in @('recover_pilot.py', 'onyx_recovery.py', 'collection_index.json')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $baixador $arquivo) -UseBasicParsing
    }
    py -3 (Join-Path $baixador 'recover_pilot.py') --restante --destino $pasta
    if ($LASTEXITCODE -ne 0) { throw 'Ainda ha pendencias. Confira as mensagens e os logs indicados.' }
}
```

Mantenha `Originais`, `Songs`, `Verificacoes` e os ZIPs existentes: o programa
confere e reaproveita esses arquivos. As receitas de músicas não mudaram.
Agora cada tentativa do Onyx deixa um log em `Downloads\MixDrumRock\Logs\Onyx`,
mesmo se a conversão falhar. A mensagem mostra a etapa e o motivo do conversor.
Um timeout de download, como o de Octavarium no texto recebido, é uma pendência
separada: a retomada tenta baixar essa origem novamente.

## Escolher lote e usar no jogo

### Durante as conversões do Onyx

O baixador informa se está na importação ou exportação, mostra o PID e o caminho
do log e imprime o tempo de espera a cada 15 segundos. Isso indica espera pelo
processo; não é porcentagem nem comprovação de avanço interno do conversor.
O tempo de **abertura do executável** aparece separado da **espera pelo processo**.
Os limites da espera, após a criação do processo, são **180 segundos na importação**
e **900 segundos na exportação**, por música. O supervisor verifica o prazo em
intervalos de no máximo meio segundo, encerra e recolhe o próprio processo ao
esgotá-lo e registra a pendência para continuar com outras músicas.

Foi corrigido um defeito na atualização anterior: o contador começava antes da
saída inicial e só terminava depois de aguardar a thread de mensagens. Um atraso
de saída podia inflar o tempo mostrado, mesmo com o conversor rápido. Isso foi
reproduzido em teste; não determina a causa específica dos 731 s reportados em Stain.
O usuário informou que não selecionou texto nem suspendeu o computador.
Agora a supervisão não espera indefinidamente a thread do console e a medição é
capturada antes dessa espera. Uma conclusão observada após o prazo não é anunciada
como sucesso dentro dele.

Cada log recebe um arquivo vizinho **`.tempos.jsonl`**, com início de abertura,
processo criado, PID, duração de abertura/espera/limpeza e resultado. Se voltar a
demorar, envie somente esse arquivo pequeno e o `.log` correspondente. O Windows
pode demorar para criar um processo: essa chamada do sistema não é cancelável
pelo timeout de espera do Python. Por isso o tempo de abertura é registrado
separadamente; não há promessa de um limite total enquanto o sistema está bloqueado.

**Ctrl+C encerra a execução; não serve para passar à próxima música.** A nova
mensagem de interrupção informa como retomar, sem traceback. As músicas prontas,
ZIPs e downloads concluídos são reaproveitados pelo mesmo comando. Para atualizar,
use o bloco de três arquivos em “Se o Onyx parou na importação”, acima.

No PowerShell clássico, se houver seleção de texto ativa (modo Marcar/Selecionar),
use **Esc** para sair desse modo. A seleção pode pausar a saída do console.
Isso é uma verificação possível, não a causa confirmada do relato.

O relato de 2026-10-18 mostra o lote 09 concluído e as sete primeiras músicas do
lote 10 conferidas, seguido de interrupção por teclado durante a importação de
Endless, Nameless. A mesma fonte importou em 1,35 s no Linux; esse tempo não prevê
o desempenho no Windows. O log local da música ainda é necessário para investigar
a demora. O usuário esclareceu que interrompeu essa importação antes de três
minutos; esse traceback não prova que o prazo venceu ou que o conversor falhou.
A música anterior esperou cerca de três minutos, sem etapa informada.
Para ler o log do caminho informado pelo usuário, em uma linha:

```powershell
Get-Content -Path 'C:\Users\mateus\Downloads\MixDrumRock\Logs\Onyx\60ef8143a26301.37936371-*.log' -Tail 40
```

Se já tem músicas antigas, use [SEM-REPETIDAS.md](SEM-REPETIDAS.md) para gerar
um complemento local, reconhecendo pastas renomeadas sem enviar áudios/ZIPs.
Monte a biblioteca nova a partir dos lotes e desse complemento.

Para executar apenas um lote, acrescente `--lote 2` ao comando `py -3 ...`.
Para mudar o destino, altere somente `$pasta`. Prefira um caminho curto se o
Windows avisar sobre nomes/caminhos longos.

Copie as pastas `MixDrumRock - Lote XX` de dentro de `Songs` para a biblioteca do
Clone Hero, execute **Scan Songs** e escolha **Pro Drums / Expert** nos lotes 02–11.
No lote 12, cuja pasta contém `Drums`, escolha **Drums / Expert**: Pro Drums não
foi comprovado nessas oito faixas. A configuração não foi forçada para alegar Pro Drums.

Mantenha o áudio que acompanha cada chart. Os charts nativos mantêm áudio e notas originais;
alguns recebem somente `pro_drums=True`, com base nos marcadores existentes.
Conversões de Rock Band são feitas pelo Onyx, com MIDI conferido contra o que foi
inspecionado na nuvem. Ogg usa identificadores variáveis: os áudios convertidos
ganham hashes locais em `Verificacoes` para permitir retomada e preservar edições.

O relatório [cobertura.csv](reports/cobertura.csv) mantém a ordem completa da
playlist e indica lote, fonte e pendências de cada entrada. Entradas repetidas
que usam o mesmo chart compartilham uma pasta. `not_found` significa ausência de
correspondência conservadora nos catálogos CH/Phase Shift/RB3 pesquisados, não
prova que uma chart jamais existiu. Versões incertas, links inacessíveis e formatos
sem conversão validada ficam pendentes. Novas músicas não foram testadas no jogo;
validação de arquivos não comprova sincronismo percebido nem qualidade musical.

Os arquivos de música não entram no GitHub. O que fica versionado são o baixador,
receitas e relatórios de metadados, permitindo reconstruir a coleção no seu PC.
Os links originais ainda podem mudar, ser removidos ou atingir limites do provedor;
nesse caso a falha fica explícita e os demais arquivos são preservados.
