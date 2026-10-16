# Chimbal ausente: diagnóstico e skill local

Inspeção em 2026-10-16 desta cópia de `clone-hero-chart-midi`. A música privada,
stems, checkpoint e MIDI com as falhas relatadas não estão disponíveis aqui.

## Um defeito confirmado e corrigido

O CLI apresenta `--thresholds BD SD HH TT CY`, mas o adaptador enviava essa lista
sem tradução ao ADTOF `85c192e`. O [código fixado do backend](https://github.com/xavriley/ADTOF-pytorch/blob/85c192e78f716ea0b111cc8a5ee4a8f6a3a4f8a9/src/adtof_pytorch/post_processing.py)
define `LABELS_5 = [35, 38, 47, 42, 49]`: bumbo, caixa, tons, chimbal, pratos.
Consequentemente, ajustar o terceiro valor público alterava os tons, e o quarto
alterava o chimbal. Isso explica uma falha de configuração possível; não prova
que seja a causa de todas as notas ausentes na música do usuário.

O adaptador agora traduz os valores para a ordem upstream na fronteira do
subprocesso e verifica os rótulos ao importar o backend. O CLI mantém sua ordem
pública: **o terceiro valor ajusta o chimbal**. Sem opções explícitas, os defaults
upstream permanecem iguais. Valores antigos ajustados em torno do comportamento
invertido precisam ser reavaliados. Um teste de regressão verifica os limiares
enviados para as notas GM 42 (chimbal) e 47 (tons), sem instalar o modelo.

## Qual abordagem faz sentido

O ADTOF já usa uma representação espectral do áudio. Uma onda no tempo mostra a
soma dos sons; o espectrograma mostra a distribuição das frequências ao longo do
tempo. Transformada de Fourier, fluxo espectral e envelopes de ataque ajudam a
encontrar eventos fracos. Frequência, duração e contexto ajudam a classificá-los,
mas não existe uma frequência única que identifique cada peça da bateria.

Reconhecimento como Shazam procura uma gravação conhecida por impressões digitais
do áudio. Aqui precisamos de transcrição polifônica: qual instrumento atacou, em
qual tempo, inclusive quando vários tocam juntos. Uma skill organiza essa análise;
os sinais e os modelos fazem a detecção.

Nesta cópia, o separador é somente um passthrough: `--skip-separation` passa a
entrada diretamente ao transcritor. Não há integração Moises nem separação local
implementada. Um stem externo pode ser preparado e transcrito pelo fluxo existente.

A [documentação do Moises Pro](https://help.moises.ai/hc/en-us/articles/360010972019-Which-instruments-can-be-separated-on-the-Pro-plan)
confirma separação de bumbo, caixa, tons, chimbal e pratos. Primeiro compare a mix
à bateria isolada; para investigar mascaramento dentro do kit, acrescente o
chimbal separado quando disponível. Exporte arquivos com o mesmo início,
velocidade e versão, de preferência WAV/FLAC. Conversão de MP3 não recupera
informação que já foi descartada.

O [trabalho de Riley e Dixon](https://arxiv.org/abs/2509.24853) investiga a combinação
de stems e transcrição ADTOF, incluindo distinção de mais classes e estimativa de
velocidades. É uma base técnica útil para um experimento, sem garantir melhoria
em toda música. Separadores também podem apagar ataques ou introduzir vazamento.

## Usar a skill

A skill está em `.agents/skills/drum-audio-diagnostics/SKILL.md`, com script e lock
de dependências próprios. O núcleo do projeto continua sem dependências de runtime.
Não há instalação de modelo, integração remota ou upload de áudio por essa skill.

No Codex aberto na raiz do projeto, solicite:

```text
Use $drum-audio-diagnostics para investigar os chimbais ausentes. Leia as
instruções do projeto, compare o áudio original e os stems locais disponíveis,
gere os relatórios e meça precisão/recall antes de escolher qualquer ajuste.
```

Se a skill ainda não aparecer, reabra a sessão ou indique seu arquivo diretamente.
O arquivo SKILL.md contém comandos completos de PowerShell. O analisador usa
FFmpeg instalado e as dependências NumPy 2.3.5/Matplotlib 3.10.8 declaradas em
PEP 723; o lock ao lado do script fixa a resolução. O uv instala essas bibliotecas
em ambiente separado se necessário, sem modificar o ambiente do ADTOF.

Entradas: um a oito áudios locais, início e duração de até 60 s. Saídas em pasta
nova: HTML autocontido, PNG por áudio, JSON de configuração e CSV de candidatos.
O cálculo combina potências dos canais para preservar eventos em oposição de
fase. Os espectrogramas compartilham escala de cor; as curvas de fluxo têm
normalização própria por faixa. Os primeiros/últimos 24 ms não geram candidatos.
O script não alinha stems, classifica instrumentos ou exporta um chart.

Os pontos indicam aumentos espectrais em graves, médios e agudos, não notas de
bumbo/caixa/chimbal identificadas. Uma caixa ou um corte abrupto do bumbo também
pode criar agudos. A interpretação exige áudio, ativação por classe e MIDI.

## Validação desta entrega

- Linux/Python 3.12.14; execução nativa Windows deste analisador ainda não feita.
- 38 testes do projeto passaram, incluindo a regressão de HH/TT; Ruff e mypy passaram.
- Lock do núcleo, help/doctor, execução do script pelo lock próprio e builds
  wheel/sdist passaram. Os dois arquivos de distribuição foram inspecionados:
  nenhum áudio, modelo, cache ou arquivo temporário. O aviso de uv sobre cache
  dentro da raiz não se confirmou nos membros dos arquivos gerados.
- Demonstração autoral de quatro segundos: 15 ataques agudos fracos e sete ataques
  graves fortes, sete deles simultâneos aos agudos. As amplitudes de pico dos
  sinais geradores são 0.025 e 0.8; não são instrumentos acústicos gravados.
- No sinal sintético sem cortes bruscos, houve 15 candidatos agudos para 15 ataques,
  desvio máximo de aproximadamente 12 ms. Isso testa o analisador, não o ADTOF.
- Silêncio não gerou candidatos; estéreo em oposição preservou os agudos; recorte
  manteve tempos absolutos. FFmpeg real gerou o relatório inspecionado visualmente.
- Reutilizar a pasta de saída foi recusado sem alterar o relatório; início NaN
  foi recusado antes da geração. O relatório não contém áudio.

Não foi medida melhora de transcrição real nem compatibilidade no jogo. DCF-114
e DCF-116–122 continuam pendentes. O próximo experimento é receber um trecho
problemático e o MIDI correspondente, comparar mix/bateria/chimbal e variar só HH
mantendo os outros quatro limiares fixos. Registre TP/FP/FN, precisão, recall,
F1 e erro de tempo com correspondência um-para-um por classe. Confira o ajuste
em um segundo trecho antes de processar a música inteira.
