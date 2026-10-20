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
