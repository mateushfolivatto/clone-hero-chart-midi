# Próximo prompt completo

Leia integralmente AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md, BACKLOG.md e lessons.md.
Releia lessons.md junto do backlog e depois de recuperar contexto. Leia também
os relatórios em docs/environment.md, docs/phase-0-verification.md,
docs/research-notes.md e docs/dependency-licenses.md.

A Phase 0 e a auditoria de compatibilidade pré-Phase 1 estão concluídas em
Windows nativo/Python 3.12 CPU. Audite Git e ambiente
antes de editar. A continuação da Phase 1 está na branch
`feat/raw-midi-diagnostics`: preserve e continue nela para a mesma unidade de
trabalho. Crie outra branch a partir de main somente para uma nova unidade.
Preserve trabalho local.
Windows é primário para desenvolver, testar, executar e futuramente gerar charts.
Linux/WSL é apenas portabilidade futura. Não instale WSL, use docker-desktop,
introduza Docker ou modifique políticas administrativas. CUDA é opcional.

Continue a Phase 1 a partir de DCF-113–114 e DCF-116/117/120–122.
DCF-100–104/107/109–112/115 já
implementam o preparo, interfaces e transcrição ADTOF, mas o fluxo ainda
deve ser exercitado com FFmpeg e áudio privado no Windows nativo. Use a
decisão de `docs/phase-1-windows-compatibility.md`: FFmpeg nativo como boundary de
normalização, PyTorch CPU e ADTOF `85c192e`, sem separação inicialmente.

DCF-118/119 agora têm implementação e evidência sintética no comando
`drumforge inspect-midi 'work/raw.mid' --out 'output/diagnostico-midi'`. Leia
docs/phase-1-midi-diagnostics.md. Mido 1.3.3 está no grupo dev e no extra opcional
diagnostics, fixado no uv.lock; `uv sync --locked --extra diagnostics` prepara
o parser. O comando preserva tempos, velocidades MIDI e notas simultâneas e gera
report.json/events.csv em pasta nova. Ele espera percussão GM no canal 10, não um
chart PART DRUMS existente. Não trate velocidade armazenada como dinâmica acústica
estimada ou confiança; DCF-113/114 permanecem abertos.

Faça primeiro a validação nativa com áudio privado e aplique as contagens/CSV à
música real. Se os arquivos/ambiente não estiverem disponíveis, registre o bloqueio
e não alegue inferência ou qualidade real. Esta cópia da nuvem não tem o áudio de
Turn to Ashes, checkpoint ou ambiente ADTOF. Os 104 testes e a demonstração de
22 ataques foram sintéticos; a Phase 1 continua em andamento.

Use sempre a skill local `.agents/skills/drum-audio-diagnostics/SKILL.md` em toda
tarefa de música para chart, conforme solicitado pelo usuário e registrado em
AGENTS.md. Aplique também seu procedimento para investigar
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
commit na branch. AGENTS.md exige manter uma fase incompleta na branch; a Phase 1
ainda depende da validação privada. Quando os critérios estiverem satisfeitos,
faça merge --no-ff em main, verifique árvore limpa e informe hashes.
Tente push de main para origin após o merge e verifique sincronização; se falhar,
preserve os commits e registre o erro real. Entregue apenas os DCFs realmente
concluídos, medições e o próximo menor passo. Não avance a Phase 2/3 antes de
verificar os critérios de aceitação da fase atual.
