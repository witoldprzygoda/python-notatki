# Petla zadan uruchamiana w piaskownicy jako LogonCommand (patrz piaskownica.py).
# Wykonuje kolejno, w porzadku nazw, skrypty *.ps1 wrzucane przez hosta do katalogu
# jobs\ katalogu wymiany; wyjscie zapisuje w out\<nazwa>.log i out\<nazwa>.err,
# a kod wyjscia w out\<nazwa>.done.
$ErrorActionPreference = 'Continue'
$Root = 'C:\zrzuty-vsc'
$Jobs = Join-Path $Root 'jobs'
$Run = Join-Path $Root 'running'
$Out = Join-Path $Root 'out'
New-Item -ItemType Directory -Force $Jobs, $Run, $Out | Out-Null
Set-Content -Path (Join-Path $Out 'runner.ready') -Value (Get-Date -Format o)
while ($true) {
    $job = Get-ChildItem -Path $Jobs -Filter '*.ps1' -ErrorAction SilentlyContinue |
        Sort-Object Name | Select-Object -First 1
    if (-not $job) {
        Set-Content -Path (Join-Path $Out 'runner.heartbeat') -Value (Get-Date -Format o)
        Start-Sleep -Milliseconds 700
        continue
    }
    $name = $job.BaseName
    $dest = Join-Path $Run $job.Name
    Move-Item -Path $job.FullName -Destination $dest -Force
    $log = Join-Path $Out "$name.log"
    $err = Join-Path $Out "$name.err"
    $p = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $dest) `
        -RedirectStandardOutput $log -RedirectStandardError $err `
        -WindowStyle Hidden -PassThru
    $null = $p.Handle  # bez zapamietanego uchwytu ExitCode bywa pusty po zakonczeniu procesu
    $p.WaitForExit()
    Set-Content -Path (Join-Path $Out "$name.done") -Value $p.ExitCode
}
