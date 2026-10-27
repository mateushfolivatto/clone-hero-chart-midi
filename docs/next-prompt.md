# Próximo prompt completo

Leia integralmente AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md.
Releia lessons.md ao consultar o backlog e após recuperar contexto. Leia a skill
`.agents/skills/drum-audio-diagnostics/SKILL.md` em toda tarefa de música para chart.
Audite Git/ambiente antes de editar, preserve trabalho existente e use uma branch
nova a partir de main para uma nova unidade. Continue a branch existente se a
unidade ainda estiver aberta. Preserve a implementação inspect-midi.

DCF-127 comparou fontes explícitas em sete músicas já discutidas e adicionou
predict-components sem chart. Leia docs/stem-component-study.md e suas receitas.
O usuário quer rota sem assinatura e atualização contínua da skill com evidências
para músicas futuras; não prometa 100%. O avaliador v2 exclui silêncio digital
de bateria/componentes, preserva sinais fracos e registra cobertura por classe.
Brompton tem drums.ogg zero nos dois recortes; seus resultados históricos de
bateria incluíam o arquivo pelo nome e não têm a mesma cobertura do novo agregado.
Nos mesmos 80 s de Afterlife/Crawling, F1 bateria→componentes é 0,661→0,610 bumbo,
0,482→0,761 caixa e 0,686→0,776 amarelo. O kit restante não é chimbal isolado.
São músicas já examinadas, sem recalibrar; não é um novo teste independente.

Já foram obtidos sete MP3 de demonstração StemGMD/LarsNet (3,35 MB) pelo conector
GitHub, com hashes/proveniência e comparação às referências. São saídas publicadas
dos autores, sem inferência local ou MIDI de referência; E-GMD não foi integrado.
Não confunda recurso consultado, amostra baixada e modelo executado. Pesos LarsNet
(562 MB, CC BY-NC 4.0) não foram baixados. Próximo menor experimento: auditar/pinar
runtime e pesos de um separador CPU, executá-lo em uma amostra reservada e comparar
mix/bateria/componentes por instrumento, junto ao ADTOF quando disponível. Não
contorne rede bloqueada nem baixe modelos implicitamente. Preserve baseline,
tempos brutos e licença separada de código/pesos. Consulte docs/testing.md.

DCF-126 inspecionou Faint e Crawling, indicadas pelo usuário como exemplos de
chimbal marcando tempo. Leia docs/linkin-park-hihat.md e sua receita/resultados.
O leitor antigo ignorava disco flip de Crawling. Agora resolve mix Expert com
flag d em MIDI/.chart: vermelho vira prato amarelo, amarelo (até tom) vira caixa;
dnoflip/outro mix Expert encerra a troca. A semântica v2 mantém origem/tempos e
registra reclassificações. Não interprete midi_note armazenada como group já
resolvido. Foram corrigidas 422 notas na música; dez charts anteriores e Faint
mantiveram eventos idênticos. Nos recortes de Crawling há 212 amarelos Pro.
O perfil permaneceu congelado. F1 do amarelo original→perfil: Faint/mix
0,618→0,589; Crawling/mix 0,683→0,550; Crawling/bateria 0,847→0,824.
Use o detector original de HH como referência no próximo teste independente;
não complete a cadência nem infira aberto/fechado pelo relato genérico ou cor.
As sequências chartadas têm passos de 222 ms (Faint) e 286/143 ms (Crawling).

DCF-125 também foi executado: leia docs/cod-a7x-heldout.md e os arquivos
cod-a7x-heldout-* em docs/experiments/. O perfil das cinco músicas anteriores
ficou congelado e foi aplicado a 115, Carry On, Not Ready To Die, Afterlife e
Brompton Cocktail, com 200 s e 1.157 referências na mix. Bateria existe só nas
duas últimas. O subcomando evaluate confere perfil/receitas e rejeita reutilização
de dados da calibração. Há suporte de referência a notes.chart com semântica
própria de pratos/tempo/offset e velocidade ausente como null.

