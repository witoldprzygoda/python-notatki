"""Strażnik gałęzi książki: kontrola, czy commit albo katalog roboczy zawiera
wyłącznie książkę.

Gałęzie dev i master (a także content/* i infra/*) zawierają wyłącznie książkę
i narzędzia służące jej przygotowaniu; ćwiczenia rozwija gałąź cwiczenia,
a slajdy wykładowe — gałąź slajdy (zasady w DEVELOPMENT_WORKFLOW.md).

Domyślnie skrypt bada wskazany commit, a nie katalog roboczy: listę plików
odczytuje przez git ls-tree, treść stron przez git grep, a konfigurację przez
git show <commit>:mkdocs.yml. Wynik nie zależy więc od tego, w którym katalogu
roboczym (worktree) repozytorium ani w którym jego podkatalogu skrypt
uruchomiono. W ten sposób wywołuje go także hook pre-push instalowany przez
scripts/install_git_hooks.py.

Z opcją --robocze skrypt bada bieżący katalog roboczy: pliki śledzone
i nieśledzone (z pominięciem ignorowanych) w ich obecnej postaci, łącznie ze
zmianami jeszcze niedodanymi do indeksu i niezatwierdzonymi.

Naruszeniem jest:
  - plik warstwy ćwiczeń: activities/**, scripts/build_activities.py,
    docs/javascripts/interactive/**, docs/stylesheets/interactive.css,
    tests/interactive/**, tests/test_build_activities.py, mkdocs.kurs.yml,
    kurs/**, .github/workflows/kurs.yml (te same ścieżki, które gałąź
    cwiczenia może dodawać);
  - plik dawnej warstwy ćwiczeń, usuniętej z książki 3 X 2026:
    mkdocs.clean.yml, INTERACTIVE_SYSTEM_SPEC.md;
  - plik slajdów wykładowych: slajdy/**;
  - atrybut data-activity-… w stronie Markdown w katalogu docs/ (rozszerzenia
    .md, .markdown, .mdown, .mkdn i .mkd, jak w MkDocs);
  - wpis build_activities, activities, interactive.css, javascripts/interactive
    albo presentation_mode w mkdocs.yml.

Użycie: python scripts/check_book_only.py [<commit> | --robocze]
        (bez argumentu skrypt bada commit HEAD)

Każde naruszenie jest wypisywane w osobnym wierszu. Kod wyjścia: 0 — commit
albo katalog roboczy zawiera wyłącznie książkę; 1 — znaleziono naruszenia;
2 — błędne wywołanie albo błąd Gita.
"""
import os
import re
import subprocess
import sys

UZYCIE = "Użycie: python scripts/check_book_only.py [<commit> | --robocze]"
ROBOCZE = "--robocze"

