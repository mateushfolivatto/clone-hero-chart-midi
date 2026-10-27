---
name: drum-audio-diagnostics
description: Investigar batidas ausentes ou falsas em transcrição de bateria para Clone Hero, gerar espectrogramas e comparar mixagem, bateria e componentes separados pelo Moises ou por um separador local. Use para chimbal fraco, mascaramento, limiares por instrumento e avaliação de precisão e recall.
---

# Diagnóstico de transcrição de bateria

Use processamento de sinais e evidência do áudio para investigar falhas. Esta skill
orienta o Codex e fornece um analisador local; ela não é um novo modelo treinado.
Leia as instruções AGENTS.md do projeto e respeite a fase vigente antes de editar.
Por preferência do usuário, aplique este procedimento em toda tarefa de música
para chart, mesmo sem uma falha de chimbal relatada. A skill orienta diagnóstico;
não substitui o transcritor nem transforma os candidatos espectrais em notas.
Após cada experimento, atualize esta skill com resultados e limitações observados,
para reutilizar o aprendizado em músicas futuras. Busque o melhor resultado
mensurável por instrumento; não prometa 100% de acerto a partir de exemplos.
Não substitua o modelo nem avance o exportador para resolver uma hipótese de áudio.

## Primeiro estabeleça os fatos

1. Inspecione o adaptador, o checkpoint, o pré-processamento e os argumentos reais.
   Diferencie código desta cópia de mudanças que só existem no PC do usuário.
2. Localize áudio e MIDI privados. Se faltarem, entregue diagnóstico do código,
   procedimento e demonstração sintética; não alegue ter ouvido/testado a música.
3. Escolha um trecho de 15–30 s com falhas, incluindo notas fracas e ataques
   simultâneos. Anote a origem absoluta do recorte, versão da música e configurações.
4. Compare o MIDI bruto à exportação antes de culpar o detector. Uma nota pode ser
   perdida na classificação, no peak picking, na normalização ou no mapeamento.

## Inspecione o MIDI bruto

Após `transcribe`, gere os diagnósticos antes de ajustar limiares:

```powershell
uv --cache-dir .uv-cache sync --locked --extra diagnostics
uv --cache-dir .uv-cache run --locked drumforge inspect-midi 'work/raw.mid' --out 'output/diagnostico-midi'
```

Adapte os caminhos e use uma pasta de saída nova. O extra opcional fixa Mido
1.3.3; não instala ML. `report.json` contém SHA256 do MIDI, mapa de tempo e
contagens por nota/grupo BD SD HH TT CY UNKNOWN. `events.csv` preserva tempos em
segundos, notas GM, velocidades armazenadas e ataques simultâneos, sem deduplicar
ou quantizar. Velocidade MIDI não é intensidade acústica estimada nem confiança.

O comando espera percussão GM no canal 10 (índice 9). Ele rejeita `PART DRUMS`,
formato 2 e divisão SMPTE, e informa notas ignoradas em outros canais. Não passe
um `notes.mid` de Clone Hero: seus números de notas significam pistas do jogo.
Os tempos partem do zero do MIDI; se a transcrição veio de um recorte, registre
separadamente sua origem na música antes de comparar ao gráfico com `--start`.

## Gere os gráficos

### Aprender com charts existentes e ondas

Quando houver músicas já chartadas, use-as como referências fracas de tempo e
pistas, em vez de esperar somente por Turn to Ashes. O experimento de cinco músicas
está em `docs/five-song-chart-reference.md`, com receita e resultados agregados em
`docs/experiments/`. Ele usa dois trechos de 20 s por música, mix reconstruída e
stems de bateria já presentes, sem baixar ou treinar modelos.

Resolva eventos de mix Expert antes de usar cores como referências. O flag `d`
em `[mix 3 drums2d]` (ou eventos locais equivalentes em .chart) indica disco flip:
em Pro, vermelho armazenado vira prato amarelo e amarelo armazenado vira caixa,
inclusive se era tom. Vale desde o tick do evento até o próximo mix Expert;
`dnoflip` e mix sem flag não trocam notas. Outras dificuldades não resetam Expert.
O leitor resolve estados no mesmo tick independentemente da ordem, recusa conflitos
e mantém números de nota/tempos/velocidades de origem. `group` é a pista Pro
resolvida; `midi_note` continua sendo a pista armazenada, não uma nota GM.

