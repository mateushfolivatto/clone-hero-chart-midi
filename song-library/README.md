# Biblioteca de músicas — MixDrumRock

**The Strokes:** [THE-STROKES.md](THE-STROKES.md) traz 20 destaques nos lotes
41–42, com 18 Pro Drums, dois Drums comuns e comparação com Songs para adicionar
somente as músicas ausentes. A página inclui referências para ouvir e pendências.

**Skillet, Imagine Dragons e LoL:** [SKILLET-IMAGINE-LOL.md](SKILLET-IMAGINE-LOL.md)
traz 137 charts novos nos lotes 31–40, recuperação por grupo e comparação com a
biblioteca instalada para acrescentar somente músicas ausentes. Há listas e
pendências explícitas; a busca não comprova a discografia integral.

**Linkin Park:** [LINKIN-PARK.md](LINKIN-PARK.md) reúne a ampliação, as listas por
lote e a comparação com sua biblioteca para acrescentar somente músicas ausentes.
Given Up já está no lote 02. O relatório por álbum distingue seleção e lacunas.

**45 charts novos nos lotes 13–18:** [TEMATICOS.md](TEMATICOS.md), com League of
Legends, Imagine Dragons e sete bandas próximas de Linkin Park. A curadoria
temática tem recuperação seletiva e não altera a cobertura da playlist Qobuz.

**Para recuperar os 254 charts dos lotes 02–12, veja [CONTINUACAO.md](CONTINUACAO.md).** Para
recuperar somente o piloto de 12, use [BAIXAR.md](BAIXAR.md). O baixador e
a receita estão no GitHub; a pasta `data` é gerada localmente e não é versionada.
Links de arquivos da máquina da nuvem não garantem disponibilidade após retomadas.

**Para juntar sua coleção antiga aos lotes, use [SEM-REPETIDAS.md](SEM-REPETIDAS.md).**
O comparador roda no PC, reconhece pastas renomeadas por metadados/conteúdo e cria
um ZIP só do complemento, preservando os originais. Nenhum upload de mídia é necessário.

Área separada para organizar a playlist do Qobuz e preparar charts já existentes
para tocar bateria no Clone Hero. A coleção pode crescer além de 600 músicas;
o processamento futuro deve ser incremental e preservar escolhas anteriores.
O pipeline de MP3 → transcrição do Drum Chart Forge continua independente.

O exportador de metadados do Qobuz já está implementado em
`src/drumforge/library/qobuz.py`. A MixDrumRock foi exportada com 681 faixas,
preservando ordem, versões e identificadores, em CSV, Excel e um snapshot JSON.
O snapshot atualizado de 2026-10-17 contém **744 entradas**. A busca/preparação em
lotes está implementada e acrescentou **254 charts**: 246 Pro Drums e oito Drums
comuns, em 11 lotes separados do piloto. São 266 charts incluindo as 12 originais,
cobrindo 275 entradas da playlist. As outras 469 têm motivos registrados no
[CSV completo](reports/cobertura.csv): 358 sem correspondência conservadora,
50 versões incertas e 61 casos bloqueados. Não há promessa de cobertura integral.

As receitas duráveis `src/drumforge/library/collection_02.json` até `collection_12.json`
guardam fontes, autores, hashes e IDs do Qobuz. O índice e o baixador conferem a
identidade dessas receitas; novas atualizações acrescentam lotes sem reescrever
os anteriores. Os ZIPs atuais ficam em
`/workspace/shared/downloads/MixDrumRock-continuacao/`, mas o caminho durável de
entrega é o comando para Windows em CONTINUACAO.md. Os novos charts ainda precisam
de Scan Songs/playtest. O usuário confirmou que conseguiu receber o piloto.

## Lote de teste 01 — 12 músicas

O primeiro arquivo foi criado em `data/mixdrumrock/exports/MixDrumRock-piloto-12.zip`
(138,6 MiB). Ele não sobreviveu à retomada da máquina. O lote foi recuperado em
2026-10-17 e a cópia atual está em
`/workspace/shared/downloads/MixDrumRock-piloto-12.zip`.
Para obter uma cópia durável no PC, siga [BAIXAR.md](BAIXAR.md).
Ele contém `Songs/MixDrumRock - Lote teste 01/`, com uma pasta por música, além de
`LEIA-ME.txt`, `musicas.csv` e `receita-verificada.json` na cópia reconstruída.
Não há ZIPs internos.