# Ścieżki warstwy ćwiczeń — te same, które gałąź cwiczenia może dodawać.
KATALOGI_CWICZEN = (
    "activities/",
    "docs/javascripts/interactive/",
    "tests/interactive/",
    "kurs/",
)
PLIKI_CWICZEN = {
    "scripts/build_activities.py",
    "docs/stylesheets/interactive.css",
    "tests/test_build_activities.py",
    "mkdocs.kurs.yml",
    ".github/workflows/kurs.yml",
}
# Pliki dawnej warstwy ćwiczeń, usunięte z książki 3 X 2026 (wcześniejszy stan
# zachowuje tag przed-rozdzieleniem-cwiczen); gałąź cwiczenia ich nie dodaje.
PLIKI_DAWNEJ_WARSTWY = {
    "mkdocs.clean.yml",
    "INTERACTIVE_SYSTEM_SPEC.md",
}
# Slajdy wykładowe powstają na osobnej gałęzi slajdy.
KATALOGI_SLAJDOW = ("slajdy/",)
ZNACZNIK_W_TRESCI = "data-activity-"
# Rozszerzenia stron Markdown w MkDocs 1.6 (mkdocs.utils.markdown_extensions).
ROZSZERZENIA_STRON = (".md", ".markdown", ".mdown", ".mkdn", ".mkd")
WZORCE_STRON = tuple(f":(top)docs/*{rozszerzenie}" for rozszerzenie in ROZSZERZENIA_STRON)
WPISY_KONFIGURACJI = (
    "build_activities",
    "interactive.css",
    "javascripts/interactive",
    "presentation_mode",
)
# Katalog activities jako osobne słowo, np. wpis „- activities” w sekcji watch.
KATALOG_W_KONFIGURACJI = re.compile(r"(?<![\w-])activities(?![\w-])")
# Rodzaje naruszeń: etykieta wiersza i etykieta w podsumowaniu.
PLIK, DAWNY, SLAJD = "plik ćwiczeń", "plik dawnej warstwy ćwiczeń", "plik slajdów"
ZNACZNIK, WPIS = "znacznik w treści", "wpis w mkdocs.yml"
PODSUMOWANIE = {PLIK: "pliki ćwiczeń", DAWNY: "pliki dawnej warstwy",
                SLAJD: "pliki slajdów", ZNACZNIK: "znaczniki w treści",
                WPIS: "wpisy w mkdocs.yml"}


class BladGita(Exception):
    """Polecenie git zakończyło się błędem albo wskazany obiekt nie istnieje."""