Fora do disco flip, leia marcadores de tom 110/111/112 por seus intervalos antes de
interpretar notas Expert 96–100. Nota 98 com marcador 110 é tom amarelo; sem ele,
prato amarelo.
Prato amarelo é **proxy de possível chimbal**, não identificação acústica garantida.
O mesmo vale para o pad vermelho como proxy de caixa. Charts podem simplificar
ataques; não copie MIDI do jogo como se já fosse percussão GM de um transcritor.

Na raiz do repositório, ajuste a raiz dos lotes já extraídos:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py study --recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --out 'output/referencia-cinco-musicas'
```

O script fixa NumPy/Matplotlib/Mido em lock próprio e reutiliza o espectrograma e
fluxo desta skill. Confere os hashes dos 36 arquivos da receita, aplica tempo MIDI
e delay explícito, preserva ataques simultâneos e soma os stems com ganho comum.
`song.ogg` de um pacote multitrack pode conter somente acompanhamento: não o chame
sozinho de mixagem completa. Prévia/crowd e codificações duplicadas são excluídas.
O decoder usa guarda final de 100 ms e corta ao número exato de amostras do trecho;
isso corrige a sobra de quadros, sem mover ataques ou preencher stems curtos.

Calibre regras de faixa/limiar em quatro músicas e teste na quinta. Todos os
trechos da quinta devem ficar fora da calibração. Correspondência uma a uma a
±30 ms, excluindo 50 ms de cada borda; reporte TP/FP/FN, precisão, recall, F1 e
erro temporal. Não ajuste offsets ou limiares usando os rótulos da música de teste.
Este benchmark mede coincidência com charts, não acurácia acústica independente.

Inspecione `report.html`, dez PNGs, `report.json`, `chart-events.csv`,
`held-out-candidates.csv` e `spectral-profile.json`. Os gráficos também mostram
tons e outros pratos como contexto. O perfil final é calibrado nas cinco músicas;
as métricas independentes são as dos cinco folds, não um teste desse perfil final.

Resultado em 2026-10-27: na mix, F1 de bumbo 0,385→0,599 e proxy de caixa
0,339→0,468; prato amarelo 0,472→0,456. O ajuste não melhorou o chimbal e o stem
de bateria não foi superior em toda classe/música. Não substitua defaults ADTOF
com esses números: ADTOF não foi comparado neste experimento.

Para propor candidatos em outro áudio, sem fornecer um chart:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py predict 'audio/musica.wav' --profile docs/experiments/five-song-spectral-profile.json --start 30 --duration 20 --out 'output/candidatos-experimentais'
```

Essa saída é CSV de candidatos experimentais e proveniência, ainda sem chart de
jogo ou dinâmica/confiança estimadas. O perfil declara uso automático não
recomendado. Não complete colcheias nem chame todos os agudos de chimbal; anote
um trecho por instrumento, incluindo outros pratos e simultaneidades, para a
próxima comparação com ADTOF ou um método multibanda mais discriminativo.

### Testar em outras músicas sem recalibrar

