# Przygotowanie piaskownicy do zrzutów VS Code (wywoływane jako zadanie przez piaskownica.py).
# 1. Python 3.14 w układzie Python Install Managera: %LOCALAPPDATA%\Python\pythoncore-3.14-64,
#    wpis PEP 514 w HKCU i katalog w PATH użytkownika (wszystko wewnątrz piaskownicy).
#    Python Install Manager (pakiet MSIX z python.org), kompilacja free-threaded 3.14t w tej samej
#    wersji co 3.14 (py install) i środowisko .venv-t projektu C:\projekty\moj-projekt (venv.md).
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
$PyT = Join-Path $Local 'Python\pythoncore-3.14t-64'
$PyVersion = '3.14.8'
$PymVersion = '26.4'
$Projekt = 'C:\projekty\moj-projekt'

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

# Python Install Manager: w piaskownicy nie ma Microsoft Store, więc pakiet MSIX z python.org;
# pobrany plik zostaje w katalogu wymiany i służy kolejnym przebiegom
if (-not (Get-AppxPackage PythonSoftwareFoundation.PythonManager)) {
    $msix = Join-Path $Root "python\python-manager-$PymVersion.msix"
    if (-not (Test-Path $msix)) {
        Krok "python-manager-$PymVersion.msix"
        Invoke-WebRequest "https://www.python.org/ftp/python/pymanager/python-manager-$PymVersion.msix" -OutFile $msix -UseBasicParsing
    }
    Krok "Python Install Manager $PymVersion"
    Add-AppxPackage $msix
}
$PyMgr = Join-Path $Local 'Microsoft\WindowsApps\py.exe'
for ($i = 0; -not (Test-Path $PyMgr) -and $i -lt 30; $i++) { Start-Sleep -Seconds 1 }
if (-not (Test-Path $PyMgr)) { throw "brak polecenia py: $PyMgr" }

# Kompilacja free-threaded 3.14t. Archiwum z pamięci podręcznej managera na hoście (kopiuje je
# piaskownica.py przygotuj) trafia do pamięci podręcznej managera w piaskownicy: manager sprawdza
# jego skrót SHA-256 z indeksu python.org i nie pobiera go ponownie. Książka podaje py install 3.14t
# (najnowsze wydanie 3.14t); dokładny znacznik 3.14.8t zachowuje wersję 3.14 także po kolejnych wydaniach.
if (-not (Test-Path "$PyT\python3.14t.exe")) {
    Krok "Python $PyVersion (free-threaded) -> $PyT"
    $Cache = Join-Path $Local 'Python\_cache'
    $zipT = "pythoncore-3.14t-64-$PyVersion.zip"
    if ((Test-Path "$Root\python\$zipT") -and -not (Test-Path "$Cache\$zipT")) {
        if (-not (Test-Path $Cache)) { New-Item -ItemType Directory $Cache | Out-Null }
        Copy-Item "$Root\python\$zipT" $Cache
    }
    & $PyMgr install --yes "$($PyVersion)t"
    if ($LASTEXITCODE -ne 0) { throw "py install: $LASTEXITCODE" }
}
& $PyMgr list
& $PyMgr -V:3.14t -VV

# Środowisko .venv-t projektu moj-projekt: polecenie z venv.md (.venv tworzy vsc_zrzuty.py projekty)
if (-not (Test-Path $Projekt)) { New-Item -ItemType Directory -Force $Projekt | Out-Null }
Push-Location $Projekt
if (-not (Test-Path .venv-t)) { Krok '.venv-t'; & $PyMgr -V:3.14t -m venv .venv-t }
Pop-Location
if (-not (Test-Path "$Projekt\.venv-t\Scripts\python.exe")) { throw "brak środowiska $Projekt\.venv-t" }
& "$Projekt\.venv-t\Scripts\python.exe" -VV

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
