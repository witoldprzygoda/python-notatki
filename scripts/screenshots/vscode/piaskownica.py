r"""Zrzuty ekranu Visual Studio Code wykonywane w Piaskownicy systemu Windows (strona hosta).

Wszystkie zrzuty VS Code do książki powstają w Piaskownicy systemu Windows (Windows Sandbox),
nie na pulpicie hosta: VS Code, rozszerzenia, Python 3.14 i projekty przykładowe istnieją
tylko w piaskownicy, a na hoście zapisywany jest wyłącznie katalog wymiany. Ten skrypt działa
na hoście (dowolny Python 3.14, sama biblioteka standardowa) i steruje piaskownicą przez
katalog wymiany: wrzuca do niego skrypty zadań, które pętla wsb/runner.ps1 (LogonCommand
piaskownicy) wykonuje po kolei, i czeka na ich wynik.

Użycie (z katalogu głównego repozytorium):
    python scripts/screenshots/vscode/piaskownica.py --katalog <katalog-wymiany> wszystko
    python scripts/screenshots/vscode/piaskownica.py --katalog <katalog-wymiany> kopiuj

Polecenia:
    przygotuj      tworzy katalog wymiany, kopiuje do niego skrypty i archiwa Pythona 3.14 i 3.14t
                   z pamięci podręcznej Python Install Managera, zapisuje plik .wsb
    start          uruchamia piaskownicę (WindowsSandbox.exe <plik.wsb>) i czeka na pętlę zadań
    instaluj       zadanie wsb/przygotuj.ps1: Python 3.14.8, Python Install Manager z kompilacją 3.14t
                   i środowiskiem .venv-t, kopia VS Code, Playwright, rozszerzenia
    projekty       zadanie: projekty przykładowe z listingów książki i ich środowiska .venv
    zrzuty [ID…]   zadanie: vsc_zrzuty.py — wszystkie zrzuty albo wskazane (klucze słownika
                   SCENARIUSZE: 1 4 8 9 10 11 12 13 14 15 interpreter menedzer); opcje sterownika
                   przechodzą dalej, np. --motyw="Default Light Modern"
                   --wyjscie=C:\zrzuty-vsc\warianty\light-modern
    zadanie NAZWA POLECENIE   dowolne polecenie PowerShell w piaskownicy (diagnostyka)
    stop           zamyka piaskownicę (shutdown w środku, w razie potrzeby wsb stop)
    wszystko [ID…] przygotuj, start, instaluj, projekty, zrzuty (wszystkie albo wskazane), stop
    kopiuj         kopiuje gotowe pliki z <katalog-wymiany>/zrzuty do docs/ (po obejrzeniu!)

Wymagania hosta: włączona funkcja Piaskownica systemu Windows, VS Code w instalacji
użytkownika (katalog mapowany do piaskownicy tylko do odczytu), połączenie z siecią
(Marketplace rozszerzeń, PyPI). W piaskownicy może działać tylko jedno wystąpienie naraz.
Gotowe obrazy trafiają do <katalog-wymiany>/zrzuty/<ścieżka względem docs>; warianty
pomocnicze do <katalog-wymiany>/warianty. Ustawienia zrzutów (rozmiar okna 1280×800,
skala 1,5, motyw Light+ jak we wcześniejszych zrzutach VS Code w książce) opisuje vsc_zrzuty.py.
Pierwsze uruchomienie (wszystko) trwa ok. 20–25 minut, w tym pobieranie rozszerzeń i pakietów.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TUTAJ = Path(__file__).resolve().parent
REPO = TUTAJ.parents[2]
KATALOG_DOMYSLNY = Path(os.environ.get("TEMP", ".")) / "zrzuty-vsc"
VSCODE = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Microsoft VS Code"
PAMIEC_MANAGERA = Path(os.environ["LOCALAPPDATA"]) / "Python" / "_cache"
PYTHON_ZIPY = [PAMIEC_MANAGERA / f"pythoncore-{tag}-64-3.14.8.zip" for tag in ("3.14", "3.14t")]
SANDBOX_EXE = Path(r"C:\Windows\System32\WindowsSandbox.exe")
WNETRZE = r"C:\zrzuty-vsc"  # katalog wymiany widziany z piaskownicy
PYTHON_NARZEDZI = r"C:\narzedzia\venv\Scripts\python.exe"

WSB = """<Configuration>
  <VGpu>Disable</VGpu>
  <Networking>Enable</Networking>
  <MemoryInMB>8192</MemoryInMB>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <PrinterRedirection>Disable</PrinterRedirection>
  <AudioInput>Disable</AudioInput>
  <VideoInput>Disable</VideoInput>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>{wymiana}</HostFolder>
      <SandboxFolder>{wnetrze}</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>{vscode}</HostFolder>
      <SandboxFolder>C:\\host\\vscode</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>{docs}</HostFolder>
      <SandboxFolder>C:\\host\\docs</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Minimized -File {wnetrze}\\wsb\\runner.ps1</Command>
  </LogonCommand>