Use o subcomando evaluate para medir a transferência do perfil já salvo. Ele
confere o hash do perfil e a receita original, rejeita músicas/charts da calibração
e não chama o calibrador. Não ajuste offsets ou faixas após olhar os rótulos de
teste. O estudo externo CoD/Avenged Sevenfold está em docs/cod-a7x-heldout.md.

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py evaluate --recipe docs/experiments/cod-a7x-heldout-recipe.json --profile docs/experiments/five-song-spectral-profile.json --training-recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --out 'output/cod-a7x-teste'
```

Não exija bateria isolada para avaliar a mixagem: um pacote pode ter somente
guitar.ogg/song.ogg com o áudio completo. Registre a seleção efetiva; bateria só
entra no agregado das músicas que têm seus stems. Não invente stems ou compare
agregados de amostras diferentes como se fossem os mesmos pares.

O leitor também aceita notes.chart: flags 66/67/68 no mesmo tick marcam pratos;
sem esses flags as notas coloridas são pads/tons. Isso é diferente do MIDI, onde
110/111/112 marcam tons e a ausência deles indica prato nas pistas amarelo/azul/
verde. Preserve Resolution, mudanças de BPM, Offset e delay do INI. Não invente
velocidade de MIDI para .chart: registre null e a convenção de números de pista.

No teste CoD/A7X de 2026-10-27, sem recalibração, mix F1 foi 0,428→0,424 em bumbo,
0,395→0,513 no proxy de caixa e 0,218→0,279 em prato amarelo. O perfil perdeu
recall. Carry On falhou inclusive com a regra original; investigue pareamento,
alinhamento e mascaramento antes de atribuir uma causa. Os trechos de 115 não
têm prato amarelo no chart: não use esse F1 como recall de chimbal. Preserve
os casos ruins no relatório e não troque janelas depois de ver os resultados.

O usuário lembra que, nas músicas de CoD/Avenged discutidas, o amarelo corresponde
a chimbal, geralmente aberto. Use essa informação como hipótese principal para
revisar esses pares, com origem explícita no relato do usuário; não a estenda a
todo o catálogo nem atribua abertura a cada nota sem conferir o trecho. Preserve
YELLOW_CYMBAL_PROXY nas métricas congeladas. Zero notas dessa classe em um recorte
não comprova ausência de chimbal audível, como no caso a revisar de 115.

Na revisão do chimbal aberto, examine ataque e cauda de energia no espectrograma
e no envelope. A cauda pode sobrepor o ataque seguinte; sustentar energia não
significa um novo golpe. Compare também chimbal fechado, ride/crash e ataques
simultâneos de caixa/bumbo. Duração isolada não identifica o prato. O detector
atual usa picos de fluxo por faixa, sem classificar aberto/fechado nem modelar
explicitamente o decaimento. Esta é uma hipótese para o próximo experimento,
não uma melhora já medida ou motivo para retocar o perfil congelado.

### Chimbal mantendo a pulsação: Faint e Crawling

O usuário indicou essas músicas de Linkin Park como exemplos. O estudo está em
`docs/linkin-park-hihat.md`, com receita e resultados em docs/experiments/.
Para reproduzir, use evaluate com `linkin-park-hihat-recipe.json`, o mesmo perfil
e a receita original de calibração. Mantenha 60–80 s e 120–140 s sem recalibrar.
Faint tem mix; Crawling tem mix e bateria. Não atribua a ambas a lembrança de
chimbal geralmente aberto relatada antes para CoD/A7X: abertura aqui não foi anotada.

Crawling revelou o disco flip ignorado: o amarelo Pro passou de 52 para 212
referências nos recortes após corrigir a leitura, sem alterar o detector. O leitor
registra versão semântica 2 e notas reclassificadas. Compare referências antigas
antes de atribuir uma diferença de score ao algoritmo de áudio. Os eventos dos
dez charts anteriores e Faint ficaram idênticos após esta correção.

Nas sequências chartadas, Faint tem passos típicos de 222 ms; Crawling alterna
286/143 ms. Meça diferenças consecutivas dentro do recorte, com PPQN explícito,
sem completar notas. O detector original de agudos superou o perfil restritivo:
F1 de amarelo 0,618→0,589 em Faint/mix, 0,683→0,550 em Crawling/mix e
0,847→0,824 em Crawling/bateria. A bateria recuperou ataques neste exemplo;
não generalize nem mude defaults ADTOF sem outra avaliação independente.

### Auditar e aproveitar componentes existentes

Consulte `docs/stem-component-study.md` e as receitas/resultados correspondentes
em docs/experiments/. A comparação adicional nas sete músicas CoD/A7X/Linkin usa
as mesmas janelas e regras; não é um novo teste independente. O avaliador aceita
`component_sources` explícitos por grupo, que devem apontar a arquivos distintos
já selecionados e fixados por hash. As regras congeladas de bateria são aplicadas
por classe a esses componentes, sem argmax ou supressão entre instrumentos.

Decodifique antes de confiar no nome do stem. Brompton Cocktail tem drums.ogg
exatamente silencioso nos dois recortes; The Number of the Beast tem drums_2.ogg
silencioso em 60–80 s. Não conclua que o arquivo inteiro está vazio. O avaliador
v2 registra peak/RMS, exclusões e class_coverage com músicas, recortes, segundos
e referências por classe. Exclua apenas silêncio digital exato, preservando áudio
muito fraco. Não pontue um componente indisponível como falha de detecção.

Em Afterlife/Crawling, drums_1/2/3 foram declarados como bumbo/caixa/restante do
kit. O terceiro ainda contém tons e pratos: não é chimbal isolado. Nos mesmos
80 s, F1 congelado bateria→componentes: bumbo 0,661→0,610, caixa 0,482→0,761 e
amarelo 0,686→0,776. Fonte melhor depende da classe. Não transforme seleção feita
após este teste em ganho independente nem altere defaults ADTOF com esses dados.

Para receber stems de um separador em uma música sem chart:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py predict-components --kick 'audio/kick.wav' --snare 'audio/snare.wav' --high-percussion 'audio/kit-ou-hihat.wav' --profile docs/experiments/five-song-spectral-profile.json --rules baseline --start 30 --duration 20 --out 'output/candidatos-componentes'
```

