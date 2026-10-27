# Componentes gratuitos e referências externas

O usuário autorizou começar sem depender de assinatura, usando as músicas já
discutidas e atualizando a skill para músicas futuras. Esta unidade usa arquivos
locais, uma pequena amostra pública e regras espectrais existentes. Não houve
cobrança, upload de músicas ou download/execução de novos pesos ML.

## Recursos usados e custo

| Recurso | Uso nesta unidade | Custo de acesso |
| --- | --- | --- |
| Stems dos lotes locais | Comparação de mix, bateria e componentes | Nenhuma assinatura adicional |
| StemGMD | Sete MP3 de demonstração, 3.354.638 bytes, com referências separadas | Acesso gratuito; dataset declarado CC BY 4.0 |
| LarsNet | Saídas pré-calculadas publicadas pelos autores, comparadas às referências | Acesso gratuito; modelo não executado localmente |
| E-GMD | Consultado como opção; nenhum arquivo usado | Dataset gratuito, ainda sem integração |
| Songsterr | Nenhum download ou assinatura nesta unidade | Exportação MIDI/GP é recurso Plus opcional |

O [StemGMD](https://zenodo.org/records/7860223) completo ocupa mais de 1 TB
descompactado. Usamos somente o exemplo Bluebird/funk de
[áudio dos autores](https://polimi-ispl.github.io/larsnet/), obtido pelo conector
GitHub em revisão `a5f75326ebcc4c253bce75cb74e029f5b75cfa88`. Foram conferidos
tamanho, identidade Git blob e SHA256. Os sete arquivos são mix e os pares
referência/estimativa de bumbo, caixa e chimbal. O exemplo junta chimbal aberto
e fechado; não há anotação MIDI de ataques nesta amostra baixada.

O [LarsNet](https://github.com/polimi-ispl/larsnet) anuncia execução CPU e pesos
de 562 MB sob CC BY-NC 4.0. Esses pesos não foram baixados, instalados ou testados.
Os exemplos demonstram o resultado dos autores, não uma execução nossa em Linkin
Park/A7X. Acesso gratuito não estabelece permissão de redistribuição/comercial.
Uma tentativa de acesso HTTP pelo shell aguardou permissão de rede e foi
interrompida; o conector GitHub conseguiu ler a amostra pública normalmente.

Créditos da amostra: Alessandro Ilic Mezza, Riccardo Giampiccolo, Alberto
Bernardini e Augusto Sarti, StemGMD / Toward Deep Drum Source Separation.
Os gráficos deste relatório são análises derivadas dessas fontes.

## Áudio real dos lotes: o nome do arquivo não basta

Auditamos 12 músicas já estudadas em 60–80 s. `drums.ogg` de Brompton Cocktail
e `drums_2.ogg` de The Number of the Beast retornaram somente amostras zero nesse
recorte. Isso não comprova silêncio no arquivo inteiro. Os demais valores e
hashes estão em `experiments/stem-source-audit.json`.

A nova avaliação lê também 120–140 s e registra peak/RMS/silêncio por arquivo e
recorte. Exclui bateria/componentes somente quando seu sinal é exatamente zero;
áudio fraco é preservado. A mix permanece como referência. Brompton tem bateria
silenciosa em ambos os recortes e fica fora deste agregado de bateria. Os antigos
relatórios, que incluíram o arquivo pelo nome, permanecem como registro histórico;
suas métricas de bateria não usam exatamente a mesma cobertura do novo ensaio.

Crawling e Afterlife têm três streams aproveitáveis. A receita declara as fontes
por classe, com base no layout do pacote e eventos de mix Expert: drums_1 para
bumbo, drums_2 para caixa e drums_3 para o restante do kit. Este último ainda mistura
chimbal, tons e outros pratos; não é um chimbal isolado. Não inferimos identidade
acústica por nome nem reutilizamos um arquivo como três componentes distintos.

## Comparação com regras inalteradas

Reavaliamos 115, Carry On, Not Ready To Die, Afterlife, Brompton Cocktail, Faint e
Crawling: 38 arquivos fixados, 14 recortes e 280 s de música. São as mesmas músicas
de testes anteriores, em uma comparação adicional de fontes; não é um novo teste
independente. O perfil, faixas, limiares, offsets e janelas não foram recalibrados.
Os componentes usam as mesmas regras do perfil de bateria. Há correspondência
uma a uma a ±30 ms, com exclusão de 50 ms nas bordas e leitura Pro/disco flip.

Mix tem sete músicas e 1.665 referências-alvo. Bateria e componentes usam somente
Afterlife/Crawling: 80 s e 511 referências, sendo 155 de bumbo, 119 de caixa e 237
de amarelo Pro. O JSON informa músicas, recortes, segundos e notas por classe.

| Classe — mesmos 80 s e perfil congelado | Bateria completa: F1 | Componentes: F1 |
| --- | ---: | ---: |
| Bumbo | 0,661 | 0,610 |
| Caixa aproximada | 0,482 | 0,761 |
| Prato amarelo / chimbal segundo o relato | 0,686 | 0,776 |

Os componentes melhoraram caixa e amarelo, mas pioraram bumbo. Em Afterlife,
amarelo passou de 15 TP/88 FP/10 FN para 20/39/5; em Crawling, de 173/35/39 para
176/33/36. Essas métricas medem acordo com o chart, não precisão acústica
independente. Não trocamos automaticamente o pipeline pela fonte vencedora.
Carry On continua com pouco acordo e os recortes de 115 sem referências amarelas.

O avaliador gera espectrogramas da mix, da bateria útil e do restante do kit
quando disponível. O raster identifica qual método/fonte gerou seus candidatos.
A versão 2 do relatório inclui `source_audio_audit`, `excluded_views` e
`class_coverage`, para impedir uma comparação de amostras diferentes sem aviso.

## Pequena amostra pública: o que verificamos

Comparamos 2–12 s da mix e dos stems publicados com suas referências, sem mover
os sinais. A métrica SI-SDR usa o estéreo concatenado, média removida e projeção
escalar; permite diferença global de ganho e penaliza erro de forma de onda.

| Componente | Mix contra referência | Saída dos autores contra referência |
| --- | ---: | ---: |
| Bumbo | 4,49 dB | 27,83 dB |
| Caixa | −4,67 dB | 17,01 dB |
| Chimbal | −30,41 dB | −5,33 dB |

As estimativas ficaram mais próximas das referências neste único exemplo. O
chimbal ainda apresenta erro considerável; SI-SDR não é acurácia de notas nem
garantia de desempenho nas nossas músicas. São cópias MP3 de uma demonstração
selecionada pelos autores, sem inferência local, MIDI de referência ou comparação
ADTOF. Receita de origem e resultados estão em
`experiments/stemgmd-author-sample.json`; mídia fica ignorada em output/.

## Reutilizar em músicas sem chart

O novo `predict-components` recebe três stems já alinhados. Não lê chart/MIDI,
não chama um separador e não completa notas por ritmo. A fonte de percussão aguda
pode ser chimbal isolado ou o restante do kit, com essa distinção registrada pelo
usuário. Os eventos são candidatos espectrais em CSV, ainda sem exportação jogável.

```powershell
uv --cache-dir .uv-cache run --no-project --locked --script .agents/skills/drum-audio-diagnostics/scripts/chart_reference.py predict-components --kick 'audio/kick.wav' --snare 'audio/snare.wav' --high-percussion 'audio/kit-ou-hihat.wav' --profile docs/experiments/five-song-spectral-profile.json --rules baseline --start 30 --duration 20 --out 'output/candidatos-componentes'
```

Use `--rules frozen` para o perfil salvo; baseline aplica as regras originais.
O comando registra hashes das entradas/perfil, janela absoluta, ganho comum,
auditoria dos sinais e classes indisponíveis. Preserva ataques simultâneos e
não normaliza fontes separadamente. Mesmos comprimentos não comprovam alinhamento;
ele precisa vir da separação ou ser conferido explicitamente antes.

Para reproduzir a comparação local, use `chart_reference.py evaluate` com
`experiments/stem-component-recipe.json`, o perfil e a receita de calibração
anteriores, a raiz dos lotes e uma pasta de saída nova. Os hashes fixam esta cópia;
uma nova conversão Onyx exige proveniência própria, pois seus Ogg podem mudar.

## Validação e próximo limite

O comando sem chart foi executado em Crawling 60–80 s, gerando 268 candidatos
com as regras originais. Cinco regressões novas de DSP verificam silêncio versus
áudio muito fraco, seleção de fontes, simultaneidades sem chart, mudança de entrada
durante leitura e cobertura parcial sem pontuar um componente indisponível.
Passaram 141 testes do núcleo e 13 opcionais de DSP em Linux/Python 3.12.14,
com NumPy 2.3.5, Matplotlib 3.10.8, Mido 1.3.3 e FFmpeg local. Locks, Ruff,
mypy, CLI/doctor e build também passaram. Os 38 arquivos locais e o perfil
permaneceram idênticos, e as métricas anteriores de mix/bateria não silenciosa
foram reproduzidas. Wheel/sdist foram inspecionados sem mídia, modelos ou caches.
O ZIP temporário `output/Componentes-e-referencia-gratuita.zip` reúne relatórios,
gráficos, CSV, receitas e este guia; não inclui áudio/charts originais ou pesos.
Windows nativo e desempenho de
separação/transcrição ML ainda precisam ser exercitados.

O próximo passo é executar um separador auditado e o transcritor em um trecho
reservado, comparando à mix e a anotações por instrumento. Este trabalho prepara
e mede as entradas; não implementa DCF-105/106, treinamento, exportador ou Scan
Songs. Phase 1 permanece aberta. Nenhum percentual de acerto futuro é garantido.
