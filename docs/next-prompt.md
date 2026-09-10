# Próximo prompt completo

Leia integralmente AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md.
Releia lessons.md junto do backlog e depois de recuperar contexto. Leia também
os relatórios em docs/environment.md, docs/phase-0-verification.md,
docs/research-notes.md e docs/dependency-licenses.md.

A Phase 0 está validada em Windows nativo/Python 3.12 CPU. Audite Git e ambiente
antes de editar; crie uma branch dedicada a partir de main. Preserve trabalho local.
Windows é primário para desenvolver, testar, executar e futuramente gerar charts.
Linux/WSL é apenas portabilidade futura. Não instale WSL, use docker-desktop,
introduza Docker ou modifique políticas administrativas. CUDA é opcional.

Faça somente a auditoria de compatibilidade pré-Phase 1 para este Windows 10,
Python 3.12.0, 4 CPUs lógicas, 15.9 GiB RAM e Intel HD Graphics 630 sem NVIDIA.
Não implemente DCF-100 em diante nesta auditoria. Não execute inferência nem baixe
modelos. Investigue ffmpeg, PyTorch CPU, ADTOF-pytorch, separação, transitivas e
checkpoints por fontes primárias, metadados e manifests.

Para cada componente registre suporte Windows/Python 3.12, wheel compatível,
compilação necessária, requisitos ffmpeg/CUDA, tamanho e licenças código/pesos.
Distinga evidência documental, resolução de pacotes e teste real. Não apresente
wheel disponível como inferência validada. Recomende a menor configuração
Windows CPU para áudio -> transcrição de bateria -> MIDI, explicitando bloqueios.

A API ADTOF inspecionada pode continuar sem carregar pesos ausentes. Documente
isso: um futuro adaptador deve rejeitar checkpoint ausente/incompatível. Não
infira licença dos pesos a partir do wrapper. Não trate WSL como solução.

Atualize documentos, backlog e lessons.md com evidências. Execute gates aplicáveis
em docs/testing.md, revise artefatos e ausência de áudio/pesos rastreados, faça
commit na branch e merge --no-ff em main. Verifique árvore limpa e informe hashes.
Entregue a matriz de compatibilidade, recomendação mínima, limites e próximo
prompt completo. Aguarde nova instrução antes de iniciar DCF-100.
