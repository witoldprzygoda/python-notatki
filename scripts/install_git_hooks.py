"""Instalator hooków Git chroniących gałęzie książki.

Zapisuje w katalogu $(git rev-parse --git-common-dir)/hooks dwa hooki w języku
powłoki POSIX (Git for Windows uruchamia je dołączonym do siebie bashem).
Katalog hooków jest wspólny dla wszystkich katalogów roboczych (worktree)
repozytorium, więc jedna instalacja obejmuje każdy z nich.

pre-push
    Chroni gałęzie dev i master w repozytorium zdalnym. Przy ich aktualizacji
    przerywa wypchnięcie, gdy:
      - wypychany zakres zawiera commit scalający (historia dev i master jest
        liniowa; gdy gałęzi nie ma jeszcze w repozytorium zdalnym, badana jest
        cała historia wypychanego commitu);
      - wypchnięcie nie jest przewinięciem, czyli nadpisałoby historię;
      - wypychany commit nie zawiera strażnika scripts/check_book_only.py albo
        strażnik jest pusty;
      - strażnik zgłosi naruszenia.
    Strażnik działa w wersji z wypychanego commitu, a jeśli gałąź istnieje
    w repozytorium zdalnym z inną wersją strażnika — także w tamtej wersji;
    wypychany commit nie może więc osłabić kontroli, której podlega.
    Złagodzenie reguł strażnika wymaga dwóch wypchnięć: najpierw samego
    strażnika, potem zmian, które on dopuszcza.
    Strażnik trafia do prywatnego katalogu tymczasowego i działa w trybie
    izolowanym Pythona (-I) pod interpreterem o ścieżce bezwzględnej ustalonej
    podczas instalacji. Pierwszeństwo ma .venv w katalogu głównym
    repozytorium; alias python3 z katalogu WindowsApps nigdy nie jest używany.
    Każdy błąd (brak interpretera, brak commitu z repozytorium zdalnego, błąd
    Gita) przerywa wypchnięcie. Pozostałe gałęzie oraz usunięcia gałęzi hook
    przepuszcza.
pre-rebase
    Odmawia przebudowy historii (rebase) gałęzi cwiczenia i gałęzi sync/*
    (drugi argument hooka, a gdy go brak — bieżąca gałąź).

Instalacja jest idempotentna: ponowne uruchomienie niczego nie zmienia, a hook
z tego instalatora w innej wersji zostaje zaktualizowany. Obcy hook o tej
samej nazwie przed zastąpieniem zostaje zachowany jako <nazwa>.przed-instalacja.

Użycie: python scripts/install_git_hooks.py [--sprawdz | --usun]

    bez opcji    instaluje albo aktualizuje oba hooki;
    --sprawdz    wypisuje stan hooków i niczego nie zmienia;
    --usun       usuwa hooki zainstalowane przez ten skrypt (obcych nie zmienia).

Kod wyjścia: 0 — powodzenie (dla --sprawdz: oba hooki zainstalowane, aktualne
i z istniejącym interpreterem); 1 — --sprawdz wykrył braki; 2 — błędne
wywołanie, błąd Gita albo brak odpowiedniego interpretera.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

UZYCIE = "Użycie: python scripts/install_git_hooks.py [--sprawdz | --usun]"
ZNACZNIK = "python-notatki: hook zainstalowany przez scripts/install_git_hooks.py"
PRZYROSTEK_KOPII = ".przed-instalacja"

PRE_PUSH = """#!/bin/sh
# @ZNACZNIK@
# Chroni gałęzie dev i master w repozytorium zdalnym: przerywa wypchnięcie, które
# wprowadza commit scalający, nadpisuje historię albo zawiera materiał spoza
# książki według strażnika scripts/check_book_only.py. Strażnik pochodzi
# z wypychanego commitu oraz z bieżącego stanu gałęzi w repozytorium zdalnym,
# a interpreter ustalono podczas instalacji. Każdy błąd przerywa wypchnięcie.
PYTHON=@PYTHON@
katalog=

przerwij() {
    for wiersz in "$@"; do
        echo "pre-push: $wiersz" >&2
    done
    echo "pre-push: wypchnięcie przerwane (zasady w DEVELOPMENT_WORKFLOW.md)." >&2
    exit 1
}

sprzataj() {
    [ -z "$katalog" ] || rm -rf "$katalog"
}
trap sprzataj EXIT
trap 'exit 1' HUP INT TERM

