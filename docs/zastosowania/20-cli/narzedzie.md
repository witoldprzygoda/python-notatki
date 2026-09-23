# Od skryptu do polecenia

Narzędzie, które ma działać codziennie, potrzebuje testów i instalacji jako polecenie. Oba wynikają z decyzji podjętych na poprzednich stronach: `main(argv)` daje się wywołać z testu, a skrypt z tą funkcją jest gotowym punktem wejścia pakietu.

## Testy narzędzia

```python title="test_porzadek.py"
import os
from datetime import datetime

import pytest

import porzadek


@pytest.fixture
def katalog(tmp_path):
    for nazwa, data in (("a.txt", "2026-07-01"), ("b.txt", "2026-08-01"), ("c.jpg", "2026-08-15")):
        plik = tmp_path / nazwa
        plik.write_text("x", encoding="utf-8")
        czas = datetime.fromisoformat(data).timestamp()
        os.utime(plik, (czas, czas))
    return tmp_path


def test_dry_run_niczego_nie_przenosi(katalog, capsys):
    assert porzadek.main([str(katalog), "--dry-run"]) == 0
    assert capsys.readouterr().out.splitlines() == ["a.txt -> txt/", "b.txt -> txt/", "c.jpg -> jpg/"]
    assert sorted(p.name for p in katalog.iterdir()) == ["a.txt", "b.txt", "c.jpg"]


def test_podzial_wedlug_daty(katalog, capsys):
    assert porzadek.main([str(katalog), "--wg", "data"]) == 0
    assert sorted(p.name for p in katalog.iterdir()) == ["2026-07", "2026-08"]
    assert sorted(p.name for p in (katalog / "2026-08").iterdir()) == ["b.txt", "c.jpg"]
    assert "Przeniesiono plików: 3" in capsys.readouterr().out


def test_nieistniejacy_katalog_to_kod_1(tmp_path, capsys):
    assert porzadek.main([str(tmp_path / "nie-ma")]) == 1
    assert "nie jest katalogiem" in capsys.readouterr().err


def test_bledna_opcja_to_kod_2():
    with pytest.raises(SystemExit) as wyjscie:
        porzadek.main(["--wg", "nazwa"])
    assert wyjscie.value.code == 2
```

```python title="test_licznik.py"
import re
import subprocess
import sys
from pathlib import Path

from licznik import main, policz


def test_policz_liczy_wiersze_slowa_i_wzorzec():
    assert policz("ala ma kota\nkot ma alę\n") == (2, 6, None)
    assert policz("ala ma kota\nkot ma alę\n", re.compile("ma")) == (2, 6, 2)


def test_plik_i_brakujacy_plik(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("raz dwa\n", encoding="utf-8")
    assert main([str(tmp_path / "a.txt"), str(tmp_path / "brak.txt")]) == 1
    wyjscie = capsys.readouterr()
    assert wyjscie.out == f"     1      2  {tmp_path / 'a.txt'}\n"
    assert "brak.txt" in wyjscie.err


def test_wejscie_standardowe_przez_proces():
    proces = subprocess.run([sys.executable, Path(__file__).with_name("licznik.py"), "-e", "a"], input="banan\nananas\n", capture_output=True, text=True, encoding="utf-8")
    assert proces.returncode == 0
    assert proces.stdout.split()[:3] == ["2", "2", "5"]
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
.......                                                                  [100%]
7 passed in 0.21s
```

Testy jednostkowe wywołują `main()` z listą argumentów wskazującą katalog tymczasowy `tmp_path` i czytają oba strumienie przez `capsys` z rozdziału 16 „Python Notatki”; błąd użycia to `SystemExit` z kodem `2`, którego oczekujemy jawnie. Jeden test integracyjny uruchamia narzędzie jako proces z tekstem na `stdin` — sprawdza to, czego `main()` w procesie testów nie pokaże: blok strażnika, `sys.exit()` i czytanie `sys.stdin`. Ustawienia z pliku i środowiska testuje się tak samo, z `monkeypatch.setenv()` dla zmiennych i plikiem TOML w `tmp_path`.

## Polecenie w pakiecie

Skrypt z `main(argv=None)` staje się poleceniem tak, jak w [rozdziale 17](../17-pakowanie/pakiet.md#instalacja-edytowalna-i-polecenia): moduł trafia do pakietu w układzie `src`, a `pyproject.toml` dostaje punkt wejścia:

```toml title="fragment pyproject.toml"
[project.scripts]
porzadek = "narzedzia.porzadek:main"
licznik = "narzedzia.licznik:main"
```

Po `python -m pip install -e .` polecenia są dostępne w środowisku, po `pipx install` — w każdym terminalu, a archiwum `zipapp` przenosi narzędzie na komputer z samym Pythonem. Blok strażnika w każdym module pozwala dodatkowo uruchamiać `python -m narzedzia.porzadek`, a pakiet z jednym narzędziem może dostać plik `__main__.py` z `sys.exit(main())`, skracający to do `python -m narzedzia` — bywa to jedyna droga, gdy katalog `Scripts` środowiska nie jest na ścieżce. Nazwa polecenia powinna być krótka, bez rozszerzenia `.py` i bez podkreśleń — użytkownik będzie ją pisał wiele razy.

## Alternatywy

`argparse` wystarcza do narzędzi z tego rozdziału i nie wymaga instalacji. Biblioteki zewnętrzne skracają zapis: Click opisuje opcje dekoratorami funkcji, Typer wyprowadza je z adnotacji typów — jak FastAPI z rozdziału 15 — a `rich` dodaje kolorowe tabele i paski postępu na terminalu. Warto po nie sięgnąć, gdy narzędzie ma wiele podpoleceń i opcji; interfejs — strumienie, kody wyjścia, konfiguracja — pozostaje ten sam.

## Lista kontrolna

- **`main(argv=None)`** zwracające kod, `sys.exit(main())` pod strażnikiem; parser w osobnej funkcji.
- **Wynik na `stdout`, komunikaty na `stderr`**; `-q`/`-v` zmieniają tylko dziennik.
- **Kody wyjścia**: `0` sukces, `1` błąd wykonania, `2` błąd użycia, `130` przerwanie.
- **`stdin` i `-`** dla filtrów; błąd jednego pliku nie przerywa pozostałych.
- **`--dry-run`** dla operacji na plikach; `--config` i zmienne środowiskowe z przedrostkiem; argumenty wygrywają.
- **`subprocess.run()`** z listą argumentów, `check`, `timeout`, `capture_output`, `sys.executable` dla Pythona.
- **UTF-8** jawnie: pliki z `encoding`, strumienie z `PYTHONUTF8` albo `reconfigure()`.
- **Testy** przez `main(argv)` z `tmp_path` i `capsys`; jeden test procesu.

## Dalej: pobieranie stron

[Następny rozdział](../21-scraping/index.md) buduje narzędzia, które sięgają po dane do sieci — pobierają strony klientem httpx z rozdziału 14 i wyciągają z nich informacje parserem HTML; projekt ścieżki połączy pobieranie, przetwarzanie i raport w jedno narzędzie wiersza poleceń zbudowane według reguł z tego rozdziału <!-- TODO: link po powstaniu rozdziału o projekcie narzędzia automatyzującego -->.
