# Inspeção do MIDI bruto — 2026-10-20

O novo comando `inspect-midi` implementa as contagens e o CSV de debug da Phase 1
(DCF-118/119). Ele complementa a skill local antes da normalização/exportação.
O áudio de Turn to Ashes, o checkpoint e o ambiente ADTOF continuam indisponíveis
nesta cópia. A Phase 1 permanece em andamento; nenhum chart novo foi validado no jogo.

## Fluxo no Windows

Na raiz do projeto, use `uv` ou o executável local documentado no README:

```powershell
uv --cache-dir .uv-cache sync --locked --extra diagnostics
uv --cache-dir .uv-cache run --locked drumforge inspect-midi 'work/raw.mid' --out 'output/diagnostico-midi'
```

`work/raw.mid` é a saída de `transcribe`, depois de preparar o áudio com FFmpeg.
A instalação acrescenta Mido 1.3.3, opcional no runtime e incluído nos testes de
desenvolvimento, sem instalar PyTorch ou pesos. O núcleo permanece sem dependências
obrigatórias. A pasta de saída deve ser nova; o arquivo MIDI não é regravado.

Arquivos gerados:

- `report.json`: SHA256 e caminho do MIDI, formato, PPQN, duração MIDI, último
  ataque, mudanças de tempo, contagens por nota/grupo e avisos.
- `events.csv`: `time_seconds,midi_note,instrument,group,velocity,channel`.
  Cada linha é um note-on de percussão com velocidade positiva.

O inspetor lê formatos 0/1, combina o relógio das pistas e aplica mudanças de tempo
no tick correto. Sem evento de tempo inicial usa o padrão MIDI de 500.000 µs por
semínima. Isso interpreta o MIDI; não estima o BPM da gravação. Duração MIDI não
é duração do áudio, e a última nota pode terminar antes do arquivo musical.

Preserva ataques simultâneos, repetições, velocidades e tempos sem quantização.
Velocidade é somente o valor armazenado no MIDI; não foi implementada estimativa
de dinâmica acústica nem preservação de ativações/confiança do ADTOF (DCF-113/114).
As notas sem mapeamento ficam como UNKNOWN com seus números originais.

O escopo é percussão General MIDI no canal 10, representado por `channel=9` no CSV.
Notas em outros canais são contadas como ignoradas e geram aviso. Um arquivo sem
percussão gera relatório vazio com aviso. `PART DRUMS`, formato 2, tempo zero e
divisão SMPTE são recusados; não use um chart existente como MIDI de transcrição.

## Comparação orientada pela skill

Leia `.agents/skills/drum-audio-diagnostics/SKILL.md` em toda tarefa de criação de
chart. Escolha um trecho de 15–30 s e compare as linhas do CSV com o relatório
espectral da skill. Os tempos do CSV têm origem no zero do MIDI; registre a origem
de um eventual recorte e qualquer offset antes de confrontar os relógios.

Anote manualmente os ataques e classes. Conte correspondências uma a uma por
classe, usando tolerância explícita, antes de ajustar HH ou escolher stems.
Os picos espectrais são candidatos, e as contagens do MIDI são detecções; nenhum
dos dois, sozinho, mede precisão/recall. Preserve a mixagem de referência e valide
o ajuste em outro trecho. A exportação para pistas Pro Drums é uma fase posterior.

## Evidências desta entrega

Linux nativo/Python 3.12.14, CPU, FFmpeg 7.1.5; execução nativa Windows pendente.
Os 15 novos casos elevam a suíte a 104 testes. Incluem relógio com mudanças de
tempo entre pistas, classes simultâneas, running status, ataques duplicados,
velocidades zero/positivas, UNKNOWN, canal melódico, arquivos inválidos,
reprodutibilidade, preservação de saída, limpeza após falha e CLI real.
Ruff lint/format, mypy estrito e verificação do lock passaram offline.
Help/doctor e build de wheel/sdist passaram. Foram inspecionados os 43 membros do
wheel e 78 do sdist, sem áudio, pesos ou caches. O metadata do wheel declara Mido
somente sob o extra diagnostics. Regras de ignore e arquivos rastreados também
foram conferidos; o aviso de cache dentro da raiz não se confirmou nos pacotes.

Uma demonstração autoral de quatro segundos combina 15 pulsos fracos de 9 kHz e
sete pulsos graves fortes de 65 Hz, sete pares simultâneos. O MIDI de referência
foi escrito a partir desses tempos conhecidos, sem executar modelo. O inspetor
recuperou 22 ataques: 15 HH e sete BD, com último ataque em 3,75 s. O relatório da
skill mostrou 15 candidatos agudos e sete graves; PNG/HTML/JSON/CSV foram
inspecionados. Isso demonstra as ferramentas, não classificação de instrumentos
acústicos ou acurácia de transcrição. Os arquivos ficam em
`output/phase1-midi-demo-20261020/`, ignorados e temporários.

Os gates do núcleo rodaram por `uv --offline --locked`. Para preparar o ambiente
editável foi usado `--no-build-isolation` com Hatchling e editables 0.6 do cache;
editables foi removido pelo sync seguinte e não foi adicionado ao projeto.
O ambiente isolado do script não tinha o wheel NumPy em cache e sua execução via
uv offline foi recusada. O script foi executado diretamente com o Python do
ambiente, cujos NumPy 2.3.5 e Matplotlib 3.10.8 correspondem aos pins do script;
o lock de gráficos permanece inalterado. Nenhum download de modelo ou upload ocorreu.

Próximo passo: executar prepare-audio → transcribe → inspect-midi com Turn to
Ashes no Windows, comparar o trecho à skill e registrar DCF-116/117/120–122.
