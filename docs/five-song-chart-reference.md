# Charts e ondas de cinco músicas — 2026-10-27

O usuário propôs aproveitar os lotes já prontos para relacionar ataques do chart
com o áudio, descobrir características de bumbo/caixa/chimbal e preservar isso
num arquivo e na skill existente. O experimento foi executado com músicas reais,
sem esperar o áudio de Turn to Ashes e sem instalar modelos.

## Seleção e dados

Foram encontrados 76 pacotes locais com stems de bateria. A receita fixa cinco
artistas/gravações, cada um com dois trechos: 60–80 s e 120–140 s, total 200 s.

| Artista | Música | Lote |
| --- | --- | --- |
| Linkin Park | Numb | Piloto 01 |
| Nirvana | All Apologies | Piloto 01 |
| The Beatles | Come Together | Piloto 01 |
| Iron Maiden | The Number of the Beast | Piloto 01 |
| Dream Theater | Forsaken | 02 |

`experiments/five-song-chart-reference.json` fixa caminhos relativos e SHA256 de
36 arquivos (INI, MIDI e áudio). Todas as entradas foram verificadas antes da
análise. Nenhum original foi alterado, enviado a serviço ou adicionado ao Git.
As análises por evento e os gráficos permanecem em output/, privado/ignorado.
Os arquivos versionados são código, receita, métricas agregadas e perfil de regras.

A mix técnica soma igualmente todos os stems de reprodução reconhecidos,
excluindo prévia e crowd. O conjunto de bateria soma drums ou seus componentes.
Aplica-se um só ganho contra clipping à mix e à bateria de cada trecho; não há
normalização separada. Isso não reproduz necessariamente os ganhos do jogo ou
uma master comercial. O nome song.ogg sozinho não implica mix completa.

## O que o processo inverso identifica

O leitor integra mudanças de tempo MIDI, soma o delay do INI e interpreta os
intervalos dos marcadores de tom 110/111/112. Preserva simultaneidades e registra
outros tons/pratos além das três classes avaliadas. A inspeção limita-se ao
conductor e PART DRUMS para evitar SysEx de outras pistas, sem alterar o MIDI.

As referências de jogo são fracas: 96 = bumbo, 97 = pad vermelho/proxy de caixa,
98 sem tom = prato amarelo/proxy de possível chimbal. Um prato amarelo pode
representar outro prato; o chart pode simplificar o áudio. Não foram anotados
manualmente rótulos acústicos nem identificados chimbal aberto/fechado ou pedal.

## Método e resultados

Reutilizamos FFT estéreo, média de potências e fluxo espectral positivo da skill.
A regra original procura picos em 40–200 Hz, 200–4000 Hz e 4000–16000 Hz. O estudo
compara 90 combinações previamente fixadas de seis faixas, multiplicador MAD e
piso relativo, separadamente por classe. Não há argmax entre peças nem novo
treinamento ADTOF: são regras de processamento de sinais calibradas por grid.

Cada fold calibra em quatro músicas e testa em todos os trechos da quinta.
Não há recortes de uma mesma música dos dois lados. Nenhum offset é ajustado com
os rótulos da quinta. A comparação é uma a uma a ±30 ms, removendo 50 ms de cada
borda. Os 860 ataques das três classes são avaliados uma vez por modo de áudio.
Estes F1 medem coincidência com charts, não acurácia acústica ou resultado no jogo.

| Áudio | Referência | F1 original | F1 calibrado |
| --- | --- | ---: | ---: |
| Mix técnica | Bumbo | 0,385 | 0,599 |
| Mix técnica | Proxy de caixa | 0,339 | 0,468 |
| Mix técnica | Prato amarelo | 0,472 | 0,456 |
| Bateria | Bumbo | 0,414 | 0,635 |
| Bateria | Proxy de caixa | 0,366 | 0,441 |
| Bateria | Prato amarelo | 0,516 | 0,446 |

