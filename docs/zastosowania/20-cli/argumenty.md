# Argumenty i opcje

Interfejs narzędzia to jego argumenty. Rozdział 7 „Python Notatki” pokazał argument pozycyjny, opcję z wartością i pomoc; narzędzie do codziennej pracy potrzebuje więcej: ścieżek jako obiektów `Path`, wyboru z listy, przełączników z formą przeczącą, stopniowanej szczegółowości komunikatów i próbnego uruchomienia, które pokazuje plan, zanim coś zmieni.

## Narzędzie porządkujące

```python title="porzadek.py"
"""porzadek — porządkuje pliki w katalogu w podkatalogach według rozszerzenia albo daty."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

dziennik = logging.getLogger("porzadek")


def zbuduj_parser():
    parser = argparse.ArgumentParser(
        prog="porzadek",
        description="Przenosi pliki z katalogu do podkatalogów według rozszerzenia albo miesiąca modyfikacji.",
        epilog="Przykład: porzadek Pobrane --wg data --dry-run",
    )
    parser.add_argument("katalog", type=Path, nargs="?", default=Path("."), help="katalog do uporządkowania (domyślnie bieżący)")
    parser.add_argument("--wg", choices=["rozszerzenie", "data"], default="rozszerzenie", help="kryterium podziału (domyślnie %(default)s)")
    parser.add_argument("-n", "--dry-run", action="store_true", help="tylko wypisz plan, niczego nie przenoś")
    parser.add_argument("--limit", type=int, metavar="N", help="przenieś najwyżej N plików")
    parser.add_argument("--ukryte", action=argparse.BooleanOptionalAction, default=False, help="uwzględnij pliki zaczynające się od kropki")
    glosnosc = parser.add_mutually_exclusive_group()
    glosnosc.add_argument("-v", "--verbose", action="count", default=0, help="więcej komunikatów (-vv: jeszcze więcej)")
    glosnosc.add_argument("-q", "--quiet", action="store_true", help="tylko błędy")
    return parser


def podkatalog(plik, wg):
    if wg == "data":
        return datetime.fromtimestamp(plik.stat().st_mtime).strftime("%Y-%m")
    return plik.suffix.lstrip(".").lower() or "bez-rozszerzenia"


def main(argv=None):
    argumenty = zbuduj_parser().parse_args(argv)
    poziom = logging.ERROR if argumenty.quiet else [logging.WARNING, logging.INFO, logging.DEBUG][min(argumenty.verbose, 2)]
    logging.basicConfig(level=poziom, format="%(levelname)s: %(message)s", stream=sys.stderr, force=True)
    if not argumenty.katalog.is_dir():
        dziennik.error("%s nie jest katalogiem", argumenty.katalog)
        return 1
    pliki = sorted(p for p in argumenty.katalog.iterdir() if p.is_file() and (argumenty.ukryte or not p.name.startswith(".")))
    plan = [(plik, argumenty.katalog / podkatalog(plik, argumenty.wg) / plik.name) for plik in pliki][: argumenty.limit]
    dziennik.debug("kryterium %s, plików %d, w planie %d", argumenty.wg, len(pliki), len(plan))
    for zrodlo, cel in plan:
        if argumenty.dry_run:
            print(f"{zrodlo.name} -> {cel.parent.name}/")
            continue
        cel.parent.mkdir(exist_ok=True)
        zrodlo.rename(cel)
        dziennik.info("%s -> %s", zrodlo.name, cel.relative_to(argumenty.katalog))
    if not argumenty.dry_run:
        print(f"Przeniesiono plików: {len(plan)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Parser powstaje w osobnej funkcji, żeby testy i pomoc mogły go zbudować bez uruchamiania narzędzia. Nowe elementy względem rozdziału 7: `type=Path` zamienia tekst w obiekt ścieżki, `nargs="?"` z `default` czyni argument pozycyjny opcjonalnym, `choices` ogranicza wartość do listy, a `%(default)s` w `help` wstawia wartość domyślną do pomocy, więc istnieje ona w jednym miejscu. `action="store_true"` to zwykły przełącznik, `action="count"` liczy powtórzenia (`-vv`), a `BooleanOptionalAction` tworzy parę `--ukryte`/`--no-ukryte`. Grupa wzajemnie wykluczająca nie pozwala podać naraz `-v` i `-q`. `metavar` nadaje nazwę wartości w pomocy. Narzędzie pisze wyniki przez `print()` na `stdout`, a komunikaty o przebiegu przez `logging` z rozdziału 8 „Python Notatki” na `stderr`, z poziomem zależnym od opcji; `force=True` w `basicConfig()` pozwala wywołać `main()` wiele razy w jednym procesie, co przyda się w testach. Kod wyjścia wraca z `main()` do `sys.exit()` jak w rozdziale 7.

## Uruchomienie i pomoc

```python title="uzycie-porzadek.py"
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import porzadek

