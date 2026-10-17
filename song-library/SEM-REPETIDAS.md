# Juntar os lotes às músicas antigas

A comparação e o ZIP são feitos no seu PC. Não precisa enviar os 4 GB, nem
instalar dependências além do Python já usado pelo baixador.

**Complemento-antigas.zip** contém as músicas antigas selecionadas como ausentes
dos lotes presentes no disco. Os lotes têm prioridade. O programa não apaga,
move, renomeia nem edita a biblioteca atual ou os downloads.

## Executar no Windows

Espere o baixador terminar. O comando usa `Documentos\Clone Hero\Songs`, conforme
sua captura, e `Downloads\MixDrumRock\Songs`. Documentos é localizado pelo caminho
oficial do Windows, inclusive quando redirecionado ao OneDrive. Se suas pastas
forem diferentes, altere `$antigas` ou `$novas`.

Cole no PowerShell:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $mix = Join-Path $env:USERPROFILE 'Downloads\MixDrumRock'
    $ferramenta = Join-Path $mix 'Comparador'
    New-Item -ItemType Directory -Path $ferramenta -Force | Out-Null
    foreach ($arquivo in @('complement.py', 'local_library.py')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $ferramenta $arquivo) -UseBasicParsing
    }
    $antigas = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Clone Hero\Songs'
    $novas = Join-Path $mix 'Songs'
    $saida = Join-Path $mix ('Complemento-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    py -3 (Join-Path $ferramenta 'complement.py') --antigas $antigas --novas $novas --destino $saida
    if ($LASTEXITCODE -ne 0) { throw 'A comparacao nao concluiu. Confira a mensagem acima.' }
    Invoke-Item $saida
}
```

A pasta do resultado abre no Explorador. Contém:

- **Complemento-antigas.zip:** músicas antigas selecionadas para acrescentar aos lotes.
- **comparacao.csv:** uma linha por pasta antiga, com decisão e correspondente.
- **avisos.csv:** compactados/links/pastas temporárias ignorados e novas incompletas.
- **resumo.json / LEIA-ME.txt:** contagens e instruções.

O ZIP usa ZIP64, incluindo suporte a mais de 4 GB. Áudios já comprimidos são
armazenados sem nova compressão. Reserve aproximadamente o tamanho das músicas
selecionadas, mais 64 MiB; o programa confere o espaço e lê os arquivos em blocos.
Não cria uma segunda cópia inteira antes do ZIP. Ler vários GB pode demorar em HD
ou OneDrive; o terminal mostra o andamento.

## Montar a biblioteca

1. Crie uma pasta vazia, por exemplo `Downloads\Clone Hero - Biblioteca nova`.
2. Copie para ela as pastas de `Downloads\MixDrumRock\Songs`, incluindo o piloto
   se estiver ali.
3. Extraia nela a pasta `Complemento-antigas` do ZIP gerado.
4. Confira os itens `revisar` no CSV antes de acrescentar versões incertas.
5. Aponte o Clone Hero para essa biblioteca nova, faça **Scan Songs** e teste.
   Mantenha a antiga como backup; deixe somente a biblioteca escolhida configurada
   para o jogo não escanear as duas cópias ao mesmo tempo.

Acrescentar esses arquivos por cima da pasta antiga mantém as cópias renomeadas
que já estavam lá. Por isso a montagem usa uma pasta vazia; o comparador não
remove arquivos da biblioteca atual.

## Como decide

A comparação lê `song.ini`, sem depender do nome das pastas, inclusive em packs
e discografias. Aceita UTF-8/CP1252/UTF-16 e normaliza caixa, acentos, pontuação
e marcações de cor. Também compara SHA256 da chart e de todos os áudios: conteúdo
idêntico pode ser reconhecido mesmo com textos do INI alterados.

| Estado no CSV | Resultado |
| --- | --- |
| `adicionar` | Entra no ZIP; nenhuma sobreposição identificada. |
| `ja_nos_lotes` | Fica fora do ZIP; mantém a versão dos lotes novos. |
| `repetida_antiga` | Fica fora do ZIP; outra antiga selecionada representa a música. |
| `revisar` | Continua no original, fora do ZIP, aguardando comparação manual. |

Mesmo artista/título conta como a mesma música mesmo com chart/autor diferente:
a prioridade é dos lotes. Entre antigas equivalentes, mantém a primeira pasta em
ordem de caminho e lista as outras; isso não avalia qualidade musical. Somente o
nome ou o MIDI não provam uma cópia de conteúdo: o SHA exige chart e áudios juntos.

Diferenças de duração acima de oito segundos, indícios de live/demo/acústica/remix
no título/álbum, remaster ou metadados ausentes levam à revisão quando há uma
correspondência possível. Títulos explicitamente diferentes, como `(Live)`, podem
permanecer separados. Se artista/título também foram reescritos ou estão errados,
a deduplicação pode precisar de revisão. Envie somente **comparacao.csv e
avisos.csv** no chat para isso; não precisa enviar mídia ao GitHub.

Somente pastas novas com INI, chart e áudio não vazios servem de referência.
Download incompleto não faz a antiga ser omitida. Após baixar mais lotes, execute
novamente para um destino novo. Compactados `.zip`, `.rar`, `.7z` e `.sng` não são
abertos nem copiados: use as pastas extraídas. O `Songs.rar` mostrado será ignorado.

O ZIP preserva arquivos de jogo, áudio, imagens, vídeo e créditos das músicas
selecionadas. Backups compactados ficam fora. Links/junções não são seguidos.
Cada arquivo é conferido pelo SHA256 inicial e dentro do ZIP; alterações durante
a execução descartam o ZIP incompleto. Resultados anteriores não são sobrescritos.
Esses checks não medem qualidade, sincronismo ou aceitação no jogo.
