# Linkin Park — Faint e Crawling: chimbal marcando tempo

O usuário indicou Faint e “crawler”, interpretada como Crawling, como exemplos
de chimbal mantendo a pulsação. Os dois pacotes já estavam nos lotes locais.
Usamos a skill do projeto e o perfil anterior congelado, sem treinar modelo,
ajustar limiares ou escolher offsets pelos resultados.

## O que a inspeção encontrou

Crawling contém eventos MIDI `[mix 3 drums2d]`. Eles indicam disco flip: em Pro
Drums, o vermelho armazenado vira prato amarelo e o amarelo armazenado vira caixa,
inclusive quando este tinha marcador de tom. O efeito termina no próximo evento
de mix Expert que não tenha o flag `d`; `dnoflip` não troca notas. Outros níveis
de dificuldade não alteram Expert. Os estados valem desde o tick do evento.

Nosso leitor ignorava essa convenção. A correção reclassifica 422 notas na música
inteira, preservando tempos, ticks, números de nota armazenados e velocidades.
O CSV mantém `midi_note` como origem; `group` representa a pista resolvida para
Pro Drums. O relatório registra versão semântica 2 e a contagem de reclassificações.
A mesma regra é aplicada aos eventos locais de mix em .chart, com ou sem
colchetes/underscores. Estados conflitantes no mesmo tick são recusados.

Uma leitura inicial, anterior à correção, contou apenas 52 amarelos nos recortes
de Crawling; a leitura correta conta 212. Aquela pontuação inicial não serve para
avaliar chimbal. A mudança corrige a referência, sem melhorar ou retunar o detector.
Os dez charts dos estudos anteriores e Faint foram comparados com o leitor
anterior: seus eventos permanecem idênticos. Os arquivos originais não mudaram.

Fontes consultadas em 2026-10-27:

