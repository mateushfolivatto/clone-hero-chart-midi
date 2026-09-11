# Próximo prompt completo

Leia integralmente AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md.
Releia lessons.md junto do backlog e depois de recuperar contexto. Leia também
os relatórios em docs/environment.md, docs/phase-0-verification.md,
docs/research-notes.md e docs/dependency-licenses.md.

A Phase 0 e a auditoria de compatibilidade pré-Phase 1 estão concluídas em
Windows nativo/Python 3.12 CPU. Audite Git e ambiente
antes de editar; crie uma branch dedicada a partir de main. Preserve trabalho local.
Windows é primário para desenvolver, testar, executar e futuramente gerar charts.
Linux/WSL é apenas portabilidade futura. Não instale WSL, use docker-desktop,
introduza Docker ou modifique políticas administrativas. CUDA é opcional.

Após nova autorização explícita do usuário, implemente somente o menor primeiro
recorte de Phase 1 (começando em DCF-100), neste Windows 10/Python 3.12 CPU. Use a
decisão de `docs/phase-1-windows-compatibility.md`: FFmpeg nativo como boundary de
normalização, PyTorch CPU e ADTOF `85c192e`, sem separação inicialmente.

Faça primeiro o menor slice testável de probe/cópia/normalização, preservando o
original e usando `pathlib.Path`, `ffmpeg.exe` resolvido explicitamente, argumentos
de subprocesso e `shell=False`. Não instale WSL/Docker/CUDA e não torne separação
um requisito. Mantenha dependências ML opcionais e travadas.

A API ADTOF pode continuar sem carregar pesos ausentes. O adaptador deve rejeitar
checkpoint ausente/incompatível, validar o SHA256 registrado e forçar CPU. Não
infira licença dos pesos a partir do wrapper. Não trate WSL como solução.

Atualize documentos, backlog e lessons.md com evidências. Execute gates aplicáveis
em docs/testing.md, revise artefatos e ausência de áudio/pesos rastreados, faça
commit na branch e merge --no-ff em main. Verifique árvore limpa e informe hashes.
Entregue apenas os DCFs realmente concluídos, medições e o próximo menor passo.