No conjunto externo: F1 de bumbo 0,428→0,424, caixa aproximada 0,395→0,513,
prato amarelo 0,218→0,279. Houve perda de recall. Carry On teve pouquíssimas
correspondências até no detector original; revise pareamento/alinhamento/
mascaramento antes de escolher uma causa. Os trechos de 115 têm zero notas de
prato amarelo, portanto não medem recall de chimbal. Preserve casos ruins e não
recalibre após olhar o teste e depois chame a nova medição de independente.

O usuário lembra que o amarelo nas músicas de CoD/A7X discutidas era chimbal,
geralmente aberto. Use como hipótese principal com proveniência no relato,
preservando as classes/métricas congeladas. Revise ataque e cauda sobreposta,
compare aberto/fechado e outros pratos, e confira no áudio a ausência de
referências amarelas nos recortes de 115. O detector atual não classifica abertura;
não apresente essa hipótese como anotação por evento ou ganho medido.

O usuário autorizou estudar cinco músicas prontas como referências de áudio/chart
e combinar o resultado em arquivo e na skill. DCF-124 entregou esse experimento;
leia docs/five-song-chart-reference.md, a receita, resultados e perfil em
docs/experiments/. Foram usadas Numb, All Apologies, Come Together, The Number of
the Beast e Forsaken: 36 arquivos verificados, dois trechos de 20 s por música,
200 s e 860 ataques das três classes por modo de áudio.

A skill agora tem chart_reference.py com study/predict e lock próprio de
NumPy 2.3.5, Matplotlib 3.10.8 e Mido 1.3.3. study interpreta tempo/delay e
marcadores de tom, soma stems com ganho comum, calibra em quatro músicas e testa
na quinta sem misturar trechos entre os lados. predict usa só áudio/perfil e
exporta candidatos CSV; não gera chart de jogo. O perfil final foi calibrado
nas cinco músicas e depois avaliado nos conjuntos externos descritos acima.
Seu uso automático não é recomendado.

Resultados na mix, F1 contra o chart a ±30 ms: bumbo 0,385→0,599; proxy de caixa
0,339→0,468; prato amarelo 0,472→0,456. Houve troca de recall por precisão e o
chimbal não melhorou. Prato amarelo não é rótulo acústico garantido de chimbal;
pad vermelho também é proxy. Não mude defaults ADTOF com base nesses números:
ADTOF não foi executado/comparado. Preserve a mix de referência, os ataques
simultâneos e tempos sem quantização.

Próximo menor experimento: obter/anotar manualmente por instrumento um trecho
reservado de outra música, com caixa+chimbal simultâneos, pausas, tons e ride/crash.
Pode usar pares locais de outros lotes existentes, sem esperar só por Turn to
Ashes. Registre versão, origem e offsets; não ajuste o método olhando rótulos
do conjunto reservado. Compare o método espectral e ADTOF quando houver
ambiente/pesos locais verificados. Reporte TP/FP/FN, precisão/recall/F1 e erros.
Não declare identificação acústica por cores de chart ou acurácia por candidatos.

Windows/Python 3.12 CPU continua primário. Os resultados de 2026-10-27 são Linux;
141 testes do núcleo e 13 regressões opcionais de DSP passaram. Consulte
docs/testing.md. Não instale WSL, Docker ou CUDA nem altere políticas do PC.
O decoder do experimento usa guarda final de 100 ms e recorte por amostras,
sem mover ataques ou preencher stems curtos. Charts/áudios originais permanecem
privados/ignorados; receitas, agregados e regras são versionados.

Se executar ADTOF, use a revisão/peso auditados em
docs/phase-1-windows-compatibility.md, CPU e --skip-separation. O adaptador valida
SHA256 e carregamento estrito. --thresholds usa BD SD HH TT CY, traduzida uma vez
para BD SD TT HH CY no backend. Não baixe modelos nem faça uploads ao Moises sem
autorização específica. Velocidade MIDI não é confiança calibrada.

Phase 1 continua em andamento: Turn to Ashes, DCF-113/114 e validação privada
não foram concluídos. Não implemente exportador/GUI para contornar incertezas de
transcrição. Atualize documentos/backlog/lessons com evidências, execute gates,
inspecione artefatos e revise o diff exato. Faça commit da unidade verificada e
siga o Git workflow de AGENTS.md; merge --no-ff/push quando a unidade estiver
concluída, preservando commits e reportando bloqueios reais.
