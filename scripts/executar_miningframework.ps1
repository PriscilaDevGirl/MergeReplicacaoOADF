param(
    [string]$RunName = ('piloto-' + (Get-Date -Format 'yyyyMMdd-HHmmss')),
    [string]$RuntimeRoot = 'C:\Users\Public\codex-merge-pilot'
)
$ErrorActionPreference = 'Stop'
if ($RunName -notmatch '^[a-zA-Z0-9_-]+$') { throw 'RunName deve conter apenas letras, numeros, _ ou -.' }
$taskWorkspace = Split-Path -Parent $PSScriptRoot
$taskFramework = Join-Path $RuntimeRoot 'miningframework'
$taskGradle = Join-Path $RuntimeRoot 'gradle-runtime\bin\gradle.bat'
$taskOutput = Join-Path $taskFramework ('output-' + $RunName)
$taskInput = Join-Path $taskFramework ('input-' + $RunName)
$taskLocalOutput = Join-Path $taskWorkspace ('resultados\miningframework\' + $RunName)
if (!(Test-Path -LiteralPath $taskGradle)) { throw 'Runtime oficial ainda nao provisionado.' }
if ((Test-Path -LiteralPath $taskOutput) -or (Test-Path -LiteralPath $taskInput) -or (Test-Path -LiteralPath $taskLocalOutput)) {
    throw 'Nome de execucao ja utilizado. Escolha outro RunName.'
}
# Um alias novo impede que o framework remova/reclone uma copia de execucao anterior.
$taskProjectName = 'underscore_' + $RunName
$taskClone = [System.IO.Path]::GetFullPath((Join-Path $taskFramework ('clonedRepositories\' + $taskProjectName)))
$taskCloneRoot = [System.IO.Path]::GetFullPath((Join-Path $taskFramework 'clonedRepositories')) + '\'
if (!$taskClone.StartsWith($taskCloneRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destino de clone invalido.' }
if (Test-Path -LiteralPath $taskClone) { throw 'Destino de clone ja existe; escolha outro RunName.' }
New-Item -ItemType Directory -Path $taskInput | Out-Null
New-Item -ItemType Directory -Path $taskLocalOutput | Out-Null
$taskProjects = "path,name`nhttps://github.com/jashkenas/underscore,$taskProjectName`n"
[System.IO.File]::WriteAllText((Join-Path $taskInput 'projects.csv'), $taskProjects)
$taskCommits = Import-Csv -LiteralPath (Join-Path $taskWorkspace 'experimentos\miningframework\commits_piloto.csv')
foreach ($taskRow in $taskCommits) { $taskRow.project = $taskProjectName }
$taskCommits | Export-Csv -LiteralPath (Join-Path $taskInput 'commits.csv') -NoTypeInformation -Encoding utf8
$taskOldEnv = @{}
foreach ($taskKey in @('GRADLE_USER_HOME','JAVA_HOME','TEMP','TMP','JAVA_OPTS','PATH')) {
    $taskOldEnv[$taskKey] = [Environment]::GetEnvironmentVariable($taskKey, 'Process')
}
$taskCode = 1
try {
    $env:GRADLE_USER_HOME = Join-Path $RuntimeRoot 'gradle-cache'
    $env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.8.9-hotspot'
    $env:TEMP = Join-Path $RuntimeRoot 'tmp'
    $env:TMP = $env:TEMP
    $env:JAVA_OPTS = '-Djava.io.tmpdir=' + $env:TEMP.Replace('\','/')
    $env:PATH = 'C:\Program Files\Git\usr\bin;' + $env:PATH
    $taskJvm = '-Dorg.gradle.jvmargs=-Djava.io.tmpdir=' + $env:TEMP.Replace('\','/')
    $taskArgs = '--args=--injector injectors.DynamicAnalysisJsModifiedLinesDetectionModule --extension .js --keep-projects --max-commits-per-project 5 --random-seed 1 --project-commit-hashes-file input-' + $RunName + '/commits.csv input-' + $RunName + '/projects.csv output-' + $RunName
    Push-Location $taskFramework
    try {
        & $taskGradle --no-daemon --console=plain $taskJvm run $taskArgs 2>&1 | Tee-Object -FilePath (Join-Path $taskLocalOutput 'framework.log')
        $taskCode = $LASTEXITCODE
    } finally { Pop-Location }
    if ($taskCode -ne 0) { throw "Gradle terminou com codigo $taskCode" }
    if (!(Test-Path -LiteralPath (Join-Path $taskOutput 'data\results.csv'))) { throw 'Coletor nao gerou results.csv.' }
    Copy-Item -LiteralPath $taskOutput -Destination (Join-Path $taskLocalOutput 'saida_oficial') -Recurse
    Write-Output ('Resultados em ' + $taskLocalOutput)
} finally {
    foreach ($taskKey in $taskOldEnv.Keys) {
        [Environment]::SetEnvironmentVariable($taskKey, $taskOldEnv[$taskKey], 'Process')
    }
}