def git(*argumenty, kody=(0,)):
    """Uruchamia git w bieżącym katalogu; zwraca (kod wyjścia, stdout)."""
    try:
        wynik = subprocess.run(["git", *argumenty], stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", check=False)
    except OSError as blad:
        raise BladGita(f"nie można uruchomić programu git ({blad})") from blad
    if wynik.returncode not in kody:
        komunikat = wynik.stderr.strip() or f"kod wyjścia {wynik.returncode}"
        raise BladGita(f"git {argumenty[0]}: {komunikat}")
    return wynik.returncode, wynik.stdout


def rodzaj_pliku(sciezka):
    """Rodzaj naruszenia dla ścieżki pliku albo None, gdy plik należy do książki."""
    if sciezka in PLIKI_CWICZEN or sciezka.startswith(KATALOGI_CWICZEN):
        return PLIK
    if sciezka in PLIKI_DAWNEJ_WARSTWY:
        return DAWNY
    if sciezka.startswith(KATALOGI_SLAJDOW):
        return SLAJD
    return None


def naruszenia_plikow(pliki):
    """Naruszenia wynikające z samej listy plików."""
    return [(rodzaj, sciezka) for sciezka in pliki
            if (rodzaj := rodzaj_pliku(sciezka)) is not None]


def naruszenia_tresci(zrodlo, przedrostek=""):
    """Znaczniki w stronach Markdown katalogu docs/ (git grep w podanym źródle)."""
    # Wiersz wyniku przy -z: <przedrostek><ścieżka>\0<numer wiersza>\0<treść>.
    _, trafienia = git("grep", "-n", "-I", "-z", "--full-name", "--no-color", "-F",
                       "-e", ZNACZNIK_W_TRESCI, zrodlo, "--", *WZORCE_STRON,
                       kody=(0, 1))
    naruszenia = []
    for rekord in trafienia.split("\n"):
        if not rekord:
            continue
        sciezka, numer, tresc = (rekord.split("\0", 2) + ["", ""])[:3]
        sciezka = sciezka.removeprefix(przedrostek)
        naruszenia.append((ZNACZNIK, f"{sciezka}:{numer}: {tresc.strip()}"))
    return naruszenia


def naruszenia_konfiguracji(tekst):
    """Wpisy warstwy ćwiczeń w treści mkdocs.yml."""
    return [(WPIS, f"mkdocs.yml:{numer}: {wiersz.strip()}")
            for numer, wiersz in enumerate(tekst.splitlines(), 1)
            if any(wpis in wiersz for wpis in WPISY_KONFIGURACJI)
            or KATALOG_W_KONFIGURACJI.search(wiersz)]


def sprawdz_commit(ref):
    """Zwraca opis commitu i listę naruszeń (rodzaj, opis)."""
    kod, sha = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", kody=(0, 1))
    if kod != 0:
        raise BladGita(f"„{ref}” nie wskazuje commitu")
    sha = sha.strip()
    skrot = git("rev-parse", "--short", sha)[1].strip()

    # --full-tree: pełne ścieżki niezależnie od podkatalogu, w którym uruchomiono skrypt.
    lista = git("ls-tree", "-r", "-z", "--full-tree", "--name-only", sha)[1]
    pliki = [sciezka for sciezka in lista.split("\0") if sciezka]
    naruszenia = naruszenia_plikow(pliki) + naruszenia_tresci(sha, f"{sha}:")

    if "mkdocs.yml" not in pliki:
        raise BladGita(f"commit {skrot} nie zawiera pliku mkdocs.yml")
    naruszenia += naruszenia_konfiguracji(git("show", f"{sha}:mkdocs.yml")[1])
    return skrot, naruszenia


def sprawdz_katalog_roboczy():
    """Zwraca opis bieżącego katalogu roboczego i listę naruszeń (rodzaj, opis)."""
    gora = git("rev-parse", "--show-toplevel")[1].strip()
    if not gora:
        raise BladGita("bieżący katalog nie należy do katalogu roboczego repozytorium")
    try:
        os.chdir(gora)
    except OSError as blad:
        raise BladGita(f"nie można przejść do katalogu {gora} ({blad})") from blad

    # Pliki śledzone i nieśledzone bez ignorowanych; plik usunięty z dysku pomijamy.
    lista = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")[1]
    pliki = sorted({sciezka for sciezka in lista.split("\0")
                    if sciezka and os.path.lexists(sciezka)})
    naruszenia = naruszenia_plikow(pliki) + naruszenia_tresci("--untracked")

    try:
        with open("mkdocs.yml", encoding="utf-8", errors="replace") as plik:
            konfiguracja = plik.read()
    except OSError as blad:
        raise BladGita(f"nie można odczytać pliku mkdocs.yml ({blad})") from blad
    naruszenia += naruszenia_konfiguracji(konfiguracja)
    return f"katalog roboczy {gora}", naruszenia


def main(argumenty):
    """Sprawdza commit albo katalog roboczy i zwraca kod wyjścia 0, 1 albo 2."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if any(a in ("-h", "--help") for a in argumenty):
        print(__doc__)
        return 0
    if len(argumenty) > 1 or (argumenty and argumenty[0].startswith("-")
                               and argumenty[0] != ROBOCZE):
        print(UZYCIE, file=sys.stderr)
        return 2
    try:
        if argumenty == [ROBOCZE]:
            opis, naruszenia = sprawdz_katalog_roboczy()
        else:
            opis, naruszenia = sprawdz_commit(argumenty[0] if argumenty else "HEAD")
    except BladGita as blad:
        print(f"BŁĄD: {blad}", file=sys.stderr)
        return 2
    if not naruszenia:
        print(f"OK: {opis} zawiera wyłącznie książkę")
        return 0
    for rodzaj, szczegoly in naruszenia:
        print(f"NARUSZENIE ({rodzaj}): {szczegoly}")
    liczby = {}
    for rodzaj, _ in naruszenia:
        liczby[rodzaj] = liczby.get(rodzaj, 0) + 1
    rozbicie = ", ".join(f"{PODSUMOWANIE[rodzaj]}: {n}" for rodzaj, n in liczby.items())
    print(f"NIEZGODNOŚĆ: {opis} zawiera elementy spoza książki; "
          f"liczba naruszeń: {len(naruszenia)} ({rozbicie})")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
