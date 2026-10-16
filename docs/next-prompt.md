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

Continue a Phase 1 a partir de DCF-113–114 e DCF-116–122. DCF-100–112 e DCF-115 já
implementam o preparo, interfaces e transcrição ADTOF, mas o fluxo ainda
deve ser exercitado com FFmpeg e áudio privado no Windows nativo. Use a
decisão de `docs/phase-1-windows-compatibility.md`: FFmpeg nativo como boundary de
normalização, PyTorch CPU e ADTOF `85c192e`, sem separação inicialmente.

Faça primeiro a validação nativa com áudio privado e gere contagens/CSV de debug.
Use a skill local `.agents/skills/drum-audio-diagnostics/SKILL.md` para investigar
chimbal ausente e comparar um trecho de 15–30 s da mixagem com stems locais de
bateria/chimbal, quando fornecidos. Veja docs/drum-audio-diagnostics.md. O CLI
mantém `--thresholds BD SD HH TT CY`; o adaptador agora traduz para a ordem
upstream BD SD TT HH CY. Terceiro valor público = chimbal. Reavalie vetores
explícitos antigos ajustados antes da correção. Preserve a mixagem de referência,
varie só HH e meça TP/FP/FN e erro de tempo por classe; não suponha que a separação
melhore tudo. O script espectral produz candidatos, não classes reconhecidas.
Não faça upload ao Moises nem baixe modelos sem autorização específica; stems
exportados pelo usuário podem ser preparados/transcritos no fluxo atual.
Mantenha separação desativada no baseline por meio do passthrough existente e
`--skip-separation`. Não instale WSL/Docker/CUDA e não torne
separação um requisito. Mantenha dependências ML opcionais e travadas.

A API ADTOF upstream pode continuar sem carregar pesos ausentes; o adaptador local
já rejeita checkpoint ausente/incompatível, valida o SHA256 e força CPU. Não
infira licença dos pesos a partir do wrapper. Não trate WSL como solução.

Atualize documentos, backlog e lessons.md com evidências. Execute gates aplicáveis
em docs/testing.md, revise artefatos e ausência de áudio/pesos rastreados, faça
commit na branch e merge --no-ff em main. Verifique árvore limpa e informe hashes.
Entregue apenas os DCFs realmente concluídos, medições e o próximo menor passo.
