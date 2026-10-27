# Call of Duty e Avenged Sevenfold — teste externo do perfil

Em 2026-10-27 o usuário pediu testar outras músicas de CoD e Avenged Sevenfold.
Usamos o perfil salvo no estudo anterior, sem recalibrar faixas/limiares nas novas
músicas, sem ajustar offsets pelos rótulos de teste e sem executar ADTOF.

## Dados e protocolo

| Música | Artista | Referência | Áudio disponível |
| --- | --- | --- | --- |
| 115 | Elena Siegman | notes.chart | Um stream do pacote |
| Carry On | Avenged Sevenfold | notes.mid | Um stream do pacote |
| Not Ready To Die | Avenged Sevenfold | notes.mid | Um stream do pacote |
| Afterlife | Avenged Sevenfold | notes.mid | Mix reconstruída e bateria |
| Brompton Cocktail | Avenged Sevenfold | notes.mid | Mix reconstruída e bateria |

115 vem da trilha de Black Ops Zombies; os pacotes de Carry On e Not Ready To Die
também são relacionados a CoD. Não se presume que a gravação de cada chart seja
idêntica a toda edição da trilha. A receita fixa as versões presentes nos lotes.

Cada música usa os mesmos intervalos previamente fixados: 60–80 s e 120–140 s.
São 200 segundos de música e 1.157 referências nas três classes da mix: 680 de
bumbo, 335 de pad vermelho e 142 de prato amarelo. A comparação de bateria usa
somente Afterlife/Brompton Cocktail: 80 s e 461 referências; não é a mesma amostra
de cinco músicas. Nenhum stem foi criado para as outras três.

`experiments/cod-a7x-heldout-recipe.json` fixa 25 arquivos de entrada e o SHA256
do perfil congelado. O perfil tem identidade
`57986ca5e92f8b258d30035dbae4c8a3807f59d945b87ee77ff25fa9873f8b0b`.
O avaliador confere sua receita de calibração, rejeita IDs usados nela e charts
duplicados sob outro ID. O arquivo do perfil permanece byte a byte inalterado.

As regras geram candidatos recebendo só áudio e perfil; os charts entram na
pontuação. O detector original de três bandas é a comparação. Correspondência
uma a uma a ±30 ms, com 50 ms excluídos de cada borda. O mapa de tempo e delay
do INI são preservados, com Offset adicional para .chart. Alinhamento acústico
e qualidade das anotações não foram verificados independentemente.

## Resultados

| Áudio | Referência aproximada | F1 original | F1 congelado |
| --- | --- | ---: | ---: |
| Mix — cinco músicas | Bumbo | 0,428 | 0,424 |
| Mix — cinco músicas | Caixa | 0,395 | 0,513 |
| Mix — cinco músicas | Prato amarelo | 0,218 | 0,279 |
| Bateria — duas músicas | Bumbo | 0,320 | 0,397 |
| Bateria — duas músicas | Caixa | 0,431 | 0,458 |
| Bateria — duas músicas | Prato amarelo | 0,165 | 0,192 |

Na mix o bumbo perdeu recall: 437 TP/927 FP/243 FN na regra original contra
232/183/448 com o perfil. A caixa passou de 231/603/104 para 153/108/182.
O prato amarelo passou de 117/816/25 para 108/524/34. O perfil elimina muitos
candidatos, mas perde mais ataques. O ganho em F1 de duas classes não demonstra
boa transcrição geral, identificação de chimbal ou melhora sobre ADTOF.

| Música — mix | Bumbo original→congelado | Caixa original→congelado | Prato amarelo original→congelado |
| --- | ---: | ---: | ---: |
| 115 | 0,659→0,730 | 0,384→0,528 | 0,000→0,000 (zero referências) |
| Carry On | 0,108→0,009 | 0,088→0,000 | 0,000→0,000 (duas referências) |
| Not Ready To Die | 0,552→0,528 | 0,530→0,783 | 0,613→0,762 |
| Afterlife | 0,444→0,462 | 0,598→0,667 | 0,167→0,203 |
| Brompton Cocktail | 0,355→0,291 | 0,335→0,447 | 0,165→0,149 |

