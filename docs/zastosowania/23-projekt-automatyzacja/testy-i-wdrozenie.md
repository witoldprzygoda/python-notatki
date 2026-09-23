# Testy i wdrożenie

Narzędzie z harmonogramu pracuje bez nadzoru, więc testy i dziennik są jedynym sposobem, by wiedzieć, że działa.

## Testy

```python title="tests/test_monitor.py"
from pathlib import Path

import pytest

from monitor import analiza, historia
from monitor.cli import main
from sklep_serwer import uruchom
from zbuduj_sklep import zbuduj

SKLEP = Path(__file__).parent.parent / "sklep"


@pytest.fixture(scope="module")
def adres():
    zbuduj(SKLEP)
    serwer, adres = uruchom(SKLEP)
    yield adres
    serwer.shutdown()


def test_porownanie_pomiarow():
    poprzedni = {"AGD-001": ("Czajnik", 149.0), "AGD-002": ("Toster", 199.0), "AGD-003": ("Ekspres", None)}
    biezacy = {"AGD-001": ("Czajnik", 149.0), "AGD-002": ("Toster", 179.1), "AGD-004": ("Waga", 69.99)}
    wynik = analiza.porownaj(poprzedni, biezacy)
    assert wynik["zmiany"] == [{"sku": "AGD-002", "nazwa": "Toster", "stara": 199.0, "nowa": 179.1, "procent": -10.0}]
    assert wynik["nowe"] == ["AGD-004"] and wynik["brakujace"] == ["AGD-003"]


def test_poprawne_sku():
    dobre, odrzucone = analiza.poprawne_sku([{"sku": "AGD-001"}, {"sku": "x1"}])
    assert [rekord["sku"] for rekord in dobre] == ["AGD-001"] and odrzucone == ["x1"]


def test_historia_w_bazie(tmp_path):
    polaczenie = historia.otworz(tmp_path / "test.sqlite")
    historia.zapisz_pomiar(polaczenie, "2026-09-22 08:00", [{"sku": "AGD-001", "nazwa": "Czajnik", "cena": 149.0}])
    historia.zapisz_pomiar(polaczenie, "2026-09-23 08:00", [{"sku": "AGD-001", "nazwa": "Czajnik", "cena": None}])
    assert historia.pomiary(polaczenie) == ["2026-09-22 08:00", "2026-09-23 08:00"]
    assert historia.pomiar(polaczenie, "2026-09-23 08:00") == {"AGD-001": ("Czajnik", None)}
    assert historia.historia_produktu(polaczenie, "AGD-001") == [("2026-09-22 08:00", 149.0), ("2026-09-23 08:00", None)]
    polaczenie.close()


def test_pobierz_i_raport(adres, tmp_path, capsys):
    baza = str(tmp_path / "monitor.sqlite")
    assert main(["--baza", baza, "pobierz", adres + "index.html", "--opoznienie", "0", "--czas", "2026-09-22 08:00"]) == 0
    assert main(["--baza", baza, "raport", "-o", str(tmp_path)]) == 1
    assert main(["--baza", baza, "pobierz", adres + "index.html", "--opoznienie", "0", "--czas", "2026-09-23 08:00"]) == 0
    assert main(["--baza", baza, "raport", "-o", str(tmp_path)]) == 0
    assert (tmp_path / "monitor-cen.xlsx").exists() and (tmp_path / "monitor-cen.docx").exists()
    wyjscie = capsys.readouterr()
    assert "Zapisano pomiar 2026-09-22 08:00: 10 produktów" in wyjscie.out and "Raport: zmian cen 0" in wyjscie.out
    assert "dwóch pomiarów" in wyjscie.err
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
....                                                                     [100%]
4 passed in 1.37s
```

Analizę i historię testujemy bez sieci: porównanie na słownikach wpisanych w test, bazę w `tmp_path`. Test narzędzia buduje sklep od nowa (po przebiegu z poprzedniej strony pliki są zmienione), uruchamia serwer raz na moduł i wywołuje `main()` z listą argumentów, sprawdzając kody wyjścia, oba strumienie i istnienie plików raportu. Wpis `pythonpath` w `pyproject.toml` dodaje katalog projektu do ścieżki importu, więc pakiet `monitor` i moduły sklepu są widoczne niezależnie od katalogu, z którego uruchamiamy testy.

