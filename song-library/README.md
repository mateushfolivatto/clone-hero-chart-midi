# Biblioteca de músicas — MixDrumRock

Área separada para organizar a playlist do Qobuz e preparar charts já existentes
para tocar bateria no Clone Hero. A coleção pode crescer além de 600 músicas;
o processamento futuro deve ser incremental e preservar escolhas anteriores.
O pipeline de MP3 → transcrição do Drum Chart Forge continua independente.

Esta entrega cria a organização, os modelos CSV e o plano de trabalho. Ainda não
há importador, busca automática, downloader, conversor ou empacotador implementado.
A playlist real ainda não foi recebida e nenhuma música foi baixada.

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

1. Receber o arquivo MixDrumRock, de preferência CSV ou XLSX com artista e título;
   álbum, duração, versão, ISRC e link da faixa ajudam na identificação. O modelo
   em `templates/playlist.csv` é uma opção, não um requisito para receber o arquivo.
   Preservar a exportação original em `inbox/`. Não é necessário enviar senha.
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

Esses estados são uma proposta de contrato, não resultados da playlist real.
O backlog oficial permanece em [BACKLOG.md](../BACKLOG.md), itens DCF-LIB-001–006.

## Evidência e pendências desta sessão

Em 2026-10-16, as tentativas HTTPS de abrir
`https://rhythmverse.co/songfiles/game` e `https://rhythmverse.co/robots.txt`
falharam no proxy deste ambiente com `Tunnel connection failed: 403 Forbidden`.
Isso não é uma resposta do site e não comprova sua política de automação nem
disponibilidade atual. Não foi possível inspecionar a busca ou links de download.
A inclusão de `rhythmverse.co` na rede foi salva no rascunho de configuração;
ainda precisa ser aplicada/publicada nas configurações do ambiente e testada.
Outros domínios só serão necessários se os links reais apontarem para eles.

Este chat não dispõe de conexão com seu Google Drive. Para começar a coleção
real, anexe a exportação MixDrumRock ou forneça um link acessível. Um link público
da playlist também pode servir, dependendo do acesso. Depois precisamos de uma
amostra de pacote de chart e, para evitar duplicação, da lista da sua biblioteca
existente (sem necessidade de enviar toda a mídia agora).

## Prompt para continuar

> Leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md, depois
> song-library/README.md. Continue apenas a frente MixDrumRock, sem avançar fases
> de transcrição. Audite Git e runtime e use uma branch dedicada conforme as
> instruções do projeto. Com a playlist anexada, implemente primeiro importação
> e inventário incremental com dados privados em song-library/data/mixdrumrock/.
> Preserve versões e escolhas, não altere músicas existentes. Verifique acesso ao
> RhythmVerse antes de implementar integração; não suponha uma API. Após receber
> pacotes reais, valide um piloto com drums/Pro Drums e conversão apropriada,
> mantendo a confirmação no jogo separada da inspeção estrutural. Atualize os
> DCF-LIB no backlog com evidências, execute os gates pertinentes e siga o fluxo
> de commit, merge --no-ff e push sem descartar trabalho em caso de falha.