O comando usa somente áudio e regras, registra hashes/ganho comum/silêncio e
gera CSV experimental. `--rules frozen` usa o perfil salvo de bateria. Os stems
precisam já estar alinhados; duração igual não comprova isso. Não há separação,
identificação de aberto/fechado, MIDI ou chart de jogo nesse comando.

### Recursos externos: distinguir acesso de inferência

Não é necessária assinatura para os ensaios locais. Em 2026-10-27 obtivemos sete
MP3 (3,35 MB) do exemplo oficial StemGMD/Bluebird com referências e resultados
pré-calculados LarsNet, revisão a5f75326. Identidade Git blob e SHA256 estão em
docs/experiments/stemgmd-author-sample.json. Mídia permanece privada/ignorada.
Os gráficos e SI-SDR comparam as saídas publicadas; não representam LarsNet rodando
nas nossas músicas, acurácia de notas ou um teste amplo. Não houve MIDI de
referência usado na amostra. O HH publicado combina aberto/fechado.

StemGMD declara CC BY 4.0. O modelo LarsNet anuncia CPU, 562 MB e pesos CC BY-NC
4.0; esses pesos não foram baixados/executados, e a compatibilidade Windows local
não está validada. E-GMD não foi integrado. Songsterr MIDI/GP é opção paga,
dispensável aqui. Informe o estado real de cada recurso; não chame demonstrações
de terceiros de inferência nossa. Audite revisão/hash/licença antes de instalar
um separador, preserve a mix e compare uma amostra reservada por instrumento.

O script `scripts/inspect_audio.py`, relativo a esta skill, usa FFmpeg local,
NumPy e Matplotlib. Não importa PyTorch, não baixa pesos e não envia áudio.
O uv pode instalar as dependências Python declaradas e travadas no lock do script.
Explique essa instalação se necessária; não exija Docker, WSL, CUDA ou uma API paga.