katalog = Path("pobrane")
shutil.rmtree(katalog, ignore_errors=True)
katalog.mkdir()
srodowisko = {**os.environ, "PYTHONUTF8": "1"}
for nazwa, data in (("raport.pdf", "2026-07-14"), ("zdjecie.JPG", "2026-08-02"), ("notatki.txt", "2026-08-30"), ("archiwum.zip", "2026-09-01"), ("README", "2026-09-20"), (".ukryty", "2026-09-21")):
    plik = katalog / nazwa
    plik.write_text("", encoding="utf-8")
    czas = datetime.fromisoformat(data).timestamp()
    os.utime(plik, (czas, czas))

print("--- plan według rozszerzenia")
print("kod:", porzadek.main(["pobrane", "--dry-run"]))
print("--- plan według daty, z ukrytymi, limit 3")
print("kod:", porzadek.main(["pobrane", "-n", "--wg", "data", "--ukryte", "--limit", "3"]))
print("--- wykonanie jako proces, oba strumienie razem")
proces = subprocess.run([sys.executable, "porzadek.py", "pobrane", "--wg", "data", "-v"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=srodowisko)
print(proces.stdout + "kod:", proces.returncode)
print(sorted(str(p.relative_to(katalog)).replace(os.sep, "/") for p in katalog.rglob("*")))
print("--- błąd użycia")
proces = subprocess.run([sys.executable, "porzadek.py", "pobrane", "--wg", "nazwa"], capture_output=True, text=True, encoding="utf-8", env=srodowisko)
print("kod:", proces.returncode, "| stdout:", repr(proces.stdout), "| stderr:", proces.stderr.splitlines()[-1])
print("--- pomoc")
print(subprocess.run([sys.executable, "porzadek.py", "--help"], capture_output=True, text=True, encoding="utf-8", env=srodowisko).stdout)
```

```{ .text .no-copy }
--- plan według rozszerzenia
archiwum.zip -> zip/
notatki.txt -> txt/
raport.pdf -> pdf/
README -> bez-rozszerzenia/
zdjecie.JPG -> jpg/
kod: 0
--- plan według daty, z ukrytymi, limit 3
.ukryty -> 2026-09/
archiwum.zip -> 2026-09/
notatki.txt -> 2026-08/
kod: 0
--- wykonanie jako proces, oba strumienie razem
INFO: archiwum.zip -> 2026-09\archiwum.zip
INFO: notatki.txt -> 2026-08\notatki.txt
INFO: raport.pdf -> 2026-07\raport.pdf
INFO: README -> 2026-09\README
INFO: zdjecie.JPG -> 2026-08\zdjecie.JPG
Przeniesiono plików: 5
kod: 0
['.ukryty', '2026-07', '2026-07/raport.pdf', '2026-08', '2026-08/notatki.txt', '2026-08/zdjecie.JPG', '2026-09', '2026-09/README', '2026-09/archiwum.zip']
--- błąd użycia
kod: 2 | stdout: '' | stderr: porzadek: error: argument --wg: invalid choice: 'nazwa' (choose from 'rozszerzenie', 'data')
--- pomoc
usage: porzadek [-h] [--wg {rozszerzenie,data}] [-n] [--limit N]
                [--ukryte | --no-ukryte] [-v | -q]
                [katalog]

Przenosi pliki z katalogu do podkatalogów według rozszerzenia albo miesiąca
modyfikacji.

positional arguments:
  katalog               katalog do uporządkowania (domyślnie bieżący)

options:
  -h, --help            show this help message and exit
  --wg {rozszerzenie,data}
                        kryterium podziału (domyślnie rozszerzenie)
  -n, --dry-run         tylko wypisz plan, niczego nie przenoś
  --limit N             przenieś najwyżej N plików
  --ukryte, --no-ukryte
                        uwzględnij pliki zaczynające się od kropki
  -v, --verbose         więcej komunikatów (-vv: jeszcze więcej)
  -q, --quiet           tylko błędy

Przykład: porzadek Pobrane --wg data --dry-run
```

Skrypt kontrolny tworzy katalog z plikami o ustalonych datach modyfikacji (`os.utime()`), więc podział według miesiąca jest przewidywalny, i wywołuje `main()` z listą argumentów — tak samo zrobią testy. Próbne uruchomienie wypisuje plan i niczego nie zmienia. Wykonanie z `-v` skrypt uruchamia jako osobny proces z połączonymi strumieniami: komunikaty `INFO` dziennika idą na `stderr`, podsumowanie na `stdout` — i pojawia się ono na końcu, bo `stdout` skierowany do potoku jest buforowany blokowo i trafia do niego dopiero po zapełnieniu bufora albo przy zakończeniu programu, a `stderr` jest buforowany wierszami. **Procesy potomne** (ang. *child processes*) dostają zmienną środowiskową `PYTHONUTF8=1`, żeby polskie znaki w pomocy przeszły przez potok bez błędu; następna strona wraca do tego tematu. Błędną wartość `--wg` parser odrzuca sam: wypisuje na `stderr` sposób użycia i komunikat, a proces kończy się kodem `2`, zarezerwowanym dla błędów użycia. Pomoc powstaje z opisu argumentów: sposób użycia z nawiasami dla elementów opcjonalnych, argumenty pozycyjne, opcje (z wartością domyślną `--wg` wstawioną przez `%(default)s`) i przykład z `epilog`.

## Reguły projektowania opcji

| Reguła | Dlaczego |
|---|---|
| Krótkie `-v` i długie `--verbose` dla często używanych opcji; tylko długie dla rzadkich | krótkie pisze się w terminalu, długie czyta w skryptach i harmonogramach |
| Bez argumentów robi coś sensownego albo pokazuje pomoc | `porzadek` bez argumentów porządkuje katalog bieżący, jak `git status`; narzędzie, które bez argumentów nie ma na czym pracować, wypisuje pomoc zamiast wyjątku |
| Wartości domyślne w pomocy (`%(default)s`) | użytkownik nie musi czytać kodu |
| `--dry-run` dla każdej operacji, która zmienia pliki | pozwala sprawdzić plan; skrypt automatyczny może go zapisać do dziennika |
| Przełączniki z formą przeczącą (`BooleanOptionalAction`) | konfiguracja i skrypty mogą jawnie wyłączyć to, co domyślnie włączone |
| `-q`, `-v`, `-vv` sterują tylko dziennikiem, nie wynikiem | wynik na `stdout` jest zawsze taki sam, więc program czytający z potoku dostaje zawsze te same dane |
| Błąd użycia → kod `2` i komunikat na `stderr` | tak robi `argparse` i narzędzia systemowe; kod `1` zostaje dla błędów wykonania |

Te reguły pochodzą z narzędzi systemowych, do których użytkownicy terminala są przyzwyczajeni; narzędzie, które ich przestrzega, daje się łączyć z innymi bez czytania dokumentacji.
