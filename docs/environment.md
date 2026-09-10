# Current environment and portability audit

Native Windows is the primary environment for this stage, including development,
execution, testing and future chart generation. CPU is the minimum requirement;
CUDA/GPU is optional acceleration. Linux/WSL should remain supportable in the
future but cannot be required. No WSL installation, docker-desktop usage, Docker
workaround or changes to administrative policies on this college PC.

## Validated host

Windows 10; PowerShell 7.4.13; Python 3.12.0 x64; uv 0.12.13; VS Code;
4 logical CPUs; 15.9 GiB RAM; Intel HD Graphics 630; no NVIDIA/CUDA.
Existing WSL contains only docker-desktop and is not used. This update relies on
the user's verified hardware inventory and rechecks the native runtime and gates.

Run in PowerShell from the repository root:

```powershell
.\.tools\bin\uv.exe --cache-dir .uv-cache sync --locked
.\.tools\bin\uv.exe --cache-dir .uv-cache run --locked drumforge doctor
.\.tools\bin\uv.exe --cache-dir .uv-cache run --locked drumforge doctor --json
```

Use `--write-dir 'C:\path with spaces\output'` for an existing writable directory.
No virtualenv activation script or system-wide PATH modification is required.
The installed uv can be used as `uv` when it is already on PATH.

## Code audit (2026-09-10)

Scope: every Python file in src/ and tests/, project config, README, kickoff and docs.

| Pattern inspected | Finding and disposition |
| --- | --- |
| Slash paths | Runtime paths use pathlib.Path and tempfile. Test path C:/Program Files/... deliberately exercises Windows spaces. Markdown links and Hatch include patterns use portable forward slashes, not Linux filesystem assumptions. |
| Bash / chmod | No runtime Bash, chmod or shell activation requirement. Kickoff's conceptual CLI example is converted to a PowerShell-compatible single line. |
| Symlinks | No symlink creation or privilege requirement in project code. Future cache/export implementations must support ordinary files on Windows. |
| /tmp, /usr, /bin | No hardcoded Unix runtime paths. Temporary write probe uses tempfile in the requested Path directory and cleans up. |
| shell=True | Absent. subprocess.run receives argument lists with bounded timeouts. |
| Executable extension | Python subprocess uses sys.executable. shutil.which('ffmpeg') resolves ffmpeg.exe using Windows PATHEXT; the resolved full path is passed as one argument. Tested with a path containing spaces. |
| Linux PATH | No Linux-specific PATH value; optional ffmpeg absence is a warning. Local uv.exe instructions are explicit. |
| OS APIs | Windows RAM uses GlobalMemoryStatusEx; sysconf is confined to the non-Windows path with an unavailable fallback. WSL detection checks Linux kernel/environment metadata without invoking wsl.exe. |
| GPU | No CUDA requirement or Intel-as-CUDA assumption. doctor separately reports native Windows/Linux/WSL, CPU, PyTorch and CUDA. |

CUDA has status ok when unavailable because it is optional. If PyTorch cannot be
probed, doctor says CUDA is unavailable to that runtime and hardware is unverified;
it does not infer physical GPU absence. OS tests simulate Linux/WSL classification;
they do not claim this release was exercised on those operating systems.

## Phase 1 constraint

Before DCF-100, audit native wheels, source requirements, codecs and weight terms.
Do not install heavyweight backends or start inference as part of the compatibility
investigation. No model download is needed to inspect indexes and manifests.
