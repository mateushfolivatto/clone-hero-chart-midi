# Padrões em 64 músicas novas

A pedido do usuário, ampliamos o estudo em 2026-10-27 para 64 músicas novas de
20 artistas normalizados. São 128 recortes fixos (60–80 e 120–140 s), 42 min 40 s
nominais de música e 14.534 referências-alvo na mix: 5.916 de bumbo, 3.922 de
caixa aproximada e 4.696 de prato amarelo. Não analisamos cada música inteira.

O experimento aplica o detector espectral original e o perfil anterior congelado.
Não houve treino, reajuste de limiares, ajuste de offsets pelos rótulos, download
de modelos ou inferência ADTOF/LarsNet. Charts são referências fracas de jogo;
abertura do chimbal e identidade acústica por ataque continuam sem anotação.

## Seleção antes de pontuar

Foram encontrados 272 diretórios de música sob Songs e 236 candidatos novos
elegíveis. Excluímos 12 músicas já estudadas, seis cópias de chart, 16 charts que
não cobriam as janelas fixas, um pacote sem Pro Drums explícito e um .chart com
flag de prato órfão. Essas exclusões precederam as métricas de áudio.

A seleção percorre artistas normalizados em rodadas, usando seed fixa
`drumforge-survey-20261027-v1`. Dentro de cada artista prioriza componentes com
layout declarado, depois nomes de arquivos de bateria, depois hash semeado.
O teto permitido era cinco músicas por artista; nesta seleção o máximo foi quatro.
VIOLENT VIRA/Violent Vira é o mesmo artista normalizado. Trata-se de uma amostra
deliberada da coleção local, majoritariamente rock/metal, não de toda a música.

Participam Avenged Sevenfold, Angra, Dream Theater, Gojira, Iron Maiden, Linkin
Park, Metallica, Megadeth, Nirvana, Sepultura, Skillet, Slayer, Slipknot, Beatles,
System of a Down e outros cinco artistas. A receita fixa 352 arquivos por SHA256.
Não selecionamos substitutas após ver os resultados.

Há 31 músicas com nomes de arquivos de bateria. Behind The Crooked Cross tem
drums.ogg e outros streams exatamente zero nos dois recortes; a mix útil está
em song.ogg. Esses dois recortes de bateria são excluídos, mantendo a mix.
Restam 30 músicas/60 recortes/1.200 s de bateria útil. Doze músicas com layout
MIDI Expert drums1/2/3 e trio correspondente fornecem 24 recortes/480 s de
componentes. O restante do kit não é chimbal isolado. Layouts incertos não ganham
uma interpretação automática de componentes.

## Resultado geral na mix

Correspondência uma a uma a ±30 ms, excluindo 50 ms nas bordas, sem quantização.
F1 agregado soma TP/FP/FN; medianas por música com referências também são salvas.
Os intervalos abaixo reamostram músicas inteiras, preservando seus recortes e
ambos os métodos juntos, em 1.000 sorteios com seed fixa. Medem estabilidade
condicional a esta coleção, não corrigem erros de anotação ou viés da amostra.

| Referência | F1 original | F1 congelado | Intervalo 95% do ganho de F1 |
| --- | ---: | ---: | --- |
| Bumbo | 0,420 | 0,533 | +0,062 a +0,160 |
| Caixa aproximada | 0,426 | 0,526 | +0,061 a +0,142 |
| Prato amarelo | 0,417 | 0,441 | +0,008 a +0,039 |

O ganho vem com ataques perdidos. Recall de bumbo cai de 79,9% para 47,0%; caixa,
de 81,3% para 55,2%; amarelo, de 74,9% para 63,7%. Precisão congelada é 61,5%,
50,3% e 33,7%, respectivamente. Um F1 maior não basta para decidir qualidade de
um chart de prática; o perfil ainda aceita muitos eventos extras e omite notas.

## O que se manteve e o que mudou nos padrões

**Separar fontes ajuda de maneira diferente por instrumento.** A comparação
abaixo usa exatamente os mesmos recortes disponíveis em ambos os lados, com
perfil congelado; não compara a mix de 64 músicas com um subconjunto de stems.

| Fontes | Músicas pareadas | Bumbo F1 | Caixa F1 | Amarelo F1 |
| --- | ---: | --- | --- | --- |
| Mix → bateria | 30 | 0,549→0,667 | 0,555→0,492 | 0,467→0,501 |
| Bateria → componentes | 12 | 0,725→0,733 | 0,502→0,617 | 0,501→0,505 |

A melhora de caixa pelos componentes persistiu: intervalo do ganho +0,023 a
+0,204. Para amarelo nos componentes, o intervalo é −0,048 a +0,076, incluindo
ausência de ganho. O resultado forte obtido antes com Afterlife/Crawling não
justifica generalizar que componentes resolvem chimbal. A bateria completa,
por sua vez, melhorou bumbo e piorou caixa frente à mix nesta amostra pareada.

**Trechos esparsos precisam de controles negativos.** Em 62 recortes com menos
de dois amarelos por segundo, F1 congelado foi 0,298 e precisão 19,1%. Em 50
recortes com 2–5/s, F1 foi 0,569. Nos quatro recortes de três músicas com pelo
menos 5/s, F1 foi 0,674: esse último grupo é pequeno e não sustenta uma regra geral.

Em 12 recortes de oito músicas, o chart não contém amarelo. Ainda assim o perfil
propõe 691 candidatos dessa classe, ou 172,75/min pelos tempos nominais. São
desacordos com o chart, não prova de ausência física de chimbal. Em Octavarium,
nenhuma das três classes-alvo aparece nos dois recortes; esse caso entra como
controle de notas extras, sem inventar recall ou colocá-lo no ranking positivo.

