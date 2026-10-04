# Przygotowanie piaskownicy do zrzutów VS Code (wywoływane jako zadanie przez piaskownica.py).
# 1. Python 3.14 w układzie Python Install Managera: %LOCALAPPDATA%\Python\pythoncore-3.14-64,
#    wpis PEP 514 w HKCU i katalog w PATH użytkownika (wszystko wewnątrz piaskownicy).
# 2. Kopia VS Code z katalogu zmapowanego tylko do odczytu do %LOCALAPPDATA%\Programs.
# 3. Środowisko narzędzi C:\narzedzia\venv z Playwright (tylko sterownik CDP, bez przeglądarek).
# 4. Rozszerzenia VS Code z Marketplace do C:\vsc\ext.
# 'Continue': w PowerShell 5.1 wpis programu zewnętrznego na stderr przy przekierowanym
# strumieniu błędów staje się rekordem błędu; kody wyjścia sprawdzamy jawnie.
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
$Root = 'C:\zrzuty-vsc'
$Local = $env:LOCALAPPDATA
$Py = Join-Path $Local 'Python\pythoncore-3.14-64'
$PyVersion = '3.14.8'

function Krok($tekst) { Write-Output ("[{0:HH:mm:ss}] {1}" -f (Get-Date), $tekst) }

# --- 1. Python ---
if (-not (Test-Path "$Py\python.exe")) {
    Krok "Python $PyVersion -> $Py"
    New-Item -ItemType Directory -Force $Py | Out-Null
    $zip = Get-ChildItem "$Root\python" -Filter "pythoncore-3.14-64-$PyVersion.zip" -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($zip) { $zipPath = $zip.FullName }
    else {
        $zipPath = Join-Path $env:TEMP "python-$PyVersion-amd64.zip"
        Invoke-WebRequest "https://www.python.org/ftp/python/$PyVersion/python-$PyVersion-amd64.zip" -OutFile $zipPath -UseBasicParsing
    }
    tar.exe -xf $zipPath -C $Py
    if ($LASTEXITCODE -ne 0) { throw "tar: $LASTEXITCODE" }
}
$key = 'HKCU:\Software\Python\PythonCore\3.14'
New-Item -Force $key | Out-Null
Set-ItemProperty $key -Name DisplayName -Value "Python $PyVersion"
Set-ItemProperty $key -Name SupportUrl -Value 'https://www.python.org/'
Set-ItemProperty $key -Name SysArchitecture -Value '64bit'
Set-ItemProperty $key -Name SysVersion -Value '3.14'
Set-ItemProperty $key -Name Version -Value $PyVersion
New-Item -Force "$key\InstallPath" | Out-Null
Set-ItemProperty "$key\InstallPath" -Name '(default)' -Value "$Py\"
Set-ItemProperty "$key\InstallPath" -Name ExecutablePath -Value "$Py\python.exe"
Set-ItemProperty "$key\InstallPath" -Name WindowedExecutablePath -Value "$Py\pythonw.exe"
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike "*$Py*") {
    [Environment]::SetEnvironmentVariable('Path', "$Py;$Py\Scripts;$userPath", 'User')
}
& "$Py\python.exe" -VV

# --- 2. VS Code ---
$Code = Join-Path $Local 'Programs\Microsoft VS Code'
if (-not (Test-Path "$Code\Code.exe")) {
    Krok "VS Code -> $Code"
    robocopy 'C:\host\vscode' $Code /E /NFL /NDL /NJH /NJS /NP /R:1 /W:1 | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy: $LASTEXITCODE" }
}
$CodeCli = Join-Path $Code 'bin\code.cmd'
& $CodeCli --version

# --- 3. Narzędzia ---
$Venv = 'C:\narzedzia\venv'
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
    Krok 'venv narzędzi (playwright)'
    & "$Py\python.exe" -m venv $Venv
    & "$Venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q playwright==1.63.0
    if ($LASTEXITCODE -ne 0) { throw "pip: $LASTEXITCODE" }
}
& "$Venv\Scripts\python.exe" -m pip list --disable-pip-version-check

# --- 4. Rozszerzenia ---
$Ext = 'C:\vsc\ext'
$Rozszerzenia = @(
    'ms-python.python', 'ms-python.vscode-pylance', 'ms-python.debugpy', 'ms-python.vscode-python-envs',
    'ms-python.pylint', 'ms-python.mypy-type-checker', 'formulahendry.code-runner', 'ms-toolsai.jupyter'
)
$argsExt = @('--user-data-dir', 'C:\vsc\ud-cli', '--extensions-dir', $Ext)
foreach ($r in $Rozszerzenia) { $argsExt += @('--install-extension', $r) }
Krok 'rozszerzenia'
& $CodeCli @argsExt
& $CodeCli --user-data-dir 'C:\vsc\ud-cli' --extensions-dir $Ext --list-extensions --show-versions
Krok 'gotowe'