- [Formato MIDI: Mix Event Details](https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/mid-format/Tracks/Drums/).
- [Formato .chart: Local Events](https://thenathannator.github.io/GuitarGame_ChartFormats/Chart-File-Formats/chart-format/Tracks/Drums/).
- [Onyx: interpretação Pro em computePro](https://github.com/mtolly/onyx/blob/master/haskell/packages/onyx-lib/src/Onyx/MIDI/Track/Drums.hs).

## Dados e pulsação

A receita fixa 13 arquivos, os mesmos intervalos 60–80 s e 120–140 s por música
e o SHA256 do perfil `57986ca5e92f8b258d30035dbae4c8a3807f59d945b87ee77ff25fa9873f8b0b`.
Faint tem um song.ogg completo e notes.chart; Crawling tem notes.mid e oito
streams, incluindo três de bateria. A mix de Crawling é uma soma técnica dos
stems com ganho comum; não reproduz necessariamente os ganhos do jogo/master.
São 80 segundos únicos de música, 508 referências-alvo na mix e 40 segundos de
bateria somente em Crawling, com 279 referências-alvo. Não há stem de chimbal
isolado. Os IDs/charts são novos em relação às cinco músicas de calibração.

| Música / recorte | Amarelos Pro | Intervalo mediano | Padrão observado no chart |
| --- | ---: | ---: | --- |
| Faint / 60–80 s | 80 | 222 ms | Predominam passos de meia semínima |
| Faint / 120–140 s | 45 | 222 ms | Mesmo passo, com uma interrupção longa |
| Crawling / 60–80 s | 99 | 143 ms | Alterna passos de meia e um quarto de semínima |
| Crawling / 120–140 s | 113 | 143 ms | Predominam passos de um quarto de semínima |

Faint usa 192 ticks por semínima: 116 dos 123 intervalos consecutivos são de
96 ticks, compatíveis com colcheias em cerca de 135 BPM. Crawling usa 480 ticks:
146 dos 210 intervalos são de 120 ticks e 64 de 240, compatíveis com semicolcheias
e colcheias em cerca de 105 BPM. Esses números descrevem o chart e seu tempo;
não são uma estimativa de BPM independente pelo áudio.

A cadência é calculada entre referências consecutivas dentro de cada recorte,
sem unir trechos separados. O JSON guarda medianas, histogramas de diferenças
em ticks e simultaneidades. Há 60 amarelos simultâneos a bumbo/caixa em Faint e
49 em Crawling. Não se completam notas por regularidade nem se interpreta uma
interrupção do chart como prova de silêncio acústico.

## Resultados com a referência corrigida

Correspondência uma a uma a ±30 ms, com exclusão de 50 ms nas bordas, sem
quantização, deslocamento ou recalibração. “Original” é o detector espectral
anterior à calibração; “perfil” é a regra congelada das cinco primeiras músicas.
O alvo abaixo é o amarelo Pro, interpretado como chimbal segundo o relato do
usuário. A identificação e a abertura não foram anotadas acusticamente por evento.

| Música / áudio | Ataques de referência | Encontrados original → perfil | F1 original → perfil |
| --- | ---: | ---: | ---: |
| Faint / mix | 125 | 93 → 73 | 0,618 → 0,589 |
| Crawling / mix | 212 | 143 → 97 | 0,683 → 0,550 |
| Crawling / bateria | 212 | 185 → 173 | 0,847 → 0,824 |

O perfil mais restritivo perde chimbais nas duas músicas. Na bateria de Crawling,
a regra original encontra 185 ataques e propõe 40 extras; o perfil encontra 173
e propõe 35 extras. Neste par, a bateria permite recuperar ataques que faltam
na mix. Isso não estabelece superioridade geral de stems nem ganho sobre ADTOF.
Os gráficos mostram espectrogramas e referências/candidatos, sem alegação de
escuta humana independente. O detector não classifica aberto/fechado.

Na mix das duas músicas, F1 por classe original → perfil: bumbo 0,290→0,699,
caixa aproximada 0,355→0,390 e amarelo 0,656→0,566. O ganho de bumbo não justifica
usar os mesmos critérios restritivos no chimbal. A próxima comparação deve
preservar o detector original de HH como referência e medir outro trecho
independente, incluindo simultaneidades, pausas e outros pratos. Nenhum default
ADTOF ou regra de produção mudou com este estudo.

## Reproduzir e verificar

Na raiz do projeto, ajuste a raiz dos lotes e use uma saída nova:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py evaluate --recipe docs/experiments/linkin-park-hihat-recipe.json --profile docs/experiments/five-song-spectral-profile.json --training-recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --out 'output/linkin-park-hihat'
```

O HTML usa o título da receita, em vez de fixar CoD/A7X para qualquer avaliação.
Saídas: quatro PNGs, HTML autocontido, report.json, chart-events.csv,
candidates.csv e cópia idêntica do perfil. A receita e os resultados agregados
ficam em `docs/experiments/linkin-park-hihat-*.json`; áudio/charts e saídas por
evento ficam privados. Os hashes identificam esta cópia dos lotes; outra
conversão Onyx pode precisar de uma nova receita de proveniência.

Os 12 casos novos de disco flip cobrem MIDI/.chart, notas simultâneas, fronteiras
de estado, `dnoflip`, outras dificuldades, marcador de tom, eventos conflitantes,
flag desconhecido e preservação dos dados de origem. São 141 testes do núcleo e
oito opcionais de DSP, todos aprovados em Linux/Python 3.12.14 com NumPy 2.3.5,
Matplotlib 3.10.8 e Mido 1.3.3. Locks, Ruff, mypy, CLI/doctor e build passaram;
os avisos do doctor sobre ML/pesos ausentes são esperados. Os pacotes de build
foram inspecionados para excluir mídia privada, modelos e caches. Os 13 arquivos
de entrada e o perfil continuaram idênticos após a análise. O ZIP temporário
`output/Linkin-Park-Faint-Crawling-chimbal.zip` reúne HTML/gráficos, relatórios,
CSV, receita, perfil e este guia, sem áudio ou charts originais.
Execução nativa Windows, ADTOF, anotação acústica por evento
e Scan Songs/playtest permanecem pendentes; Phase 1 continua aberta.