</Configuration>
"""


def przygotuj(k: Path) -> None:
    for podkatalog in ("jobs", "running", "out", "wsb", "python", "zrzuty", "warianty"):
        (k / podkatalog).mkdir(parents=True, exist_ok=True)
    # skrypty PowerShell 5.1 w piaskownicy wymagają BOM, żeby polskie znaki przetrwały
    for ps1 in (TUTAJ / "wsb").glob("*.ps1"):
        (k / "wsb" / ps1.name).write_text(ps1.read_text(encoding="utf-8"), encoding="utf-8-sig")
    shutil.copy2(TUTAJ / "vsc_zrzuty.py", k / "wsb" / "vsc_zrzuty.py")
    for archiwum in PYTHON_ZIPY:
        if archiwum.exists() and not (k / "python" / archiwum.name).exists():
            shutil.copy2(archiwum, k / "python" / archiwum.name)
    (k / "piaskownica.wsb").write_text(
        WSB.format(wymiana=k, wnetrze=WNETRZE, vscode=VSCODE, docs=REPO / "docs"), encoding="utf-8")
    print(f"katalog wymiany: {k}")


def start(k: Path, limit: float = 300) -> None:
    gotowy = k / "out" / "runner.ready"
    gotowy.unlink(missing_ok=True)
    subprocess.Popen([str(SANDBOX_EXE), str(k / "piaskownica.wsb")])
    koniec = time.monotonic() + limit
    while time.monotonic() < koniec:
        if gotowy.exists():
            print("piaskownica gotowa")
            return
        time.sleep(2)
    sys.exit("pętla zadań nie wystartowała")


def zadanie(k: Path, nazwa: str, tresc: str, limit: float = 3600) -> int:
    for koncowka in (".done", ".log", ".err"):
        (k / "out" / f"{nazwa}{koncowka}").unlink(missing_ok=True)
    (k / "jobs" / f"{nazwa}.ps1").write_text(tresc, encoding="utf-8-sig")
    gotowe = k / "out" / f"{nazwa}.done"
    koniec = time.monotonic() + limit
    while not gotowe.exists():
        if time.monotonic() > koniec:
            sys.exit(f"zadanie {nazwa}: przekroczony limit czasu")
        time.sleep(1)
    time.sleep(0.5)
    kod = int(gotowe.read_text(encoding="utf-8-sig").strip() or 1)
    for koncowka in (".log", ".err"):
        plik = k / "out" / f"{nazwa}{koncowka}"
        if plik.exists() and plik.stat().st_size:
            print(plik.read_text(encoding="utf-8", errors="replace"))
    print(f"zadanie {nazwa}: kod {kod}")
    return kod


def sterownik(*argumenty: str) -> str:
    """Treść zadania uruchamiającego vsc_zrzuty.py z podanymi argumentami (w apostrofach PowerShell)."""
    lista = " ".join("'" + a.replace("'", "''") + "'" for a in argumenty)
    return ("$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'\n"
            f"& '{PYTHON_NARZEDZI}' '{WNETRZE}\\wsb\\vsc_zrzuty.py' {lista}\n"
            "exit $LASTEXITCODE\n")


def dziala() -> bool:
    wynik = subprocess.run(["tasklist", "/FI", "IMAGENAME eq vmmemWindowsSandbox"],
                           capture_output=True, text=True)
    return "vmmemWindowsSandbox" in wynik.stdout


def stop(k: Path) -> None:
    """Zamyka piaskownicę: zadanie shutdown w środku, a gdyby nie zadziałało — wsb stop."""
    (k / "jobs" / "zz-stop.ps1").write_text("shutdown.exe /s /t 0\n", encoding="utf-8-sig")
    for _ in range(45):
        time.sleep(2)
        if not dziala():
            break
    else:
        if shutil.which("wsb"):
            lista = subprocess.run(["wsb", "list"], capture_output=True, text=True).stdout
            for identyfikator in re.findall(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", lista):
                subprocess.run(["wsb", "stop", "--id", identyfikator])
    (k / "jobs" / "zz-stop.ps1").unlink(missing_ok=True)
    if dziala():
        sys.exit("piaskownica nadal działa — zamknij jej okno")
    # po wyłączeniu maszyny okno klienta piaskownicy pozostaje otwarte; działa tylko jedna piaskownica
    # naraz, więc to okno należy do niej
    subprocess.run(["taskkill", "/IM", "WindowsSandboxRemoteSession.exe"], capture_output=True)
    print("piaskownica zamknięta")


def kopiuj(k: Path) -> None:
    for plik in sorted((k / "zrzuty").rglob("*.png")):
        cel = REPO / "docs" / plik.relative_to(k / "zrzuty")
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plik, cel)
        print(cel.relative_to(REPO))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--katalog", type=Path, default=KATALOG_DOMYSLNY, help="katalog wymiany na hoście")
    parser.add_argument("polecenie")
    parser.add_argument("reszta", nargs="*")
    a, opcje_sterownika = parser.parse_known_args()  # np. --motyw=..., --wyjscie=... dla polecenia zrzuty
    k = a.katalog.resolve()
    match a.polecenie:
        case "przygotuj":
            przygotuj(k)
        case "start":
            start(k)
        case "instaluj":
            sys.exit(zadanie(k, "010-instaluj", f"& '{WNETRZE}\\wsb\\przygotuj.ps1'\nexit $LASTEXITCODE\n"))
        case "projekty":
            sys.exit(zadanie(k, "020-projekty", sterownik("projekty")))
        case "zrzuty":
            sys.exit(zadanie(k, f"030-zrzuty-{int(time.time())}", sterownik("zrzuty", *opcje_sterownika, *a.reszta)))
        case "zadanie":
            sys.exit(zadanie(k, a.reszta[0], " ".join(a.reszta[1:]) + "\n"))
        case "stop":
            stop(k)
        case "wszystko":
            przygotuj(k)
            start(k)
            for nazwa, tresc in (("010-instaluj", f"& '{WNETRZE}\\wsb\\przygotuj.ps1'\nexit $LASTEXITCODE\n"),
                                 ("020-projekty", sterownik("projekty")),
                                 ("030-zrzuty", sterownik("zrzuty", *opcje_sterownika, *a.reszta))):
                if zadanie(k, nazwa, tresc):
                    break
            stop(k)
        case "kopiuj":
            kopiuj(k)
        case _:
            sys.exit(f"nieznane polecenie: {a.polecenie}")


if __name__ == "__main__":
    main()
