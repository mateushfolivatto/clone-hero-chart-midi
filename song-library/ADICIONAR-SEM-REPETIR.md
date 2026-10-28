# Acrescentar músicas sem repetir as instaladas

O comparador roda no seu PC e lê tanto os lotes candidatos quanto a biblioteca
que o Clone Hero já usa. Ele gera `Novas-musicas.zip` apenas com as músicas
selecionadas como ausentes. As pastas existentes e os downloads são preservados.
Não exige upload de áudio, login nem dependências além de Python 3.11+.

Esse fluxo ajuda a evitar o problema observado no relatório de varredura:
charts duplicados em pastas renomeadas e em uma cópia do complemento dentro dele
mesmo. Renomear pastas não altera a identidade do chart.

## Executar depois de terminar os downloads

O exemplo usa os novos lotes em `Downloads\LinkinPark\Songs` e a biblioteca em
`Documentos\Clone Hero\Songs`. Ajuste `$candidatas` ou `$biblioteca` se o caminho
configurado no jogo for outro. Documentos é localizado pelo Windows, inclusive
quando redirecionado ao OneDrive.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $base = 'https://raw.githubusercontent.com/mateushfolivatto/clone-hero-chart-midi/main/src/drumforge/library'
    $pasta = Join-Path $env:USERPROFILE 'Downloads\LinkinPark'
    $ferramenta = Join-Path $pasta 'Comparador'
    New-Item -ItemType Directory -Path $ferramenta -Force | Out-Null
    Invoke-WebRequest -Uri "$base/collection_index.json" -OutFile (Join-Path $ferramenta 'collection_index.json') -UseBasicParsing
    $indice = Get-Content -LiteralPath (Join-Path $ferramenta 'collection_index.json') -Raw | ConvertFrom-Json
    foreach ($arquivo in @('additions.py', 'complement.py', 'local_library.py')) {
        Invoke-WebRequest -Uri "$base/$arquivo" -OutFile (Join-Path $ferramenta $arquivo) -UseBasicParsing
        $esperado = $indice.addition_helpers.PSObject.Properties[$arquivo].Value
        if ($esperado -notmatch '^[a-f0-9]{64}$' -or (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $ferramenta $arquivo)).Hash -ne $esperado) {
            throw 'Versoes do comparador diferentes do indice. Execute novamente para atualizar.'
        }
    }
    $candidatas = Join-Path $pasta 'Songs'
    $biblioteca = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Clone Hero\Songs'
    $saida = Join-Path $pasta ('Para-adicionar-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    py -3 (Join-Path $ferramenta 'additions.py') --candidatas $candidatas --biblioteca $biblioteca --destino $saida
    if ($LASTEXITCODE -ne 0) { throw 'A comparacao nao concluiu. Confira a mensagem acima.' }
    Invoke-Item $saida
}
```

Abra `comparacao.csv` para conferir a seleção. Se houver músicas em `adicionar`,
extraia a pasta **Novas-musicas** do ZIP diretamente em **Songs**, uma única vez,
e execute **Scan Songs**. Downloads, ZIPs de origem e backups ficam fora dos
caminhos escaneados pelo jogo. O programa não instala ou apaga pastas da biblioteca.

## Como interpretar a comparação

| Estado | Resultado |
| --- | --- |
| `adicionar` | Incluído no ZIP. |
| `ja_na_biblioteca` | Uma música completa instalada tem prioridade; fica fora. |
| `repetida_candidata` | Outra candidata já representa essa música; fica fora. |
| `revisar` | Versão, duração, metadados ou chart compartilhado exigem revisão; fica fora. |

O comparador usa artista/título do INI e hashes, independentemente do nome da
pasta. Mesmo artista/título pode ser omitido mesmo quando o autor/chart difere;
isso preserva a escolha instalada. Edições explicitamente diferentes, como
ao vivo e demo, podem permanecer separadas. Chart idêntico com áudio/metadados
diferentes fica para revisão. Referências incompletas não escondem uma candidata
completa e aparecem em `avisos.csv`.

Rótulos de formato, como `(RB3 Version)` e `(2x Bass Pedal)`, também podem levar
uma correspondência à revisão. Uma fonte nova com outro autor ou nome de pasta
não deve criar automaticamente outra cópia da música instalada.

Cada execução exige um destino novo e verifica todos os arquivos exportados.
Uma biblioteca vazia é permitida neste fluxo de adições. Se todas as candidatas
já existirem ou precisarem de revisão, o ZIP contém apenas instruções, sem músicas
para instalar. Isso não comprova jogabilidade ou sincronismo: teste no jogo.