| Artista | Músicas |
| --- | --- |
| Linkin Park | Numb; Lying From You; From The Inside |
| Nirvana | Come As You Are; Dumb; All Apologies |
| Iron Maiden | Fear of the Dark; Hallowed Be Thy Name; The Number of the Beast |
| The Beatles | Come Together; Here Comes the Sun |
| Avenged Sevenfold | Requiem |

Extraia o ZIP, copie `MixDrumRock - Lote teste 01` de dentro de `Songs/` para a
pasta de músicas configurada no seu Clone Hero e execute **Scan Songs**. Escolha
**Pro Drums / Expert** em uma versão atual do jogo. Confira pratos, tons, bumbo e
sincronismo e registre o nome da faixa se algo não funcionar.

Foram verificados 12 `song.ini`, 11 MIDI e um `.chart`, 17.146 notas de bateria
Expert, marcações de pratos/tons e 40 arquivos de áudio decodificados por FFmpeg.
O ZIP foi testado, extraído novamente e todos os hashes dos arquivos conferidos.
O teste no jogo ainda depende do usuário; outros instrumentos não foram validados.
A correspondência com o Qobuz confere artista, título e duração próxima, sem
garantir o mesmo master/edição. O áudio de cada chart foi mantido com ele.

Uma versão de Heart-Shaped Box foi excluída porque tinha cinco pistas, e Dumb
entrou no lugar. Em Requiem, o único ajuste foi acrescentar `pro_drums=True` ao
`song.ini`, com base nos pratos já presentes no `.chart`. Áudio e notas não foram
convertidos ou reescritos. Arquivos auxiliares de editor e MIDIs de outros jogos
foram omitidos da entrega; os pacotes originais continuam em `downloads/`.

Na preparação original, fontes, uploaders, autores, hashes e verificações foram
registrados em `data/mixdrumrock/reports/pilot-*.json` e no catálogo
`data/mixdrumrock/catalog/pilot-01.csv`; esses arquivos locais também podem faltar
após uma retomada. A cópia recuperada inclui fontes, autores e hashes em
`receita-verificada.json`, com `game_verified=false`. A biblioteca pré-existente
do usuário não foi fornecida; este
lote fica em uma pasta própria para facilitar comparação e movimentação.

Para preparar outro ZIP nativo de uma única música, sem sobrescrever uma pasta:

```text
uv --cache-dir .uv-cache run --locked --with mido==1.3.3 python -m drumforge.library.packages ARQUIVO.zip --output-dir NOVA_PASTA
```

O helper rejeita caminhos inseguros, symlinks, colisões de nomes no Windows,
pacotes muito grandes, ausência de bateria Expert/Pro Drums e áudio ilegível.
Ele usa FFmpeg/ffprobe instalados e Mido opcional para inspecionar o mapa de tempo
e `PART DRUMS`. Outros instrumentos podem usar extensões SysEx de Phase Shift que
Mido não interpreta; esses chunks ficam fora da inspeção, preservados no original.
Não se usa clipping genérico nem se altera o MIDI para fazer a análise passar.

## Atualizar a lista sem Soundiiz

Na raiz do repositório, use um diretório novo para cada exportação:

```text
uv --cache-dir .uv-cache run --locked python -m drumforge.library.qobuz 69773629 --output-dir song-library/data/mixdrumrock/inbox/qobuz-NOVA-DATA
```

Para também gerar Excel, use a ferramenta opcional com versão fixa, sem alterar
as dependências do projeto:

```text
uv --cache-dir .uv-cache run --locked --with openpyxl==3.1.5 python -m drumforge.library.qobuz 69773629 --output-dir song-library/data/mixdrumrock/inbox/qobuz-NOVA-DATA --xlsx
```

Substitua `NOVA-DATA` por uma data/hora ainda não usada. O exportador recusa
diretórios existentes. O CSV usa UTF-8 com BOM; o Excel tem filtros e cabeçalho
fixo. São guardados `playlist.csv`, `playlist.json`, `manifest.json` e, com a opção
`--xlsx`, `playlist.xlsx`. A primeira exportação está em
`data/mixdrumrock/inbox/qobuz-2026-10-16/`.

