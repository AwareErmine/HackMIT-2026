$ErrorActionPreference = "Stop"

$arduinoRoot = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $arduinoRoot "..")).Path
$distRoot = [System.IO.Path]::GetFullPath((Join-Path $arduinoRoot "dist"))
$outputRoot = [System.IO.Path]::GetFullPath((Join-Path $distRoot "HackMIT"))
$archivePath = [System.IO.Path]::GetFullPath((Join-Path $distRoot "HackMIT.zip"))
$pythonOutput = Join-Path $outputRoot "python"
$backendOutput = Join-Path $pythonOutput "backend"
$backendSource = Join-Path $repoRoot "backend\src\backend"

if (-not $outputRoot.StartsWith($distRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "Refusing to build outside the Arduino dist directory"
}

if (Test-Path -LiteralPath $outputRoot) {
    Remove-Item -LiteralPath $outputRoot -Recurse -Force
}
if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

New-Item -ItemType Directory -Path $backendOutput -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $arduinoRoot "app.yaml") -Destination $outputRoot
Copy-Item -LiteralPath (Join-Path $arduinoRoot "README.md") -Destination $outputRoot
Copy-Item -LiteralPath (Join-Path $arduinoRoot "python\main.py") -Destination $pythonOutput
Copy-Item -LiteralPath (Join-Path $arduinoRoot "python\requirements.txt") -Destination $pythonOutput
Get-ChildItem -LiteralPath $backendSource -Filter "*.py" | Copy-Item -Destination $backendOutput

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::Open(
    $archivePath,
    [System.IO.Compression.ZipArchiveMode]::Create
)
try {
    Get-ChildItem -LiteralPath $outputRoot -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($outputRoot.Length).TrimStart("\", "/")
        $entryName = $relativePath.Replace("\", "/")
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive,
            $_.FullName,
            $entryName,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $archive.Dispose()
}

Write-Output "Arduino App Lab bundle created at $archivePath"
