# Testowanie z pytest — techniki zaawansowane

W rozdziale 7 poznaliśmy pytest w podstawowym zakresie: funkcje `test_*` z instrukcją `assert`, katalog `tests`, uruchomienie poleceniem `python -m pytest`, a w rozdziale 8 — `pytest.raises()` do testowania wyjątków. Ten podrozdział dodaje techniki, bez których testy większego projektu szybko stają się nieczytelne: fixture, parametryzację, wspólną konfigurację w `conftest.py`, markery, wybór testów do uruchomienia i pomiar pokrycia kodu. Na koniec — atrapy, które uniezależniają testy od sieci i innych zależności zewnętrznych.

## Przypomnienie i przykładowy moduł

Przykłady testują niewielki moduł z dwiema funkcjami; dla zwięzłości leży on w tym samym katalogu co testy — układ `src` z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/struktura-projektu.md#ukad-src-i-plik-pyprojecttoml) działa tak samo:

```python title="kolo.py"
import math


def pole_kola(promien: float) -> float:
    if promien < 0:
        raise ValueError("promień nie może być ujemny")
    return math.pi * promien**2


def sredni_promien(promienie: list[float]) -> float | None:
    if not promienie:
        return None
    return sum(promienie) / len(promienie)
```

Konfigurację pytest trzymamy w `pyproject.toml`; sekcja `markers` przyda się w dalszej części:

```toml title="pyproject.toml"
[tool.pytest.ini_options]
markers = ["wolny: testy trwające dłużej niż sekundę"]
```

## Fixture

**Fixture** to funkcja przygotowująca dane lub zasób dla testu; pytest wywołuje ją automatycznie, gdy test ma parametr o tej samej nazwie, i przekazuje jej wynik. Fixture z `yield` — funkcja generatorowa z rozdziału 6 — wykonuje część przed `yield` przed testem, a część po nim po teście, niezależnie od jego wyniku:

```python title="test_fixtures.py"
import os

import pytest


@pytest.fixture
def plik_z_liczbami(tmp_path):
    sciezka = tmp_path / "dane.txt"
    sciezka.write_text("1\n2\n3\n", encoding="utf-8")
    yield sciezka
    print("sprzątanie po teście")


def test_suma_z_pliku(plik_z_liczbami):
    liczby = [int(w) for w in plik_z_liczbami.read_text(encoding="utf-8").split()]
    assert sum(liczby) == 6


def test_wydruk(capsys):
    print("witaj")
    assert capsys.readouterr().out == "witaj\n"


def test_zmienna_srodowiskowa(monkeypatch):
    monkeypatch.setenv("TRYB", "test")
    assert os.environ["TRYB"] == "test"
```

```powershell title="Terminal"
python -m pytest -q -s test_fixtures.py
```

```{ .text .no-copy }
.sprzątanie po teście
..
3 passed in 0.02s
```

Fixture `plik_z_liczbami` sama korzysta z fixture wbudowanej `tmp_path` — obiektu `Path` z rozdziału 9 wskazującego katalog tymczasowy, osobny dla każdego testu; pytest zachowuje katalogi z trzech ostatnich sesji, starsze usuwa. Dwie inne wbudowane fixture: `capsys` przechwytuje to, co test wypisał na standardowe wyjście, a `monkeypatch` tymczasowo podmienia zmienne środowiskowe, atrybuty obiektów i elementy modułów, przywracając je po teście. Opcja `-s` wyłącza przechwytywanie wydruków, dlatego widać komunikat ze sprzątania; `-q` skraca raport. Domyślnie fixture jest tworzona na nowo dla każdego testu; argument `scope="module"` albo `scope="session"` tworzy ją raz — dla zasobów kosztownych, jak połączenie z bazą danych.

## Parametryzacja

Dekorator `@pytest.mark.parametrize` uruchamia jedną funkcję testową dla wielu zestawów danych; każdy zestaw jest osobnym testem z własnym identyfikatorem:

```python title="test_kolo.py"
import math

import pytest

from kolo import pole_kola, sredni_promien


@pytest.mark.parametrize(
    ("promien", "pole"),
    [(0, 0.0), (1, math.pi), (2, 4 * math.pi)],
    ids=["zero", "jednostkowe", "podwojne"],
)
def test_pole_kola(promien, pole):
    assert pole_kola(promien) == pytest.approx(pole)


def test_ujemny_promien():
    with pytest.raises(ValueError, match="ujemny"):
        pole_kola(-1)


def test_sredni_promien(promienie):
    assert sredni_promien(promienie) == 2.0


def test_pusta_lista():
    assert sredni_promien([]) is None


@pytest.mark.wolny
def test_wolny():
    assert sum(range(10_000)) == 49995000
```