O helper acessa somente metadados de playlists públicas pelo mesmo endpoint usado
pelo frontend do Qobuz. Ele lê o identificador público da aplicação; não usa senha,
token pessoal, segredo da aplicação ou endpoints de áudio. A interface pode mudar:
nesse caso o comando falha explicitamente. Ele confere contagem, paginação,
posições e identificadores de entradas e recusa snapshots parciais ou alterações
da playlist durante a captura. Músicas repetidas em entradas distintas são mantidas.

## Organização portátil

```text
song-library/
├── README.md
├── templates/
│   ├── playlist.csv
│   └── catalog.csv
└── data/                         # conteúdo local ignorado pelo Git
    └── mixdrumrock/
        ├── inbox/                # exportações originais da playlist
        ├── catalog/              # catálogo e escolhas persistentes
        ├── downloads/            # pacotes originais, preservados
        ├── work/                 # extração e conversão temporárias
        ├── Songs/                # pastas preparadas para o Clone Hero
        ├── reports/              # encontradas, dúvidas, faltantes e falhas
        └── exports/              # ZIP completo ou volumes por lote
```

Mova `data/mixdrumrock/` para transportar a coleção inteira; para levar apenas as
músicas ao jogo, copie `Songs/` para sua biblioteca configurada no Clone Hero.
O catálogo futuro deve guardar caminhos relativos a `mixdrumrock/`, sem depender
da letra de unidade do Windows ou do diretório desta máquina na nuvem.
As pastas de dados locais já foram criadas neste ambiente; diretórios vazios não
são versionados. Nenhum desses dados deve entrar em commits ou distribuições.

## O que é viável e o que precisa ser conferido

- É viável organizar centenas de faixas, localizar candidatas com drums,
  preparar os formatos suportados e produzir um ZIP com as pastas extraídas.
  Um relatório deve acompanhar os casos pendentes. Disponibilidade de 100% das
  faixas e automação integral dos downloads ainda não estão comprovadas.
- A playlist do Qobuz fornece a lista e os metadados para a busca. Ela não é um
  pacote de charts. Áudio de uma edição diferente pode perder o sincronismo;
  não substituir automaticamente o áudio que acompanha um chart.
- Guitar Hero III originalmente não tem bateria. Converter uma chart só de
  guitarra não cria drums. É preciso verificar os instrumentos de cada pacote,
  mesmo que o título ou a categoria mencione Guitar Hero.
- Pacotes já preparados para Clone Hero normalmente têm `song.ini`,
  `notes.mid` ou `notes.chart` e áudio compatível. Essa estrutura sozinha não
  comprova a existência de drums ou Pro Drums: o chart precisa ser inspecionado.
- Pacotes de Rock Band/CON e outros formatos podem precisar de conversão por
  ferramenta específica, como as opções do Onyx ou C3 CON Tools. A ferramenta,
  a versão e o formato de entrada serão escolhidos após inspecionar um pacote
  real; nenhuma conversão foi testada nesta entrega. Não basta renomear arquivos.
- Drums e Pro Drums devem ser registrados separadamente. Compatibilidade final
  só será confirmada depois de você usar Scan Songs e tocar no Clone Hero.

## Fluxo recomendado

1. Capturar a playlist pública com o comando acima, ou receber CSV/XLSX com
   artista e título. Álbum, duração, versão, ISRC e link da faixa ajudam na
   identificação. Preservar a exportação em `inbox/`. Não é necessário enviar senha.
2. Importar a lista e inventariar as músicas que você já tem. Preservar a ordem
   da playlist e registrar duplicatas; versões ao vivo, covers e regravações
   permanecem distintas. Usar identificadores estáveis quando disponíveis.
3. Procurar no RhythmVerse com filtro de bateria, guardando candidatos e fontes.
   Artista/título aproximados geram sugestões, nunca uma confirmação automática
   de mesma gravação. Priorizar a edição correta e Pro Drums quando disponível.