# uruchom_straznika <obiekt strażnika> <badany commit> <pochodzenie strażnika>
uruchom_straznika() {
    if [ -z "$katalog" ]; then
        katalog=$(mktemp -d "${TMPDIR:-/tmp}/pre-push.XXXXXX") ||
            przerwij "nie można utworzyć katalogu tymczasowego."
    fi
    plik=$katalog/check_book_only.py
    git cat-file blob "$1" >"$plik" </dev/null ||
        przerwij "nie można odczytać strażnika ($3)."
    [ -s "$plik" ] ||
        przerwij "strażnik scripts/check_book_only.py ($3) jest pusty."
    sciezka=$plik
    if command -v cygpath >/dev/null 2>&1; then
        sciezka=$(cygpath -m "$plik")  # ścieżka czytelna dla interpretera Windows
    fi
    # -I: tryb izolowany, bez katalogu skryptu w sys.path i bez zmiennych PYTHON*.
    "$PYTHON" -I "$sciezka" "$2" </dev/null
    wynik=$?
    [ "$wynik" -eq 0 ] ||
        przerwij "strażnik ($3) odrzucił commit $2 dla gałęzi $galaz (kod $wynik)."
}

while read -r lokalna_ref lokalny_sha zdalna_ref zdalny_sha
do
    case "$zdalna_ref" in
        refs/heads/dev|refs/heads/master) ;;
        *) continue ;;
    esac
    case "$lokalny_sha" in
        *[!0]*) ;;
        *) continue ;;  # usunięcie gałęzi: brak commitu do sprawdzenia
    esac
    galaz=${zdalna_ref#refs/heads/}
    [ -f "$PYTHON" ] ||
        przerwij "brak interpretera $PYTHON." "Uruchom ponownie scripts/install_git_hooks.py."

    # Historia dev i master jest liniowa i nie jest nadpisywana.
    case "$zdalny_sha" in
        *[!0]*) zakres=$zdalny_sha..$lokalny_sha ;;
        *) zakres=$lokalny_sha ;;  # gałęzi nie ma w repozytorium zdalnym: cała historia
    esac
    scalenie=$(git rev-list --merges -n 1 "$zakres" </dev/null) ||
        przerwij "nie można ustalić wypychanego zakresu $zakres;" \\
                 "jeśli brak commitu z repozytorium zdalnego, najpierw pobierz zmiany (git fetch)."
    [ -z "$scalenie" ] ||
        przerwij "zakres $zakres zawiera commit scalający $scalenie;" \\
                 "do gałęzi $galaz trafiają wyłącznie przewinięcia (ang. fast-forward), bez commitów scalających."
    case "$zdalny_sha" in
        *[!0]*)
            git merge-base --is-ancestor "$zdalny_sha" "$lokalny_sha" </dev/null ||
                przerwij "wypchnięcie nie jest przewinięciem (ang. fast-forward) gałęzi $galaz" \\
                         "i nadpisałoby jej historię."
            ;;
    esac

    # Strażnik z wypychanego commitu, a jeśli inny — także z gałęzi w repozytorium
    # zdalnym: wypychany commit nie może osłabić kontroli, której podlega.
    straznik=$(git rev-parse --verify --quiet "$lokalny_sha:scripts/check_book_only.py" </dev/null) ||
        przerwij "commit $lokalny_sha nie zawiera strażnika scripts/check_book_only.py," \\
                 "więc nie może trafić do gałęzi $galaz."
    uruchom_straznika "$straznik" "$lokalny_sha" "wersja z wypychanego commitu"
    case "$zdalny_sha" in
        *[!0]*)
            straznik_zdalny=$(git rev-parse --verify --quiet "$zdalny_sha:scripts/check_book_only.py" </dev/null) ||
                straznik_zdalny=
            if [ -n "$straznik_zdalny" ] && [ "$straznik_zdalny" != "$straznik" ]; then
                uruchom_straznika "$straznik_zdalny" "$lokalny_sha" \\
                    "wersja z gałęzi $galaz w repozytorium zdalnym"
            fi
            ;;
    esac
done
exit 0
"""

PRE_REBASE = """#!/bin/sh
# @ZNACZNIK@
# Odmawia przebudowy historii (rebase) gałęzi cwiczenia i sync/*. Obie zawierają
# scalenia z dev; rebase skopiowałby commity książki jako nowe commity gałęzi
# ćwiczeń. Zamiast rebase scalamy zmiany (merge); gałąź sync/*, której nie da się
# przewinąć, można też zastąpić nową gałęzią sync/* od aktualnej gałęzi cwiczenia.
if [ -n "$2" ]; then
    galaz=$2