**Coincidência com caixa/bumbo não prova isolamento de chimbal.** Na mix, recall
de amarelo congelado é 71,6% quando há caixa/bumbo no mesmo tick, contra 46,8%
sem eles. Esse resultado não confirma que o bumbo sempre masque chimbal. Picos
de outros instrumentos podem coincidir com as notas esperadas; diferenças de
arranjo e intensidade também interferem. É preciso anotar instrumentos e ouvir
casos reservados antes de atribuir uma causa acústica.

**Densidade também aumenta a chance de coincidência.** Após observar a relação
com densidade, acrescentamos um controle exploratório: 31 deslocamentos circulares
semeados por música/recorte, preservando contagem e janela útil de 19,9 s.
Os mesmos deslocamentos são usados para fontes/métodos; as predições reais não
mudam e nenhum deslocamento é escolhido para alinhar ou melhorar o teste.
F1 congelado real/controle médio foi 0,298/0,084 em trechos esparsos,
0,569/0,196 nos intermediários e 0,674/0,277 nos densos. O alinhamento real
contém informação, mas a oportunidade de casar picos varia entre grupos. Esse
controle não estabelece identidade de instrumento nem é um teste causal.

## Saídas e reprodução

As receitas, exclusões e ordem de seleção estão em
`experiments/broad-survey-recipe.json` e `broad-survey-selection.json`. Métricas
agregadas/intervalos ficam em `broad-survey-results.json` e as pontuações por música
em `broad-survey-song-metrics.csv`. Os relatórios completos, candidatos e notas
por evento continuam privados em output/. As regras do perfil não mudaram.

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py survey --recipe docs/experiments/broad-survey-recipe.json --profile docs/experiments/five-song-spectral-profile.json --training-recipe docs/experiments/five-song-chart-reference.json --library-root 'C:/caminho/downloads' --jobs 2 --out 'output/estudo-64'
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/survey_summary.py --recipe docs/experiments/broad-survey-recipe.json --reports 'output/estudo-64' --out 'output/resumo-64'
```

O runner limita cada processo a uma música e usa até dois workers CPU. Resume
exige `--resume`, os mesmos hashes de receita/entradas/perfil/código e versões;
confere report.json e CSV por recibo de conclusão. Diretório incompleto não é
sucesso nem é sobrescrito. Resumo recalcula as métricas a partir dos CSV e exige
igualdade com cada relatório. `--no-plots` evita gerar 128 figuras em todo lote.
O resumo tem lock próprio com os mesmos NumPy/Matplotlib/Mido já fixados.

`survey-plan` permite planejar outro grupo antes de pontuar, com raiz, perfil e
receitas anteriores a excluir, seed, contagem e teto por artista explícitos.
Não recalibrar nestas 64 músicas e depois chamar uma nova avaliação nelas de
independente. Uma nova conversão Onyx com Ogg diferentes requer nova proveniência,
sem relaxar os hashes desta receita.

Há quatro gráficos agregados e uma galeria diagnóstica posterior de seis músicas:
Octavarium, Carolina IV, Doing Time, Blackened, Lying From You e Territorial
Pissings. Ela ilustra controles, extremos e componentes, sem participar da seleção
ou alteração de regras. Suas reexecuções reproduziram os mesmos scores. Nem todas
as ondas foram inspecionadas visualmente e não alegamos escuta das 64 músicas.

Nesta entrega, `output/64-musicas-padroes-bateria.zip` reúne o relatório HTML,
quatro gráficos, a galeria, métricas CSV/JSON, receitas e os 64 relatórios por
música com candidatos/referências e recibos de execução. Extraia e abra
`report.html`; `LEIA-ME.md` explica o conteúdo. Não inclui áudio, MIDI original
ou pesos. O ZIP é temporário no workspace; os scripts, agregados e receitas
versionados permitem repetir o estudo com as entradas privadas correspondentes.

## Verificação e próxima decisão

As 64 músicas concluíram sem falhas. Uma repetição integral produziu os mesmos
128 CSV de referências/candidatos, byte a byte. Resume reutilizou os 64 relatórios
verificados sem recalcular áudio. O perfil e os 352 arquivos de entrada foram
preservados. Novas regressões cobrem seleção independente da ordem, limite por
artista, identidade de notas duplicadas, comparação de fontes no mesmo recorte,
bootstrap por música, controle temporal e rejeição de cache adulterado.

Passaram 146 testes do núcleo e 19 testes opcionais de DSP após integrar os
lotes temáticos da biblioteca. Locks, Ruff, mypy, CLI e build passaram; wheel e
sdist não contêm mídia/modelos privados. O ZIP de 14.732.657 bytes passou CRC e
conferência dos 569 hashes de conteúdo, mais seu manifesto (570 arquivos).

O estudo usa Linux/Python 3.12.14, NumPy 2.3.5, Matplotlib 3.10.8, Mido 1.3.3 e
FFmpeg local. Verificações e contagens finais estão em docs/testing.md. Windows
nativo e compatibilidade no Clone Hero continuam pendentes. Não houve mudança
nos defaults ADTOF ou promoção do perfil ao pipeline de produção. Phase 1 segue
aberta; não foi criado um novo chart jogável.

A próxima melhoria deve medir identificação de instrumentos, incluindo trechos
sem bateria/chimbal no chart, pratos diferentes e articulações abertas/fechadas.
O conjunto maior aponta que somente tornar limiares mais restritivos perde notas
e que separar o kit, por si só, não resolve a classe de chimbal.