4. Validar um piloto de 5–10 músicas com formatos diferentes antes do lote maior.
   Conferir downloads acessíveis, instrumentos, conversão, áudio e o Scan Songs
   no seu computador. Registrar autor, origem e resultado por faixa.
5. Processar o restante em lotes retomáveis, com poucas conexões simultâneas,
   limites do serviço respeitados e falhas registradas. Links externos podem
   exigir interação; registrar esses casos em vez de marcar sucesso. Manter
   originais e extrair em `work/`, rejeitando caminhos fora da pasta de destino.
6. Copiar somente pacotes validados estruturalmente para `Songs/`, sem sobrescrever
   versões existentes. Gerar nomes compatíveis com Windows e um identificador
   curto para resolver colisões. Retomar pelo catálogo, sem repetir downloads
   íntegros ou perder escolhas. A validação estrutural antecede o teste no jogo.
7. Produzir um ZIP contendo `Songs/Artista - Música [id]/...` e relatório das
   pendências, sem ZIPs internos no lugar das músicas. Se o volume for grande,
   oferecer lotes independentes. Estimar tamanho e espaço livre antes de gerar;
   manter os arquivos originais e nunca sobrescrever a biblioteca já existente.
8. Em atualizações da playlist, processar apenas novas entradas ou mudanças
   identificadas. Não apagar músicas locais só porque saíram da playlist.

## Catálogo e estados planejados

`templates/catalog.csv` define uma base para o catálogo futuro. `drums` e
`pro_drums` usam `yes`, `no` ou `unknown`; ausência de informação nunca vale `yes`.
O SHA256 é do pacote baixado; ele permite checar integridade e repetição, não
identifica sozinho qual gravação da música foi chartada.

| Estado | Significado |
| --- | --- |
| `pending_search` | Ainda não pesquisada. |
| `needs_review` | Mais de uma candidata ou gravação/instrumento incerto. |
| `not_found` | Pesquisa concluída sem candidata adequada; pode ser refeita depois. |
| `selected` | Candidata escolhida, com origem e instrumentos registrados. |
| `downloaded` | Pacote recebido e integridade registrada. |
| `needs_conversion` | Formato exige conversor ainda não executado com sucesso. |
| `prepared` | Estrutura e instrumentos verificados; ainda falta testar no jogo. |
| `game_verified` | Usuário confirmou Scan Songs e drums/Pro Drums jogáveis. |
| `blocked` | Link, acesso, formato ou outra falha identificada; motivo em `notes`. |

O CSV real em reports/cobertura.csv usa esses estados de preparação e mantém uma
linha por entrada do Qobuz; `drum_mode` distingue Pro Drums e Drums comuns.
O backlog oficial permanece em [BACKLOG.md](../BACKLOG.md), itens DCF-LIB-001–008.

## Evidência e pendências desta sessão

O histórico abaixo descreve a captura inicial. A continuação de 2026-10-17 está
registrada em [library-bulk-verification.md](../docs/library-bulk-verification.md).

O bloqueio HTTP CONNECT 403 observado no início de 2026-10-16 foi resolvido após
o usuário publicar acesso sem restrições. Qobuz e o catálogo RhythmVerse
responderam HTTP 200. Isso confirma conectividade; a busca automatizada e os
downloads dos provedores de charts ainda precisam ser investigados.

O link público `https://open.qobuz.com/playlist/69773629` retornou MixDrumRock com
681 faixas. O exportador coletou sete páginas, confirmou a revisão ao final e
preservou as 681 posições e IDs de entrada; são 681 IDs de faixa distintos.
CSV e XLSX foram reabertos e comparados ao snapshot de origem, incluindo a duração
total de 182953 segundos. Uma segunda captura reproduziu a lista; a tentativa de
reutilizar o primeiro diretório falhou sem alterar seus arquivos.
Os testes cobrem paginação incompleta, repetição de página, mudança de revisão e
preservação de músicas repetidas e versões. O lote de 12 charts passou pelas
verificações estruturais e de áudio descritas acima; nenhum foi testado no jogo.

Ainda falta inventariar as músicas que você já tem (uma lista de pastas/metadados
é suficiente; não é necessário enviar toda a mídia). A playlist já está disponível
localmente, sem necessidade de arquivo do Drive ou assinatura de exportação.

