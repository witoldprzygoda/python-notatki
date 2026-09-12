# 7. Moduły, pakiety i biblioteka standardowa

Dotychczas każdy program mieścił się w jednym pliku. Ten rozdział prowadzi od pojedynczego pliku do **projektu**: plik z kodem staje się modułem, który inne pliki importują; ten sam plik może być raz modułem, a raz programem uruchamianym z terminala i przyjmującym argumenty; moduły układają się w pakiety, a pakiet — razem z testami i opisem projektu w `pyproject.toml` — w projekt, który można zainstalować w środowisku wirtualnym i uruchamiać z dowolnego miejsca. Mechanizmem spinającym wszystkie te kroki jest instrukcja `import`, dlatego rozdział zaczyna się od dokładnego modelu jej działania: moduł jako obiekt z własną przestrzenią nazw, jednokrotne wykonanie kodu przy pierwszym imporcie, pamięć podręczna modułów i ścieżka wyszukiwania.

Rozdział domyka wątki otwarte wcześniej. Środowisko wirtualne, pip i lista `sys.path` z rozdziału [1. Instalacja i środowisko pracy](../01-instalacja/venv.md) wracają przy instalacji własnego pakietu; uruchamianie modułu przez `python -m` z rozdziału [2. Konsola](../02-konsola/pierwszy-skrypt.md) staje się regułą pracy z pakietami; a zapowiedzi z rozdziału [6. Funkcje](../06-funkcje/index.md) — gotowa memoizacja, dekorator zachowujący metadane, narzędzia do iteratorów nieskończonych, funkcje sterujące limitem rekurencji — spełniają trzy ostatnie podrozdziały poświęcone bibliotece standardowej. Od tej chwili wiele nowych tematów książki zaczyna się od importu kolejnego modułu biblioteki standardowej.

---

## W tym rozdziale

1. [Moduły i instrukcja import](moduly-i-import.md) — moduł jako plik i jako obiekt, formy instrukcji import, przestrzeń nazw modułu, wykonywanie kodu podczas importu, `sys.modules` i `sys.path`, pułapki importu
2. [Skrypt jako program](skrypt-jako-program.md) — atrybut `__name__` i nazwa `"__main__"`, strażnik uruchomienia, konwencja `main()`, uruchamianie przez `python -m`
3. [Argumenty wiersza poleceń](argumenty-wiersza-polecen.md) — lista `sys.argv`, moduł `argparse`, automatyczna pomoc, kody wyjścia i `sys.exit()`
4. [Pakiety](pakiety.md) — katalog jako pakiet, plik `__init__.py`, importy absolutne i względne, `__main__.py`, pakiety przestrzeni nazw
5. [Struktura projektu i pierwsze testy](struktura-projektu.md) — instrukcja `assert`, katalog `tests`, pytest, układ `src` i `pyproject.toml`, instalacja edytowalna
6. [Biblioteka standardowa i moduł collections](biblioteka-standardowa.md) — spis modułów i dokumentacja, moduł `sys`, typy `deque`, `Counter`, `defaultdict` i `namedtuple`
7. [Moduł functools](functools.md) — dekoratory `cache` i `lru_cache`, dekorator `wraps`, funkcja `partial`, funkcja `reduce`
8. [Moduł itertools](itertools.md) — podrozdział uzupełniający: iteratory nieskończone, `islice` i `chain`, `pairwise` i `batched`, `accumulate`, `groupby`, kombinatoryka
