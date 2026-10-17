# Biblioteca de músicas — MixDrumRock

**Para baixar o lote no seu Windows, use [BAIXAR.md](BAIXAR.md).** O baixador e
a receita estão no GitHub; a pasta `data` é gerada localmente e não é versionada.
Links de arquivos da máquina da nuvem não garantem disponibilidade após retomadas.

Área separada para organizar a playlist do Qobuz e preparar charts já existentes
para tocar bateria no Clone Hero. A coleção pode crescer além de 600 músicas;
o processamento futuro deve ser incremental e preservar escolhas anteriores.
O pipeline de MP3 → transcrição do Drum Chart Forge continua independente.

O exportador de metadados do Qobuz já está implementado em
`src/drumforge/library/qobuz.py`. A MixDrumRock foi exportada com 681 faixas,
preservando ordem, versões e identificadores, em CSV, Excel e um snapshot JSON.
Um primeiro lote privado de 12 músicas já foi obtido pelo RhythmVerse e preparado
com áudio e bateria Expert de quatro pistas. A integração geral de busca/download
para as 681 faixas continua pendente; o lote foi selecionado e conferido manualmente.

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

Esses estados são uma proposta de contrato; o catálogo de charts ainda não foi
preenchido a partir da lista real.
O backlog oficial permanece em [BACKLOG.md](../BACKLOG.md), itens DCF-LIB-001–006.

## Evidência e pendências desta sessão

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
> song-library/README.md. Continue apenas a frente MixDrumRock, sem avançar fases
> de transcrição. Audite Git e runtime e use uma branch dedicada conforme as
> instruções do projeto. A playlist de 681 faixas está no snapshot privado
> song-library/data/mixdrumrock/inbox/qobuz-2026-10-16/; atualize com o exportador
> se necessário. Faça o inventário incremental a partir da biblioteca existente
> quando sua lista for fornecida. Preserve versões e escolhas, não altere músicas
> existentes. O lote de 12 faixas está em exports/MixDrumRock-piloto-12.zip e o
> catálogo privado em catalog/pilot-01.csv, dentro da coleção original. Esses
> dados podem estar ausentes após uma retomada. A receita durável é
> src/drumforge/library/pilot_01.json; recupere o lote com recover_pilot.py conforme
> BAIXAR.md, mantendo a verificação de hashes. Uma cópia reconstruída nesta sessão
> está em /workspace/shared/downloads/MixDrumRock/. Receba o resultado
> do Scan Songs/playtest antes de marcar game_verified. O endpoint público de
> busca observado é POST https://rhythmverse.co/api/ch/songfiles/search/live,
> com instrument[]=drums, text, data_type=full, page e records (máximo 100).
> Resultados privados e plano estão em reports/rv-search/ e pilot-selection.json.
> Continue a integração incremental de busca/download e trate ambiguidades de
> versões. Use os helpers packages/inspect_song para pacotes nativos; conversão
> de console ou de cinco pistas ainda exige investigação própria. Atualize os
> DCF-LIB no backlog com evidências, execute os gates pertinentes e siga o fluxo
> de commit, merge --no-ff e push sem descartar trabalho em caso de falha.
