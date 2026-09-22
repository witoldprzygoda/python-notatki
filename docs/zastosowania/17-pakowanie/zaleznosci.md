# Zależności i wersje

Pakiet, który czegoś wymaga, musi to zadeklarować tak, by pip zainstalował właściwe wersje — nie za stare, by działał, i nie tak nowe, by przestał. Ten podrozdział porządkuje **specyfikatory wersji** (ang. *version specifier*) w zapisie zależności, różnicę między zależnościami pakietu a plikiem wymagań projektu oraz numerowanie własnych wersji.

## Specyfikatory wersji

```python title="wersje.py"
from importlib.metadata import requires, version

from packaging.specifiers import SpecifierSet
from packaging.version import Version

print(Version("1.10") > Version("1.9"), Version("2.0.0rc1") < Version("2.0.0"), Version("1.0.post1") > Version("1.0"))
wymagania = SpecifierSet(">=1.9,<2")
print([wersja for wersja in ("1.8.2", "1.9", "1.12.3", "2.0") if wersja in wymagania])
print(SpecifierSet("~=1.9").contains("1.15"), SpecifierSet("~=1.9").contains("2.0"), SpecifierSet("==1.9.*").contains("1.9.7"))
print(requires("kontakty"), version("pytest"), version("build"))
```

```{ .text .no-copy }
True True True
['1.9', '1.12.3']
True False True
["pytest>=9; extra == 'test'"] 9.1.1 1.6.1
```

| Specyfikator | Znaczenie |
|---|---|
| `pakiet` | dowolna wersja — pip bierze najnowszą |
| `pakiet>=1.9` | co najmniej 1.9 |
| `pakiet>=1.9,<2` | 1.9 lub nowsza, ale poniżej 2.0 — zwykły zapis dla bibliotek |
| `pakiet~=1.9` | „zgodna z 1.9”: `>=1.9,<2` (ostatni podany człon może rosnąć) |
| `pakiet==1.9.7` | dokładnie ta wersja — do plików wymagań i blokady |
| `pakiet==1.9.*` | dowolna 1.9.x |
| `pakiet!=1.10.0` | z wyłączeniem wersji z błędem |
| `pakiet[dodatek]>=1.9` | z grupą zależności opcjonalnych |

Numery wersji porównuje się według standardu PEP 440, nie jak teksty: `1.10` jest nowsze od `1.9`, `2.0.0rc1` (kandydat do wydania) starsze od `2.0.0`, a `1.0.post1` (poprawka wydania) nowsze od `1.0`; pakiet `packaging` — ten sam, którego używa pip — udostępnia te reguły w `Version` i `SpecifierSet`, a `importlib.metadata.version()` podaje wersje zainstalowanych pakietów. Większość bibliotek stosuje **wersjonowanie semantyczne** (ang. *semantic versioning*): `GŁÓWNA.MNIEJSZA.POPRAWKOWA`, jak w rozdziale 1 tej części: wersja poprawkowa nie zmienia zachowania, mniejsza dodaje bez usuwania, a główna może łamać zgodność — stąd typowy zapis `>=1.9,<2`: bierzemy poprawki i nowości, nie bierzemy zmian niezgodnych. Nie każdy projekt się tego trzyma (NumPy usuwa wycofane funkcje w wydaniach mniejszych, a pandas dopuszcza w nich poprawki zmieniające zachowanie), więc górne ograniczenie ustalamy według tego, co sprawdziliśmy.

## Zależności pakietu a plik wymagań

W projekcie występują trzy listy o różnym przeznaczeniu:

| Lista | Gdzie | Co zawiera |
|---|---|---|
| `dependencies` | `pyproject.toml` | to, czego pakiet potrzebuje do działania u każdego odbiorcy; zakresy, nie dokładne wersje |
| `requirements.txt` | katalog projektu | narzędzia środowiska programisty: pytest, build, PyInstaller; dokładne wersje |
| plik blokady | katalog projektu (`requirements-lock.txt`) | pełny wydruk `pip freeze` — wszystko, co jest zainstalowane, z zależnościami zależności |

Biblioteka z `dependencies = ["httpx==0.28.1"]` uniemożliwiłaby instalację obok każdego pakietu, który wymaga innej wersji httpx; zakres `httpx>=0.27,<1` pozostawia pip swobodę doboru wersji. Odwrotnie w aplikacji wdrażanej na serwer albo pakowanej w plik wykonywalny: tam liczy się powtarzalność, więc obok zakresów w `pyproject.toml` trzymamy **plik blokady** (ang. *lock file*) z dokładnymi wersjami wszystkiego (bez instalacji edytowalnej, która wskazuje lokalny katalog), odtwarzany przez `python -m pip install -r requirements-lock.txt` — jak w rozdziale 1 tej części. Po każdej zmianie zależności sprawdzamy spójność środowiska poleceniem `python -m pip check`, które wypisuje pakiety z niespełnionymi wymaganiami, a dostępne wersje pokazuje `python -m pip index versions nazwa`.

```powershell title="Terminal"
python -m pip check
python -m pip freeze --exclude-editable > requirements-lock.txt
```

## Zależności opcjonalne

Grupy w `[project.optional-dependencies]` — **zależności opcjonalne** (ang. *optional dependencies*, *extras*) — opisują potrzeby, które nie dotyczą każdego odbiorcy: `test = ["pytest>=9"]` dla programisty, w innych projektach `excel = ["openpyxl"]` dla użytkowników czytających arkusze albo `wykresy = ["matplotlib"]`. Odbiorca wybiera grupę w nawiasach kwadratowych — `python -m pip install "kontakty[test]"` — a w metadanych zależność dostaje znacznik `extra == 'test'`, który widać w wydruku `requires()`. Kod pakietu, który używa zależności opcjonalnej, importuje ją dopiero w funkcji i zgłasza zrozumiały błąd, gdy jej brak:

```python title="fragment"
def zapisz_xlsx(kontakty, sciezka):
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("zapis do XLSX wymaga instalacji: pip install kontakty[excel]") from None
    ...
```

## Wersja w jednym miejscu

Numer wersji jest potrzebny w trzech miejscach: w metadanych pakietu, w programie (`--wersja`, tytuł okna) i w nazwie pliku w `dist`. W naszym pakiecie źródłem jest `__version__` w `src/kontakty/__init__.py`: Hatchling czyta je przy budowaniu dzięki `[tool.hatch.version]`, kod importuje je wprost, a `importlib.metadata.version("kontakty")` zwraca to samo po instalacji. Alternatywa — `version = "0.1.0"` w `pyproject.toml` i odczyt przez `importlib.metadata` w kodzie — zawodzi tam, gdzie pakiet nie jest zainstalowany, na przykład w archiwum zipapp z następnej strony. Wydanie nowej wersji to zmiana jednej linii, uruchomienie testów, `python -m build` po opróżnieniu katalogu `dist` (inaczej `twine upload dist/*` wysłałby także stare pliki) i publikacja; wersje `0.x` sygnalizują, że interfejs może się jeszcze zmieniać, a `1.0` — zobowiązanie do zgodności w obrębie wersji głównej.