O ganho em bumbo/caixa veio com perda de recall: na mix, o bumbo passou de
293 TP/917 FP/18 FN para 205 TP/169 FP/106 FN. O proxy de caixa passou de
184/703/14 para 159/323/39. São menos candidatos falsos contra o chart,
porém mais notas perdidas. Para prato amarelo, a calibração piorou em quatro
das cinco músicas na mix; não é solução para chimbal ausente.

Come Together expõe uma dificuldade: seu chart completo tem 386 tons azuis e
73 pratos amarelos. Agudos e ataques de tom/outros pratos não podem ser rotulados
automaticamente como chimbal. A bateria isolada também não garantiu ganho: o F1
de bumbo em Come Together caiu de 0,303 para 0,255 após calibrar nos outros artistas.
Essas observações orientam o próximo teste, sem provar a identidade de cada som.

`experiments/five-song-results.json` retém agregados, folds, TP/FP/FN, erros de
tempo e regras escolhidas. `five-song-spectral-profile.json` combina as regras
calibradas nas cinco músicas para experimentos futuros. O perfil final não foi
testado em uma sexta música e declara uso automático não recomendado.

## Repetir e aplicar

Com os lotes já extraídos sob a raiz usada na receita, execute na raiz do projeto:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py study --recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --out 'output/referencia-cinco-musicas'
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py predict 'audio/musica.wav' --profile docs/experiments/five-song-spectral-profile.json --start 30 --duration 20 --out 'output/candidatos-experimentais'
```

O primeiro produz HTML autocontido, dez PNGs, JSON, CSV de eventos/referências e
CSV de candidatos fora da calibração, além do perfil. O segundo usa somente áudio
e perfil, sem ler chart, e produz candidate-notes.csv e proveniência. Ambos exigem
pasta nova e recusam entradas/configurações incompatíveis. Não produzem song.ini
ou notes.mid para Clone Hero. Esta é uma ferramenta de análise/proposição de
ataques da Phase 1; o exportador e a avaliação de Turn to Ashes continuam pendentes.

## Verificação e limitações

Linux/Python 3.12.14, CPU e FFmpeg 7.1.5. Foram usados NumPy 2.3.5, Matplotlib
3.10.8 e Mido 1.3.3 em ambiente temporário separado, reutilizando pacotes locais
e Mido do cache. O lock próprio do script foi conferido; a execução não instalou
ML nem baixou pesos. A execução nativa Windows permanece pendente.

117 testes do núcleo e sete regressões opcionais de DSP passaram, além de Ruff,
mypy e verificações de lock. Os testes cobrem fronteiras de marcadores/tempo,
delay, seleção de stems, correspondência um a um, exclusão de todos os trechos da
música de teste, equivalência exata com o detector original, silêncio, oposição
de fase e aplicação do perfil sem chart. O restante da biblioteca manteve seus testes.

Foi observada sobra de 352/448 amostras em recortes Vorbis de 20 s. O wrapper
decodifica uma guarda final de 100 ms e corta por contagem de amostras, sem
deslocar o início ou preencher stems curtos. Esse comportamento tem regressão.
Mesma duração não comprova alinhamento: os relatórios registram a hipótese do
mapa de tempo/delay e erros dos pares que coincidem; não há anotação acústica
independente, estimativa automática de atraso ou verificação de drift.

Próximo teste: anotar manualmente por instrumento um trecho reservado de outra
música, incluindo caixa+chimbal simultâneos, pausas e ride/crash. Comparar ADTOF
com esse conjunto; avaliar características multibanda sem afinar nos rótulos do
teste. Não substituir limiares ADTOF com este benchmark, que não executou ADTOF.

O build wheel/sdist passou; seus 46/86 membros foram inspecionados sem áudio,
pesos ou caches. Os 36 arquivos de entrada continuaram com os hashes originais
após a análise. O pacote privado temporário
`output/Charts-e-ondas-5-musicas.zip` (aproximadamente 12 MB) contém HTML autocontido,
perfil, relatórios/CSV e este guia, sem áudio/MIDI. CRC e conteúdo do HTML foram
conferidos. Arquivos em output/ não são um download permanente: a receita e os
comandos acima permitem regenerar o relatório a partir dos lotes existentes.