## Instalacja polecenia

```powershell title="Terminal"
python -m pip install -e .
monitor-cen --help
pipx install .
```

Instalacja edytowalna z rozdziału 17 daje polecenie `monitor-cen` w środowisku projektu, a `pipx` — w każdym terminalu, z osobnym środowiskiem i zależnościami z `pyproject.toml`. Po instalacji narzędzie uruchamiamy z dowolnego katalogu; plik bazy i katalog raportów podajemy wtedy pełnymi ścieżkami.

## Harmonogram zadań

```powershell title="Terminal"
schtasks /Create /SC DAILY /ST 08:00 /TN "Monitor cen" /TR "C:\Users\jan\.local\bin\monitor-cen.exe --baza C:\Users\jan\monitor\monitor.sqlite --dziennik C:\Users\jan\monitor\monitor.log pobierz https://sklep.example.com/"
```

```text title="crontab"
0 8 * * * /home/jan/.local/bin/monitor-cen --baza /home/jan/monitor/monitor.sqlite --dziennik /home/jan/monitor/monitor.log pobierz https://sklep.example.com/
```

Harmonogram zadań Windows (`schtasks`, także okno „Harmonogram zadań”) i `cron` na Linuksie (wpis dodajemy poleceniem `crontab -e`) uruchamiają polecenie o ustalonej porze; zadanie utworzone bez opcji `/RU` działa tylko przy zalogowanym użytkowniku. Trzy zasady: ścieżki bezwzględne, bo zadanie nie ma katalogu projektu ani aktywowanego środowiska; polecenie zainstalowane przez `pipx`, bo ma własne środowisko, niezależne od katalogu projektu; dziennik w pliku, bo `stderr` zadania nikt nie zobaczy. Raport tworzymy osobnym zadaniem po pomiarze albo ręcznie, gdy jest potrzebny.

## Dziennik w pliku

Wpis z datą, poziomem i treścią pozwala po tygodniu odtworzyć, co narzędzie robiło: kiedy pobierało, ile produktów zapisało, kiedy serwer nie odpowiadał. Poziom `-v` zapisuje każde pobranie — przy codziennym pomiarze kilkunastu stron plik rośnie wolno; przy tysiącach stron zostawiamy poziom ostrzeżeń albo dodajemy rotację pliku (`RotatingFileHandler` z modułu `logging.handlers`). Wyjątek nieobsłużony trafia do dziennika tylko wtedy, gdy go tam zapiszemy — `dziennik.exception()` w `main()` wokół wywołania podpolecenia jest w narzędziu bez nadzoru jedynym zapisem takiego błędu.

## Lista kontrolna

- **Wymagania przed kodem**: co narzędzie robi, skąd bierze dane, co zapisuje, jak sygnalizuje błędy.
- **Moduły o jednym zadaniu**, dane między nimi jako słowniki i listy; moduły z poprzednich rozdziałów kopiowane bez zmian.
- **Pomiar w jednej transakcji**; chwila pomiaru jako tekst ISO; identyfikatory sprawdzone wzorcem.
- **Raport z dwóch ostatnich pomiarów**; błąd zamiast pustego raportu.
- **Podpolecenia** z opcjami wspólnymi przed nazwą podpolecenia; `--czas` dla powtarzalności; `--dziennik` dla harmonogramu.
- **Testy bez sieci** dla modułów, na serwerze testowym dla narzędzia; sklep odtwarzany przed testem.
- **Wdrożenie**: `pipx`, ścieżki bezwzględne, harmonogram, dziennik w pliku.

## Zakończenie części

Ścieżka Automatyzacja prowadziła od wzorców tekstu, przez narzędzia wiersza poleceń i pobieranie stron, do plików Office i tego projektu. Razem z pozostałymi ścieżkami — danymi, uczeniem maszynowym i aplikacjami — zamyka część „Python Zastosowania”: dwadzieścia trzy rozdziały, w których biblioteki poznane osobno składają się w programy do prawdziwych zadań. Dalej pozostają dokumentacja bibliotek, własne projekty i zadania, których ta książka nie przewidziała — z warsztatem, który pozwala je rozwiązać.
