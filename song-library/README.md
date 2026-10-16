# Biblioteca de músicas — MixDrumRock

Área separada para organizar a playlist do Qobuz e preparar charts já existentes
para tocar bateria no Clone Hero. A coleção pode crescer além de 600 músicas;
o processamento futuro deve ser incremental e preservar escolhas anteriores.
O pipeline de MP3 → transcrição do Drum Chart Forge continua independente.

O exportador de metadados do Qobuz já está implementado em
`src/drumforge/library/qobuz.py`. A MixDrumRock foi exportada com 681 faixas,
preservando ordem, versões e identificadores, em CSV, Excel e um snapshot JSON.
Busca de charts, downloads de músicas, conversão e empacotamento ainda não foram
implementados. Nenhum áudio foi baixado.

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
preservação de músicas repetidas e versões. Nenhum chart foi validado no jogo.

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
> existentes. Investigue a busca de drums no RhythmVerse; não suponha uma API.
> Comece por um piloto de 5–10 faixas, registrando fontes e ambiguidades. Após obter
> pacotes reais, valide um piloto com drums/Pro Drums e conversão apropriada,
> mantendo a confirmação no jogo separada da inspeção estrutural. Atualize os
> DCF-LIB no backlog com evidências, execute os gates pertinentes e siga o fluxo
> de commit, merge --no-ff e push sem descartar trabalho em caso de falha.
