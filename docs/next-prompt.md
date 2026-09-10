# Próximo prompt completo

Leia integralmente AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md.
Considere o kickoff como instrução de execução, CONTEXT.md como contexto canônico
e BACKLOG.md como única fonte de verdade das tarefas. Releia lessons.md sempre
que reler o backlog e depois de recuperar contexto. Registre novas lições com
evidência, prevenção e forma de verificação.

A Phase 0 foi concluída e verificada em docs/phase-0-verification.md. Antes de
alterar arquivos, audite git status, branch, runtime e ferramentas; confira os
quality gates atuais em docs/testing.md. Preserve alterações locais do usuário.
Use o repositório existente clone-hero-chart-midi em main. Não renomeie o remoto.
Antes de criar ou alterar arquivos, crie e entre em uma branch dedicada a partir
da main. Trabalhe nela; após concluir e verificar a tarefa, faça commit na branch
e merge --no-ff na main. Toda fase concluída deve terminar com commit e merge.
Se houver bloqueio ou critérios pendentes, mantenha o trabalho na branch sem
declarar a fase concluída. Verifique e informe hashes e estado final do Git.

Nesta sessão, trabalhe somente no menor experimento de preparação da Phase 1,
dentro de DCF-100 a DCF-122: estabelecer um backend ADTOF reproduzível em CPU e
inspecionar um pequeno MIDI bruto. Não implemente Phase 2 nem exportador Clone Hero.
Não marque toda a Phase 1 como concluída sem satisfazer seus critérios.

Leia docs/research-notes.md, docs/dependency-licenses.md e docs/architecture.md.
O ambiente validado é Windows nativo com Python 3.12.0, 4 processadores lógicos e
15.9 GiB de RAM. uv 0.12.13 está em .tools/bin/uv.exe; use cache local .uv-cache.
ffmpeg, PyTorch e os backends ML não foram instalados. O WSL contém apenas
docker-desktop; não assuma que Ubuntu existe. Se houver incompatibilidade comprovada,
documente o erro e o menor experimento alternativo, sem introduzir Docker.

Antes de adotar um backend, fixe o commit e verifique APIs, dependências e termos
do código e dos pesos separadamente. A licença dos pesos ADTOF convertidos e a
permissão do código ADTOF-pytorch continuam questões abertas. Não redistribua
modelos nem trate a licença MIT de um wrapper como autorização sobre checkpoints.
Se a ausência de permissão bloquear a adoção, avance no probe de áudio e contratos
testáveis com dados sintéticos, registrando o bloqueio sem baixar o componente.

O checkpoint ADTOF consultado tem 3.617.805 bytes. O downloader MDX23C anuncia
aproximadamente 500 MB por modelo; confirme os tamanhos reais antes de baixar.
Informe fonte, tamanho, cache e finalidade de downloads. Não baixe modelos grandes
silenciosamente. Mantenha o núcleo leve; instale ML somente em extra funcional ou
ambiente isolado com dependências e pesos identificados por versão/hash.

ATENÇÃO: a API ADTOF inspecionada pode continuar com pesos aleatórios se o arquivo
de checkpoint não existir. O adaptador deve rejeitar pesos ausentes/incompatíveis
antes da inferência. Use CPU explicitamente. Preserve timestamps brutos e metadados
disponíveis; registre o significado de velocidade/confiança retornadas pela API.

Procure somente nos diretórios privados previstos por áudio local autorizado,
sem movê-lo ou adicioná-lo ao Git. Se não houver entrada, prepare o experimento
com áudio sintético e solicite o caminho local para validação real quando necessário.
Comece com trecho curto, registre duração, formato, tempo de execução, contagem
de notas e timestamps. Não processe a música inteira antes de validar esse teste.

Ao terminar, execute todos os quality gates configurados, inspecione os artefatos,
verifique que não há áudio/pesos rastreados, atualize CONTEXT.md, BACKLOG.md,
docs/backlog.md e lessons.md. Distinga resultados reais, propostas e bloqueios.
Entregue relatório de concluído, verificações, decisões, riscos, arquivos alterados,
IDs do backlog e um novo próximo prompt completo.