else
    galaz=$(git symbolic-ref --quiet HEAD 2>/dev/null) || galaz=
fi
galaz=${galaz#refs/heads/}
case "$galaz" in
    cwiczenia|sync/*)
        echo "pre-rebase: gałęzi $galaz nie przebudowujemy poleceniem rebase." >&2
        echo "pre-rebase: zamiast tego scal zmiany (git merge); gałąź sync/* można też zastąpić" >&2
        echo "pre-rebase: nową gałęzią, np. sync/RRRR-MM-DD-2, utworzoną od aktualnej gałęzi cwiczenia." >&2
        echo "pre-rebase: zasady w kurs/README.md na gałęzi cwiczenia." >&2
        exit 1
        ;;
esac
exit 0
"""

HOOKI = ("pre-push", "pre-rebase")


class Blad(Exception):
    """Błąd, który uniemożliwia wykonanie polecenia."""


def git(*argumenty):
    """Uruchamia git w bieżącym katalogu; zwraca (kod wyjścia, stdout, stderr)."""
    try:
        wynik = subprocess.run(["git", *argumenty], stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", check=False)
    except OSError as blad:
        raise Blad(f"nie można uruchomić programu git ({blad})") from blad
    return wynik.returncode, wynik.stdout.strip(), wynik.stderr.strip()


def katalog_wspolny():
    """Bezwzględna ścieżka wspólnego katalogu Gita (--git-common-dir)."""
    kod, wyjscie, bledy = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if kod != 0 or not wyjscie:
        raise Blad(f"bieżący katalog nie należy do repozytorium Git ({bledy})")
    return Path(wyjscie)


def wybierz_interpreter(wspolny):
    """Zwraca bezwzględną ścieżkę interpretera dla hooka pre-push albo None."""
    glowny = wspolny.parent
    kandydaci = [glowny / ".venv" / "Scripts" / "python.exe", glowny / ".venv" / "bin" / "python"]
    if sys.executable:
        kandydaci.append(Path(sys.executable))
    for kandydat in kandydaci:
        sciezka = Path(os.path.abspath(kandydat))
        if sciezka.is_file() and "windowsapps" not in str(sciezka).lower():
            return sciezka
    return None


def w_apostrofach(tekst):
    """Zapis tekstu jako jednego słowa powłoki POSIX."""
    return "'" + tekst.replace("'", "'\"'\"'") + "'"


def tresci_hookow(python):
    """Oczekiwana treść obu hooków dla danego interpretera."""
    return {
        "pre-push": PRE_PUSH.replace("@ZNACZNIK@", ZNACZNIK)
                            .replace("@PYTHON@", w_apostrofach(python.as_posix())),
        "pre-rebase": PRE_REBASE.replace("@ZNACZNIK@", ZNACZNIK),
    }


def odczytaj(sciezka):
    """Treść pliku hooka bez zmiany znaków końca wiersza."""
    return sciezka.read_bytes().decode("utf-8", errors="replace")


def kopie(katalog, nazwa):
    """Kopie obcych hooków o danej nazwie, zachowane przy instalacji."""
    return sorted(katalog.glob(nazwa + PRZYROSTEK_KOPII + "*"))


def wolna_nazwa_kopii(sciezka):
    """Pierwsza niezajęta nazwa kopii: <nazwa>.przed-instalacja[-N]."""
    kopia = sciezka.with_name(sciezka.name + PRZYROSTEK_KOPII)
    numer = 2
    while kopia.exists():
        kopia = sciezka.with_name(f"{sciezka.name}{PRZYROSTEK_KOPII}-{numer}")
        numer += 1
    return kopia


def ostrzez_o_hookspath(katalog):
    """Ostrzega, gdy Git uruchamia hooki z innego katalogu; zwraca True przy ostrzeżeniu."""
    kod, sciezka, _ = git("config", "--get", "core.hooksPath")
    if kod == 0 and sciezka:
        print(f"UWAGA: ustawienie core.hooksPath = {sciezka}: Git uruchamia hooki z tego "
              f"katalogu, a nie z {katalog.as_posix()}, więc hooki z tego instalatora "
              "nie będą działać.")
        return True
    return False


def instaluj(katalog, python):
    """Instaluje albo aktualizuje oba hooki; zachowuje obce hooki jako kopie."""
    katalog.mkdir(parents=True, exist_ok=True)
    for nazwa, tresc in tresci_hookow(python).items():
        sciezka = katalog / nazwa
        if not sciezka.exists():
            stan = "zainstalowano"
        else:
            obecna = odczytaj(sciezka)
            if obecna == tresc:
                print(f"{nazwa}: bez zmian (zainstalowany i aktualny)")
                continue
            if ZNACZNIK in obecna:
                stan = "zaktualizowano"
            else:
                kopia = wolna_nazwa_kopii(sciezka)
                sciezka.replace(kopia)
                print(f"{nazwa}: obcy hook zachowano jako {kopia.name}")
                stan = "zainstalowano"
        sciezka.write_bytes(tresc.encode("utf-8"))
        os.chmod(sciezka, 0o755)
        print(f"{nazwa}: {stan}")
    ostrzez_o_hookspath(katalog)
    return 0


def raport(katalog, python):
    """Wypisuje stan hooków; zwraca 0, gdy oba są zainstalowane i aktualne."""
    oczekiwane = tresci_hookow(python) if python else {}
    w_porzadku = True
    for nazwa in HOOKI:
        sciezka = katalog / nazwa
        if not sciezka.exists():
            print(f"{nazwa}: brak")
            w_porzadku = False
        else:
            obecna = odczytaj(sciezka)
            if ZNACZNIK not in obecna:
                print(f"{nazwa}: obcy hook (nie pochodzi z tego instalatora)")
                w_porzadku = False
            elif obecna == oczekiwane.get(nazwa):
                print(f"{nazwa}: zainstalowany, aktualny")
            else:
                print(f"{nazwa}: zainstalowany, nieaktualny (uruchom instalator ponownie)")
                w_porzadku = False
            if nazwa == "pre-push" and ZNACZNIK in obecna:
                wpis = re.search(r"^PYTHON='(.*)'$", obecna, re.MULTILINE)
                interpreter = wpis.group(1).replace("'\"'\"'", "'") if wpis else ""
                istnieje = bool(interpreter) and Path(interpreter).is_file()
                print(f"{nazwa}: interpreter {interpreter or '(nie odczytano)'} — "
                      f"{'istnieje' if istnieje else 'BRAK'}")
                w_porzadku = w_porzadku and istnieje
        for kopia in kopie(katalog, nazwa):
            print(f"{nazwa}: kopia poprzedniego hooka: {kopia.name}")
    if ostrzez_o_hookspath(katalog):
        w_porzadku = False
    return 0 if w_porzadku else 1


def usun(katalog):
    """Usuwa wyłącznie hooki zainstalowane przez ten skrypt."""
    for nazwa in HOOKI:
        sciezka = katalog / nazwa
        if not sciezka.exists():
            print(f"{nazwa}: brak, nic do usunięcia")
        elif ZNACZNIK in odczytaj(sciezka):
            sciezka.unlink()
            print(f"{nazwa}: usunięto")
        else:
            print(f"{nazwa}: obcy hook, pozostawiono bez zmian")
        for kopia in kopie(katalog, nazwa):
            print(f"{nazwa}: pozostała kopia poprzedniego hooka {kopia.name}; "
                  "w razie potrzeby można ją przywrócić ręcznie")
    return 0


def main(argumenty):
    """Wykonuje polecenie wskazane opcją i zwraca kod wyjścia."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if any(a in ("-h", "--help") for a in argumenty):
        print(__doc__)
        return 0
    if len(argumenty) > 1 or (argumenty and argumenty[0] not in ("--sprawdz", "--usun")):
        print(UZYCIE, file=sys.stderr)
        return 2
    tryb = argumenty[0] if argumenty else "--instaluj"
    try:
        wspolny = katalog_wspolny()
        katalog = wspolny / "hooks"
        print(f"Katalog hooków: {katalog.as_posix()} (wspólny dla wszystkich katalogów "
              "roboczych repozytorium)")
        if tryb == "--usun":
            return usun(katalog)
        python = wybierz_interpreter(wspolny)
        if tryb == "--sprawdz":
            return raport(katalog, python)
        if python is None:
            raise Blad("nie znaleziono interpretera Pythona: brak .venv w katalogu głównym "
                       "repozytorium, a bieżący interpreter jest aliasem z WindowsApps")
        print(f"Interpreter dla hooka pre-push: {python.as_posix()}")
        return instaluj(katalog, python)
    except (Blad, OSError) as blad:
        print(f"BŁĄD: {blad}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