## Prompt para continuar

> Leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md, depois
> song-library/README.md e docs/library-bulk-verification.md. Continue somente a
> biblioteca MixDrumRock, em uma branch a partir de main, sem avançar transcrição.
> O usuário confirmou o recebimento do piloto e autorizou o restante. O snapshot
> público de 2026-10-17 tem 744 entradas; 254 charts novos em 11 lotes, mais os
> 12 do piloto, cobrem 275 entradas. Não marque game_verified sem Scan Songs/playtest.
> Consulte song-library/reports/cobertura.csv para as 469 pendências. Preserve versões
> e escolhas; não substitua áudio, não apague arquivos locais nem repita downloads
> verificados. Receitas/índice em src/drumforge/library são duráveis; dados ignorados
> e ZIPs de /workspace/shared/downloads podem desaparecer. CONTINUACAO.md oferece
> recuperação no PC. Para atualizar, exporte Qobuz para diretório novo, execute o
> coletor drumforge.library.batch com Mido 1.3.3/gdown 5.2.1 opcionais e o Onyx
> 20261016 oficial verificado. Gere receitas com drumforge.library.delivery,
> acrescentando lotes sem modificar os existentes; confira todos os hashes e
> atualize COLLECTION_SHA256 do baixador quando o índice mudar. Separe Pro Drums e
> Drums comuns; cinco pistas ainda precisam de conversão real validada. Confira
> se provedores indisponíveis mudaram antes de repetir tentativas. A biblioteca
> pré-existente do usuário não foi inventariada. Documente evidências e pendências,
> execute os gates configurados e conclua com commit, merge --no-ff, push e
> verificação de sincronização, preservando o trabalho se a publicação falhar.

O baixador recebeu uma correção após falhas do Onyx no Windows em 2026-10-17:
não passe `+RTS -N2` à distribuição CLI do Windows; preserve o limite do AppRun
Linux. O índice referencia a versão corrigida do auxiliar. O bloco de retomada
em CONTINUACAO.md atualiza três arquivos e reaproveita os downloads existentes.
Leia também docs/library-onyx-recovery-fix.md; preserve `Logs/Onyx` ao investigar
novos erros. A confirmação da retomada no Windows e o teste no jogo permanecem
dependentes do resultado do usuário.

O usuário também autorizou comparar sua biblioteca antiga (aproximadamente 4 GB)
com os lotes. O comparador local `complement.py` + `local_library.py`, de biblioteca
padrão, produz o complemento em ZIP64 e relatórios sem alterar as coleções. Leia
SEM-REPETIDAS.md: prioridade para os lotes realmente presentes, versões incertas
fora do ZIP para revisão, repetidas antigas registradas e destino novo a cada
execução. Não confunda o inventário de teste com os arquivos reais do usuário;
aguarde comparacao.csv/avisos.csv para revisar seu resultado. A nova biblioteca
deve ser montada em pasta vazia, mantendo a antiga como backup.

Em 2026-10-18, o usuário relatou demora no Onyx e enviou KeyboardInterrupt durante
a importação de Endless, Nameless, após concluir o lote 09 e conferir sete faixas
do lote 10. O baixador agora informa etapa/tempo/log a cada 15 segundos; Ctrl+C
encerra com instruções de retomada. Leia CONTINUACAO.md. Isso não confirma a causa
da demora nem aceleração: inspecione o log local do Windows antes de diagnosticar.
O usuário esclareceu que interrompeu essa importação antes dos três minutos;
o traceback não comprova travamento ou vencimento do limite.

O relato posterior de Stain trouxe 731 s de importação com limite anunciado de
180 s, sem seleção de texto/suspensão segundo o usuário. O runner foi corrigido
para separar criação/espera/saída e supervisionar o próprio processo com prazo
monotônico, sem join de console ilimitado. Logs `.tempos.jsonl` registram as etapas;
leia CONTINUACAO.md antes de interpretar novos tempos. O defeito de medição foi
reproduzido; a causa dos 731 s no Windows ainda não foi determinada. Preserve as
receitas e verificações locais, e não atribua a demora a ações do usuário sem prova.