Na raiz do projeto, em PowerShell, use uma linha por comando:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/inspect_audio.py 'audio/musica.mp3' --start 30 --duration 20 --out 'output/diagnostico-mix' --ffmpeg-path 'C:/caminho/ffmpeg.exe'
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/inspect_audio.py 'audio/musica.mp3' 'audio/drums.wav' 'audio/hi-hat.wav' --start 30 --duration 20 --out 'output/diagnostico-comparado' --ffmpeg-path 'C:/caminho/ffmpeg.exe'
```

Adapte os caminhos reais. Cada saída precisa ser uma pasta nova. O máximo é 60 s
e oito arquivos; prefira trechos curtos no CPU. Se uv não estiver no PATH, use o
executável local já documentado no projeto. Não altere o ambiente ML para gráficos.

Abra `report.html` e inspecione também PNG, `report.json` e `candidates.csv`.
Os gráficos mostram envelope, espectrograma e fluxo espectral positivo por faixa,
com limiar local baseado em mediana/MAD. O cálculo usa a média das potências dos
canais; isso evita cancelamento de fase antes da análise espectral. O relógio
inclui `--start`. Primeiros/últimos 24 ms não produzem candidatos, por efeito de borda.

**Limite essencial:** agudos não significam automaticamente chimbal. Caixa,
guitarras, ride e crash também têm energia nessa região. Os pontos do relatório
são candidatos espectrais, não rótulos de instrumento ou probabilidades do modelo.
A escala de cor é compartilhada entre entradas; o fluxo é normalizado por faixa
para inspeção. Não use contagens de candidatos como acurácia de transcrição.

## Experimento de separação

- Preserve uma linha de base com a mixagem original.
- Compare à bateria isolada e, quando disponível, ao chimbal isolado.
- O Moises Pro documenta stems de kick, snare, toms, hi-hat e cymbals. Receba os
  arquivos exportados localmente; não invente integração, API ou plugin instalado.
  Upload ao Moises depende de ação/autorização do usuário.
- Exporte WAV/FLAC sem alterar velocidade, tom ou silêncio inicial. Não normalize
  cada stem individualmente na primeira comparação. Conversão de MP3 para WAV
  não recupera frequências perdidas; prefira a melhor fonte disponível.
- Confirme alinhamento com ataques comuns. Mesmo nome/duração não prova alinhamento;
  o script não estima atrasos. Ajuste explícito deve ficar registrado.
- Separação pode remover chimbais fracos ou introduzir vazamento e falsos ataques.
  Compare o resultado, não presuma melhoria. Uma bateria isolada ainda mistura
  bumbo e chimbal; stems por componente podem ser mais úteis para esse caso.
- Se optar por alternativa local, audite plataforma/CPU, tamanho, revisão, hash e
  licença do checkpoint antes de qualquer download. Pesos nunca são implícitos.

## Sensibilidade por instrumento e eventos simultâneos

O CLI atual aceita `--thresholds BD SD HH TT CY` e requer `--skip-separation`.
Este último significa que o projeto não executa um separador: um WAV já separado
externamente também pode ser a entrada. Prepare-o com `prepare-audio` primeiro.

O adaptador traduz a ordem pública BD SD HH TT CY para a ordem real do ADTOF
`85c192e`: BD SD TT HH CY (`LABELS_5 = [35, 38, 47, 42, 49]`). Antes desta correção,
o terceiro e quarto limiares eram enviados trocados em relação à ajuda do CLI.
O processo isolado agora rejeita uma ordem upstream diferente. Não troque valores
novamente no CLI; HH continua sendo o terceiro argumento público.

Sem ajustes prévios, os defaults upstream equivalem ao vetor público
`0.22 0.24 0.22 0.32 0.30`. Confirme a revisão antes de reutilizar esses valores.
Mantenha BD/SD/TT/CY fixos e varie apenas HH em pequenas etapas. Se havia
`--threshold` uniforme, mantenha esse valor nas outras quatro posições. Valores
menores aceitam mais ativações, aumentando também falsos positivos. Nenhum limiar
é recomendado como solução sem medir o trecho do usuário.

Não aplique argmax/softmax entre instrumentos: bumbo e chimbal podem tocar juntos.
Peak picking e deduplicação precisam operar por classe; um ataque forte de bumbo
não pode consumir o ataque simultâneo de chimbal. Preserve tempos sem quantização.
Não complete colcheias/semicolcheias automaticamente só por serem plausíveis.

Quando autorizado a implementar DCF-114, preserve as ativações por classe no
adaptador isolado e mantenha validação estrita do checkpoint. A API upstream
`return_activations=True` retorna antes de escrever MIDI: não basta ativar esse
argumento no comando atual e continuar esperando o arquivo. Ativação não deve ser
chamada de confiança calibrada. Se o MIDI já contém HH e o jogo não, investigue o
exportador; se não há pico HH, abaixar o limiar pode ser insuficiente.

## Meça antes de escolher

Anote manualmente tempos e classes de um trecho curto. Faça correspondência
um-para-um por classe, com tolerância explicitada (por exemplo, ±30 ms).
Calcule TP/FP/FN, precisão, recall, F1 e erros de tempo por classe. Inclua notas
simultâneas, pausas de chimbal, viradas e crash/ride para revelar falsas detecções.
Use outro trecho para conferir o ajuste e evitar adaptar tudo a uma única passagem.

Escolha entre mix, bateria ou fusão por classe apenas quando houver ganho medido.
Uma futura fusão pode manter BD/SD da mix e complementar HH pelo stem, deduplicando
somente dentro da classe e corrigindo offsets explícitos. Não substitua nem misture
saídas silenciosamente. Separe resultados sintéticos, resultados musicais reais
e validação no Clone Hero. Entregue config, versões, métricas, falhas e próximo teste.

## Fontes primárias

- [ADTOF-pytorch](https://github.com/xavriley/ADTOF-pytorch), revisão local `85c192e`.
- [Separação disponível no Moises Pro](https://help.moises.ai/hc/en-us/articles/360010972019-Which-instruments-can-be-separated-on-the-Pro-plan).
- [Riley e Dixon: combinação de stems e transcrição](https://arxiv.org/abs/2509.24853).
- [Fluxo espectral na documentação librosa](https://librosa.org/doc/0.11.0/generated/librosa.onset.onset_strength.html).

Fontes orientam o experimento; não demonstram acurácia nesta música.