Pierwszy argument dekoratora to nazwy parametrów, drugi — lista zestawów wartości, a `ids=` nadaje zestawom czytelne nazwy zamiast domyślnych `0-0.0`. `pytest.approx()` porównuje liczby zmiennoprzecinkowe z tolerancją — odpowiednik `math.isclose()` z rozdziału 7 — a `pytest.raises()` z argumentem `match=` znamy z podrozdziału [Styl obsługi błędów i testy wyjątków](../08-wyjatki/styl-i-testowanie.md) rozdziału 8. Test `test_sredni_promien` korzysta z fixture `promienie`, której nie ma w tym pliku — pochodzi z pliku `conftest.py`, omówionego w następnej sekcji; dlatego cały zestaw uruchamiamy dopiero tam.

## `conftest.py` i markery

Plik `conftest.py` w katalogu testów zawiera fixture dostępne dla wszystkich testów w tym katalogu i podkatalogach, bez importowania — pytest odnajduje go sam:

```python title="conftest.py"
import pytest


@pytest.fixture
def promienie():
    return [1.0, 2.0, 3.0]
```

```powershell title="Terminal"
python -m pytest -v
```

```{ .text .no-copy }
============================= test session starts =============================
...
collected 10 items

test_fixtures.py::test_suma_z_pliku PASSED                               [ 10%]
test_fixtures.py::test_wydruk PASSED                                     [ 20%]
test_fixtures.py::test_zmienna_srodowiskowa PASSED                       [ 30%]
test_kolo.py::test_pole_kola[zero] PASSED                                [ 40%]
test_kolo.py::test_pole_kola[jednostkowe] PASSED                         [ 50%]
test_kolo.py::test_pole_kola[podwojne] PASSED                            [ 60%]
test_kolo.py::test_ujemny_promien PASSED                                 [ 70%]
test_kolo.py::test_sredni_promien PASSED                                 [ 80%]
test_kolo.py::test_pusta_lista PASSED                                    [ 90%]
test_kolo.py::test_wolny PASSED                                          [100%]

============================= 10 passed in 0.06s ==============================
```

**Marker** to etykieta testu: `@pytest.mark.wolny` oznacza test długi, a własne markery rejestrujemy w `pyproject.toml` (sekcja z początku podrozdziału), inaczej pytest ostrzega o nieznanej nazwie. Markery wbudowane: `skip(reason=…)` pomija test, `skipif(warunek, reason=…)` pomija go warunkowo — na przykład na innym systemie operacyjnym — a `xfail` oznacza test, którego niepowodzenie jest znane i oczekiwane; w raporcie taki test pojawia się jako `x`, nie jako błąd.

## Uruchamianie i pokrycie kodu

Kilka opcji wiersza poleceń wystarcza w codziennej pracy:

| Opcja | Działanie |
|---|---|
| `-v` / `-q` | raport szczegółowy / skrócony |
| `-k pole` | tylko testy, których nazwa zawiera `pole` |
| `-m "not wolny"` | tylko testy bez markera `wolny` |
| `-x` | zatrzymanie po pierwszym niepowodzeniu |
| `--lf` | tylko testy, które ostatnio nie przeszły |
| `-s` | bez przechwytywania wydruków |

```powershell title="Terminal"
python -m pytest -q -k pole
python -m pytest -q -m "not wolny"
```

```{ .text .no-copy }
...                                                                      [100%]
3 passed, 7 deselected in 0.01s
.........                                                                [100%]
9 passed, 1 deselected in 0.03s
```

**Pokrycie kodu** (ang. *code coverage*) mierzy, które wiersze programu wykonały się podczas testów. Wtyczka (ang. *plugin*) pytest-cov dodaje opcję `--cov`:

```powershell title="Terminal"
python -m pip install pytest-cov
python -m pytest -q --cov=kolo --cov-report=term-missing
```

```{ .text .no-copy }
..........                                                               [100%]
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.7-final-0 _______________

Name      Stmts   Miss  Cover   Missing
---------------------------------------
kolo.py       9      0   100%
---------------------------------------
TOTAL         9      0   100%
10 passed in 0.09s
```

