# Dois pedais e Nightmare 2x

A preferência permanente do usuário é **priorizar charts de dois pedais**:
Expert+ / 2x Kick ou edições explicitamente chartadas com bumbo duplo completo.
Conferimos as notas do arquivo e a indicação do autor. Pro Drums sozinho não
comprova dois pedais; quando não houver uma versão confirmada, a limitação deve
ficar explícita. Não acrescentamos bumbos inventados nem mudamos a música original.

## A Nightmare que você já tem

A versão de ImPhanty no **lote 06 já contém dois pedais**: 893 bumbos básicos e
471 extras de Expert+, totalizando 1.364 notas de bumbo. Em **Pro Drums / Expert**,
ative **Modifiers → 2x Kick** para incluir essas notas extras. A
[documentação do Clone Hero](https://wiki.clonehero.net/books/clone-hero-manual/page/song-modifiers)
confirma esse modificador; o [FAQ de bateria](https://wiki.clonehero.net/books/guitars-drums-controllers/page/drum-faqs-and-troubleshooting)
explica que Expert+ é habilitado por ele.

## Outra edição, conferida

Foi preparada também a [publicação 2x Bass Pedal / Expert+ de UriasP](https://rhythmverse.co/songfile/65648a0a2a394727890178908126c9be),
com chart creditado a **Harmonix**. O arquivo tem 916 bumbos básicos e **454 extras**
em MIDI 95: **1.370 bumbos com 2x Kick**. Há 2.493 notas básicas de bateria e 2.947
incluindo os bumbos extras. Pratos/tons e sete áudios passaram pela inspeção.
As duas edições têm chart e áudio próprios; não misture seus arquivos.

Essa alternativa é uma **troca opcional**, disponível separadamente dos lotes
gerais. Os 675 charts da seleção padrão e suas receitas permanecem intactos.
O título original dentro do jogo continua sendo Nightmare; a pasta nova identifica
2x Kick e o autor aparece nos metadados. A contagem não comprova precisão acústica,
melhor sincronismo ou preferência musical sobre o chart anterior.

## Baixar a alternativa no Windows

Precisa de Python 3.11+ em Windows 10/11 x64 e **2 GB livres**. O original tem
402 MB porque também inclui um vídeo de fundo; as dez peças entregues somam
54 MB e o ZIP, 54 MB. O vídeo é preservado no pacote original, fora da pasta
preparada para o jogo. O leitor oficial portátil 7-Zip é baixado e conferido;
seu instalador é lido como arquivo, sem execução nem permissão administrativa.
Este pacote é nativo e dispensa conversão Onyx.

Espere um baixador anterior terminar antes de executar. Cole o bloco inteiro no
PowerShell; altere `$pasta` somente se quiser outro destino de download.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $codigo = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/e6251a31a1e33658a152479664b84fa190667e65/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\Nightmare-2x'
    $baixador = Join-Path $pasta 'Baixador'
    $verificados = @{
        'recover_pilot.py' = '17ce979cdb2df4c8829130ba8bb027909875f644fa6be7a58347b564711d674a'
        'sevenzip.py' = '822d12334b2ab821e3dfec5fcf38d99ce1dfc610c80cfae49170f8b83095da3a'
        'nightmare_2x.json' = '911067fefd52499033138374531ccc2b6a57700b79b606bfb10a3e2d7d0e3894'
    }
    New-Item -ItemType Directory -Path $baixador -Force | Out-Null
    foreach ($arquivo in $verificados.Keys) {
        $origem = if ($arquivo -eq 'nightmare_2x.json') { $base } else { $codigo }
        $local = Join-Path $baixador $arquivo
        Invoke-WebRequest -Uri "$origem/$arquivo" -OutFile $local -UseBasicParsing
        if ((Get-FileHash -LiteralPath $local -Algorithm SHA256).Hash.ToLowerInvariant() -ne $verificados[$arquivo]) {
            throw "Arquivo diferente do verificado: $arquivo"
        }
    }
    @'
import hashlib
import sys
from pathlib import Path

metadata = Path(sys.argv[1]).resolve()
root = Path(sys.argv[2]).resolve()
pins = {
    "recover_pilot.py": "17ce979cdb2df4c8829130ba8bb027909875f644fa6be7a58347b564711d674a",
    "sevenzip.py": "822d12334b2ab821e3dfec5fcf38d99ce1dfc610c80cfae49170f8b83095da3a",
    "nightmare_2x.json": "911067fefd52499033138374531ccc2b6a57700b79b606bfb10a3e2d7d0e3894",
}
try:
    for name, expected in pins.items():
        if hashlib.sha256((metadata / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Arquivo diferente do verificado: " + name)
    sys.path.insert(0, str(metadata))
    from recover_pilot import read_manifest, recover
    manifest = read_manifest(metadata / "nightmare_2x.json", pins["nightmare_2x.json"])
    target = recover(manifest, root)
    print("Concluido! ZIP:", target)
except KeyboardInterrupt:
    print("Interrompido. Execute novamente para retomar; arquivos preservados.")
    sys.exit(130)
except Exception as error:
    print("Falha:", error, "Execute novamente para retomar; arquivos existentes preservados.")
    sys.exit(1)
'@ | py -3 -I -S - $baixador $pasta
    if ($LASTEXITCODE -ne 0) { throw 'Download pendente ou interrompido. Leia a mensagem e execute novamente para retomar.' }
    Write-Host "Pasta pronta em $(Join-Path $pasta 'Songs')"
}
```

O comando verifica programa, receita, leitor, original e arquivos preparados;
retoma arquivos íntegros e preserva edições locais. Os programas estão fixados a
uma revisão publicada, sem depender de futuras atualizações do índice geral.
O link da fonte pode ser removido ou atingir cotas; nesses casos a falha é explícita.

## Substituir a música no jogo

1. Mova somente a cópia antiga de Nightmare da sua biblioteca para um backup
   **fora de todas as pastas escaneadas** pelo Clone Hero.
2. Copie a pasta `Avenged Sevenfold - Nightmare - 2x Kick [65648a0a]`, de dentro de
   `Songs\MixDrumRock - Nightmare 2x`, para a sua Songs configurada. Instale uma vez:
   copiar a pasta e também extrair o ZIP no mesmo acervo cria duas cópias.
3. Execute **Scan Songs** e selecione **Pro Drums / Expert**, com
   **Modifiers → 2x Kick** ativado.

O comando prepara o download; ele não move, apaga ou instala arquivos na sua Songs.
Como esta é outra chart da mesma música, o comparador de músicas ausentes pode
marcá-la como já presente. Use a troca acima, em vez de esperar que apareça no ZIP
das ausentes. Se copiar todos os lotes novamente, confira Nightmare para não
reinstalar também a versão antiga. Guarde notas e áudio de cada edição juntos.

A inspeção e a reconstrução foram feitas em Linux/Python 3.12. A execução nativa
no Windows, Scan Songs e teste com seus pedais continuam pendentes.

## Próxima sessão

```text
No projeto clone-hero-chart-midi, leia AGENTS.md, CODEX_KICKOFF.md, CONTEXT.md,
BACKLOG.md, lessons.md e a skill .agents/skills/drum-audio-diagnostics/SKILL.md.
Leia song-library/DOIS-PEDAIS.md. Priorize dois pedais em toda nova curadoria:
verifique Expert+/2x Kick ou autoria explícita de bumbo duplo completo e preserve
notas/áudio. Nightmare do lote 06 já tem 471 kicks opcionais; a receita opcional
nightmare_2x.json entrega outra edição com 454 extras, fora do índice de lotes.
Use Modifiers > 2x Kick. Não reescreva receitas antigas, as correções do Onyx ou
experimentos de áudio. Evite instalar as duas Nightmare ao orientar uma troca.
Peça o resultado do teste no jogo antes de afirmar compatibilidade ou sincronismo.
```