Carry On merece investigação: inclusive a regra original teve pouca coincidência
com o chart. Os números não determinam se a causa é mascaramento, diferença de
gravação, alinhamento ou classificação. O caso permanece no agregado, sem escolher
offsets ou excluir a música depois de observar a falha. Os PNGs mostram a mixagem
e os ataques do chart para ajudar essa inspeção futura.

Os trechos de 115 têm zero notas de prato amarelo; os de Carry On têm apenas duas.
Um F1 zero nesses casos não mede recall de chimbal real. Charts usam cores como
convenções de jogo, podem simplificar a bateria e não são anotações acústicas
independentes. Tons e outros pratos aparecem como contexto nos gráficos.

## Suporte acrescentado

`chart_reference.py evaluate` aplica o perfil congelado a novos pares chart/áudio.
Ele aceita áudio único sem inventar bateria e informa quais músicas participam
de cada modo. A leitura de .chart distingue seus flags de prato 66/67/68 dos
marcadores de tom MIDI 110/111/112. Considera tempo variável e Offset; velocidade
fica null quando ausente em .chart. Números de pista são convertidos para a mesma
notação MIDI Expert apenas para comparar referências; não são GM de transcrição.

Execute na raiz do repositório, ajustando a raiz dos lotes:

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py evaluate --recipe docs/experiments/cod-a7x-heldout-recipe.json --profile docs/experiments/five-song-spectral-profile.json --training-recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --out 'output/cod-a7x-teste'
```

O comando gera dez PNGs, HTML autocontido, report.json, referências/candidatos CSV
e cópia idêntica do perfil. `experiments/cod-a7x-heldout-results.json` mantém as
métricas e contagens em Git; áudio, charts e saídas por evento ficam privados e
ignorados. Pastas de saída existentes são recusadas. Não há novo chart de jogo.

## Verificação e próximo teste

129 testes do núcleo e oito testes opcionais de DSP passaram em Linux/Python
3.12.14, com NumPy 2.3.5, Matplotlib 3.10.8, Mido 1.3.3 e FFmpeg local.
Os casos novos cobrem .chart versus MIDI, mudanças de tempo/offset, flags órfãos,
proibição de cinco pistas, áudio sem stem e rejeição de dados de calibração no
teste. A regressão de avaliação falha se qualquer função de calibração for
chamada, verifica ausência de bateria inventada e identidade do perfil.
Execução nativa Windows e Scan Songs/playtest continuam pendentes.

Lint/formatação, mypy estrito, locks e build wheel/sdist passaram. Os pacotes
foram inspecionados para excluir áudio, charts privados, pesos e caches. Os 25
arquivos de entrada e o perfil permaneceram idênticos após a análise. O pacote
temporário `output/CoD-Avenged-Sevenfold-teste-congelado.zip` contém HTML
autocontido, relatórios/CSV, perfil congelado, receita e este guia, sem áudio nem
charts originais; CRC e conteúdo foram verificados. As receitas versionadas
permitem reconstruir o relatório, pois output/ não é armazenamento permanente.
Os hashes fixam os bytes usados aqui. Uma reconversão Onyx pode produzir Ogg com
outros números de série, como já observado no projeto; uma réplica com arquivos
diferentes precisa de nova proveniência verificada, sem relaxar os hashes deste teste.

O próximo passo é revisar alinhamento/pareamento de Carry On e anotar manualmente
instrumentos num trecho reservado. Não ajustar o perfil sobre estes resultados e
chamar uma nova medição nas mesmas músicas de teste independente. Os resultados
não justificam ativar automaticamente o perfil no pipeline de produção.