Kolumna `Missing` wskazuje wiersze, których żaden test nie wykonał — najczęściej gałęzie obsługi błędów. Raport `--cov-report=html` tworzy katalog `htmlcov` z podświetlonym kodem. Pokrycie jest wskazówką, nie celem: sto procent nie gwarantuje poprawności, bo test może wykonać wiersz, niczego o nim nie sprawdzając; braki pokrycia natomiast wskazują miejsca bez żadnego testu.

### Panel Testing w VSC

Visual Studio Code z rozszerzeniem Python z rozdziału 1 wykrywa testy pytest i pokazuje je w widoku **Testing** na pasku bocznym jako drzewo plików i funkcji; każdy test można uruchomić lub debugować osobno, a wynik pojawia się jako zielony lub czerwony znacznik przy funkcji. Konfigurację włącza polecenie **Python: Configure Tests** z palety poleceń (++ctrl+shift+p++), w którym wybieramy pytest i katalog testów.

<!-- TODO: screenshot — widok Testing w VSC z drzewem testów test_fixtures.py i test_kolo.py po uruchomieniu (zielone znaczniki), kadr: sam pasek boczny -->

## Atrapy — `monkeypatch` i `unittest.mock` (dla dociekliwych)

Test nie powinien łączyć się z siecią ani bazą danych: jest wtedy wolny, zawodny i zależny od serwerów zewnętrznych. Zależność zewnętrzną zastępujemy **atrapą** (ang. *mock*) — obiektem, który zastępuje prawdziwy i zwraca wartości ustalone w teście:

```python title="pogoda.py"
import json
import urllib.request


def pobierz_temperature(miasto: str) -> float:
    adres = f"https://example.invalid/pogoda/{miasto}"
    with urllib.request.urlopen(adres) as odpowiedz:
        return float(json.load(odpowiedz)["temperatura"])


def opis(miasto: str) -> str:
    try:
        temperatura = pobierz_temperature(miasto)
    except OSError:
        return f"{miasto}: brak danych"
    return f"{miasto}: {temperatura:.1f} °C"
```

```python title="test_pogoda.py"
from unittest.mock import Mock

import pogoda


def test_opis(monkeypatch):
    monkeypatch.setattr(pogoda, "pobierz_temperature", lambda miasto: 21.5)
    assert pogoda.opis("Nowy Sącz") == "Nowy Sącz: 21.5 °C"


def test_opis_bez_sieci(monkeypatch):
    atrapa = Mock(side_effect=OSError("brak połączenia"))
    monkeypatch.setattr(pogoda, "pobierz_temperature", atrapa)
    assert pogoda.opis("Nowy Sącz") == "Nowy Sącz: brak danych"
    atrapa.assert_called_once_with("Nowy Sącz")
```

```powershell title="Terminal"
python -m pytest -q test_pogoda.py
```

```{ .text .no-copy }
..                                                                       [100%]
2 passed in 0.05s
```

`monkeypatch.setattr(moduł, "nazwa", zamiennik)` podmienia funkcję w module na czas testu; pierwszy test wstawia zwykłą funkcję `lambda`, drugi — obiekt `Mock` z modułu `unittest.mock`, który przy wywołaniu zgłasza wyjątek podany w `side_effect` i pamięta, jak został wywołany (`assert_called_once_with()`). Podmieniamy nazwę **w module, który jej używa** — atrybut `pogoda.pobierz_temperature`, nie nazwę zaimportowaną do modułu testu — bo `opis()` sięga po funkcję przez globalną przestrzeń nazw modułu `pogoda`, zgodnie z mechanizmem importu z rozdziału 7; z tego samego powodu podmiana `urllib.request.urlopen` nie zadziałałaby, gdyby `pogoda.py` importował tę funkcję formą `from urllib.request import urlopen`. Podmieniamy przy tym `pobierz_temperature`, a nie `urlopen`, bo testujemy logikę `opis()`, nie sposób pobierania danych. Atrapy testują logikę wokół zależności; samą zależność sprawdzamy osobno, rzadziej, na przykład ręcznie lub w **teście integracyjnym** (ang. *integration test*) — korzystającym z prawdziwej zależności, oznaczonym własnym markerem i uruchamianym rzadziej.
