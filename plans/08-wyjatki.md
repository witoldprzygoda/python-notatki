# Rozdział 8. Wyjątki i zarządzanie zasobami — plan implementacyjny

Skondensowany projekt stron rozdziału 8 według `PLAN_ROZWOJU.md` (sekcja 4, „8. Wyjątki i zarządzanie zasobami”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/08-wyjatki` (z `dev` po integracji rozdziału 7, commit `29c3490`). Stan odniesienia: Python 3.14.7 w `.venv` projektu, MkDocs Material.

## Decyzje autora (12 IX 2026)

1. **Bez „Ściągi”.** `index.md` w układzie rozdziałów 6–7: wstęp prozą, `---`, `## W tym rozdziale`. Sekcja „Ściąga” usunięta z `PLAN_ROZWOJU.md`. Bez „Powiązanego laboratorium”.
2. **Struktura:** index + 6 podrozdziałów w kolejności: obsługa wyjątków → zgłaszanie wyjątków → styl obsługi błędów i testy wyjątków → instrukcja `with` i menedżery kontekstu → diagnostyka (ślad wywołań i debugger) → logowanie zamiast `print`.
3. **Zrzuty ekranu:** wyłącznie w `diagnostyka.md` (debugger VSC — trzy zrzuty: pułapka i wstrzymany wiersz, panele Variables/Call Stack, pasek narzędzi debugowania). W tekście znaczniki `<!-- TODO: screenshot — … -->`, wpisy w `ZRZUTY.md` (kadr ciasny, motyw jasny); zrzuty wykonuje autor. Pozostałe treści (ślady wywołań, sesje pdb, wyniki pytest, dziennik logging) jako bloki tekstowe.
4. **Długość stron:** szacunek z `PLAN_ROZWOJU.md` (800–900 linii) traktujemy jako orientacyjny i zaniżony; przy gęstości rozdziałów 6–7 spodziewany rozmiar to ok. 1600–2000 linii. O długości decyduje kompletność merytoryczna, przykłady i wyniki wykonania.
5. **Zakres `logging`:** konsola (`stderr`), poziomy, `basicConfig(level=, format=, datefmt=)`, `getLogger(__name__)`, `exception()`, leniwe formatowanie `%s`. Dziennik w pliku (`filename=`, `encoding="utf-8"`) tylko jako zapowiedź rozdziału 9; logowanie z wątków — zapowiedź rozdziału 15; konfiguracja słownikowa i handlery poza książką (co najwyżej jedno zdanie).
6. **Własne typy wyjątków:** wyłącznie zapowiedź w admonition na stronie 2 (definicja klasy w rozdziale 10, `dziedziczenie.md`). Wszystkie przykłady zgłaszają wyjątki wbudowane (`ValueError`, `TypeError`, `RuntimeError`, `ZeroDivisionError`, `KeyError`, `FileNotFoundError`).
7. **Składnia `except` z kilkoma typami:** forma kanoniczna w książce to krotka w nawiasach `except (ValueError, TypeError):` — działa na każdej wersji i jest jedyną dopuszczalną z `as`. Forma bez nawiasów z PEP 758 (3.14) pokazana raz, z komunikatem `SyntaxError: multiple exception types must be parenthesized when using 'as'` jako uzasadnieniem zalecenia.
8. **Nazwa obiektu wyjątku:** `except ValueError as e:` — nazwa `e` przyjęta powszechnie w kodzie Pythona (decyzja autora 13 IX 2026: bez wymuszania polskich nazw); w teście pytest nazwa `excinfo` z dokumentacji pytest.
9. **Nazwa strony diagnostycznej:** etykieta nav i H1 „Diagnostyka — ślad wywołań (traceback) i debugger” (decyzja autora 13 IX 2026; termin „ślad wywołań (ang. *traceback*)” wprowadzony w rozdziale 6).
10. **`open()` jako czarna skrzynka:** na stronie 4 jedno wywołanie `open("dane.txt", encoding="utf-8")` do odczytu pliku dostarczonego w bloku `text title="dane.txt"` oraz `open("brak.txt", encoding="utf-8")` jako źródło `FileNotFoundError`. Bez zapisu do plików, bez trybów, bez `pathlib`/`os`/`tempfile` — wszystko to należy do rozdziału 9. Przykład z W08 (`temp_dir` z `tempfile`/`shutil`) pominięty.
11. **Pomiar czasu:** menedżer kontekstu `stoper()` z `@contextlib.contextmanager` używa `time.perf_counter()`, wprowadzonego w miejscu użycia jednym zdaniem (zegar o wysokiej rozdzielczości do pomiaru odstępów), z zapowiedzią: „szczegółowe omówienie pomiarów czasu i profilowania znajdzie się w rozdziale o wydajności” — **bez numeru rozdziału**, z komentarzem `<!-- TODO: link po powstaniu rozdziału o wydajności -->` (konwencja książki: zapowiedzi w przód prozą po temacie, numery tylko dla rozdziałów istniejących; komentarze wyszukiwane grepem i domykane zbiorczo przy pisaniu danego rozdziału). Zapowiedź zarejestrowana w `PLAN_ROZWOJU.md`, sekcja 13 „Zapowiedzi i luki, które rozdział domyka”. Wynik pomiaru w bloku wyniku oznaczony jako zależny od komputera.
12. **Debugger:** rozszerzenie **Python Debugger** (`ms-python.debugpy`, instalowane automatycznie z rozszerzeniem Python), uruchomienie bez `launch.json` (++f5++ → wybór „Python File”), pułapki w marginesie, pasek F5/F10/F11/++shift+f11++, panele Variables, Watch, Call Stack, Debug Console; minimalny `launch.json` z `"type": "debugpy"` (dawny `"type": "python"` jest przestarzały), `"console": "integratedTerminal"`, `"args"`, `"justMyCode"`. `breakpoint()` i pdb w zakresie poleceń `n`, `s`, `c`, `p`, `l`, `q`; `PYTHONBREAKPOINT=0` jednym zdaniem; PEP 768 (`sys.remote_exec()`, `python -m pdb -p PID`) wyłącznie jako nota „Nowości Pythona 3.14”.
13. **Bez Gita, GitHub i CI** (zasada 9 `PLAN_ROZWOJU.md`); bez `unittest`, `doctest`, `warnings.warn()` (jedno zdanie w tabeli „kiedy logować”), bez `atexit`, bez `signal`.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez `class` (własne wyjątki, `__enter__`/`__exit__` jako klasa, `__str__` — wyłącznie prozą i w zapowiedziach, rozdziały 10–11), bez zapisu do plików, `pathlib`, `os`, `shutil`, `tempfile`, `io` (rozdział 9), bez wątków (rozdział 15), bez `dataclass`. `open()` wyłącznie w zakresie decyzji 10.
- Moduły biblioteki standardowej użyte w kodzie: `sys` (`sys.exit()`, `sys.exception()` nie), `math`, `contextlib`, `traceback`, `logging`, `time` (tylko `perf_counter()`, decyzja 11); pytest (tylko `pytest.raises`, strona 3, w tymczasowym venv). Żaden inny moduł nie pojawia się w kodzie; `re` w prozie przy `match=` (jedno zdanie: wzorzec jest wyrażeniem regularnym, w praktyce zwykłym fragmentem tekstu), `warnings`, `unittest`, `pdb` (jako nazwa modułu i sesja), `debugpy` (nazwa) prozą.
- Kolejność wewnątrz rozdziału jest bezwzględna: strona 1 tylko obsługuje wyjątki wbudowane; `raise` od strony 2; `pytest.raises` na stronie 3 (wymaga `raise` i pytest z rozdziału 7); `with` na stronie 4 (wymaga `try/finally` ze strony 1, generatorów i dekoratorów z rozdziału 6); strona 5 zakłada znajomość łańcuchów wyjątków ze strony 2; strona 6 zakłada `except` i `raise`.
- Pojęcia wprowadzane jawnie w miejscu pierwszego użycia: „nieprzechwycony wyjątek” i jego skutek (ślad na `stderr`, kod wyjścia 1 — przypomnienie z rozdziału 7); „propagacja” przez stos wywołań; „przechwycenie” a „obsługa”; `__debug__` (strona 2); „zasób” i „zwolnienie zasobu” (strona 4); „pułapka (ang. *breakpoint*)”; „dziennik (ang. *log*)”; „poziom komunikatu”.
- Ślady wywołań: każdy odtworzony na 3.14.7 jako pełny blok `{ .text .no-copy }` (nagłówek `Traceback (most recent call last):`, ramki z `~~~^^^`, komunikat); ścieżki skrócone do nazwy pliku zgodnie z regułą z `06-funkcje/definiowanie-funkcji.md:52`; łańcuchy z pełnymi separatorami „The above exception was the direct cause of the following exception:” i „During handling of the above exception, another exception occurred:”; podpowiedź „Did you mean: 'math'?” pokazana raz, ze stwierdzeniem, że jest częścią renderowania śladu (w `str(blad)` jej nie ma) i że jej brzmienie zmienia się z wersji na wersję; kolorowanie śladów (3.13+, `PYTHON_COLORS`, `NO_COLOR`) wyłącznie prozą. Ślady z REPL z numeracją `<python-input-N>` liczoną od zera w obrębie sesji.
- `SyntaxWarning` PEP 765 (`'return' in a 'finally' block`) i `SyntaxError` PEP 758 pokazane jako pełne komunikaty kompilatora, uruchomione na 3.14.7.
- Terminologia: „wyjątek”, „zgłoszenie wyjątku (ang. *raise*)”, „przechwycenie (ang. *catch*)”, „obsługa wyjątku (ang. *exception handling*)”, „propagacja”, „ślad wywołań (ang. *traceback*)”, „klauzula `except`/`else`/`finally`”, „łańcuch wyjątków (ang. *exception chaining*)”, „przyczyna (`__cause__`)” i „kontekst (`__context__`)” tylko w nocie, „hierarchia wyjątków”, „styl EAFP (ang. *easier to ask forgiveness than permission*)” i „LBYL (ang. *look before you leap*)”, „menedżer kontekstu (ang. *context manager*)”, „zasób”, „pułapka (ang. *breakpoint*)”, „pułapka warunkowa”, „wykonanie krokowe”, „dziennik (ang. *log*)”, „rejestrowanie zdarzeń” / „logowanie”, „poziom komunikatu”; „podrozdział” dla części książki; „funkcja generatorowa” / „generator” według konwencji rozdziału 6.
- Nagłówki w formie rzeczownikowej; nazwy w nagłówkach w kodzie (np. „Klauzule `else` i `finally`”, „Dekorator `contextlib.contextmanager`”).
- Docstringi `"""Zwraca ..."""`, `"""Wczytuje ..."""`, `"""Sprawdza ..."""`; komunikaty wyjątków po polsku, bez kropki na końcu, z wartością w `{wartosc!r}` tam, gdzie pomaga (`!r` znane z rozdziału 3 tylko przez `repr()` — zapis `{x!r}` wprowadzić jednym zdaniem przy pierwszym użyciu).
- Konwencje `CLAUDE.md`: bloki `python title="plik.py"`, `text title="dane.txt"` dla pliku danych, `json title="launch.json"`, `powershell title="Terminal"` dla poleceń (`python -O …`, `python -m pytest`, `python -m pdb`), `{ .python .no-copy }` dla REPL, `{ .text .no-copy }` dla wyników, śladów, sesji pdb (decyzja przy pisaniu: prompt `(Pdb)` bez kolorowania), tabel tekstowych i drzewa hierarchii; admonitions z polskimi tytułami; cudzysłowy „…”; klawisze `++f5++`, `++f9++`, `++f10++`, `++f11++`, `++shift+f11++`, `++ctrl+c++`; terminy angielskie z „ang.” przy pierwszym użyciu.
- Weryfikacja: każdy deterministyczny przykład uruchomiony przez `scripts/verify_page.py` na `.venv` (3.14.7); przed stroną 4 skrypt rozszerzyć tak, by bloki `text title="…"` (plik danych) były zapisywane do katalogu tymczasowego przed uruchomieniem skryptów; przykłady z `input()` przez `--stdin=plik.py=w1|w2`; sesje REPL i pdb osobno; **wyjścia mieszające `print()` i `logging`** (stdout i stderr) sprawdzane ręcznie w terminalu, bo harness dokleja `stderr` po `stdout` — w przykładach logowania nie mieszamy obu strumieni w jednym skrypcie; pytest w tymczasowym venv poza repozytorium (wersja pytest odnotowana); debugger i zrzuty — ręcznie w VSC. Liczby zależne od komputera (czas w `stoper()`) oznaczone.
- Zapowiedzi w przód (rozdziały jeszcze nienapisane: klasy, wejście-wyjście, wydajność, współbieżność, warsztat) wyłącznie prozą po temacie, bez numeru rozdziału, z komentarzem `<!-- TODO: link po powstaniu rozdziału o … -->` bezpośrednio po zdaniu; każda taka zapowiedź dopisana do listy „Zapowiedzi i luki, które rozdział domyka” właściwego rozdziału w `PLAN_ROZWOJU.md`.
- `index.md` w układzie rozdziałów 6–7 (decyzja 1). Odsyłacze do rozdziałów 1–7 wewnątrz nowych stron dozwolone od razu; zmiany w rozdziałach 1–7 (tabela na końcu) zbiorczo po ukończeniu wszystkich stron rozdziału 8. Strony rozdziału 4 z markerami aktywności nie są dotykane.

## Strony

### 1. `obsluga-wyjatkow.md` — Obsługa wyjątków

**Cel.** Czytelnik rozumie wyjątek jako obiekt zgłaszany w chwili błędu i propagowany przez stos wywołań, czyta ślad wywołań w brzmieniu 3.14, zna najczęstsze wyjątki wbudowane z rozdziałów 2–7 i przechwytuje je instrukcją `try`/`except` z klauzulami `else` i `finally`; potrafi poprawnie wczytać liczbę od użytkownika.

**Kolejność H2/H3.**
1. Program bez obsługi i z obsługą
2. Anatomia śladu wywołań (H3: Podpowiedzi interpretera)
3. Najczęstsze wyjątki
4. Instrukcja `try` i klauzula `except` (H3: Obiekt wyjątku; H3: Kilka typów w jednej klauzuli; H3: Kolejność klauzul `except`) — kolejność zmieniona przy pisaniu: krotka typów używa `as e`
5. Klauzule `else` i `finally`
6. Walidacja danych wejściowych

**Pojęcia wprowadzane.** Wyjątek jako obiekt; nieprzechwycony wyjątek → ślad na `stderr` i kod wyjścia 1 (przypomnienie z rozdziału 7); propagacja przez stos (ramki od modułu do miejsca błędu, „most recent call last”); ślad 3.14: ramki `File "…", line N, in nazwa`, wiersz kodu, znaczniki `~~~^^^` (od 3.11), komunikat `Typ: opis`; podpowiedź „Did you mean” (od 3.10; tylko w śladzie, nie w `str(blad)`); tabela wyjątków: `ValueError`, `TypeError`, `IndexError`, `KeyError`, `ZeroDivisionError`, `AttributeError`, `NameError`, `FileNotFoundError`, `ModuleNotFoundError`, `RecursionError`, `AssertionError`, `StopIteration` — z komunikatem 3.14.7 i odsyłaczem do miejsca w książce; `try`/`except Typ`; krotka typów; PEP 758 (decyzja 7); `as blad`, `str(blad)`, `blad.args`, `type(blad).__name__`, `repr(blad)` (`KeyError('klucz')`), atrybuty specyficzne: `FileNotFoundError.filename`, `StopIteration.value` (domknięcie noty z rozdziału 6); kolejność klauzul — pierwsza pasująca wygrywa, ogólniejsza przed szczegółową przesłania (`Exception` przed `ValueError`; pełna hierarchia na stronie 2); `else` (kod wykonywany tylko bez wyjątku, poza zasięgiem `except`), `finally` (zawsze; także przy `return`), PEP 765 (`SyntaxWarning: 'return' in a 'finally' block`, wynik `finally` nadpisuje `try`); pętla `while True` z `try` i `return`/`break`, operator `:=` z rozdziału 4 przy `input()`, `str.isdigit()` jako sprawdzenie „przed” (LBYL) z ograniczeniami (`"-5"`, `" 7 "`, `"1_000"` odrzucone, choć `int()` je przyjmuje) — rozwinięcie na stronie 3.

**Zależności.** `int(input())` i `ValueError` (rozdziały 2–3); `KeyError`/`get()` (5); `IndexError` (5); `StopIteration` i `next()` (4, 6); stos wywołań i ramki (6, rekurencja); kod wyjścia, `sys.exit()`, `AssertionError`, `ModuleNotFoundError` (7).

**Główne przykiady.** `srednia.py`: `int("abc")` w funkcji wywołanej z modułu — pełny ślad z dwiema ramkami; ta sama funkcja z `try/except ValueError` i komunikatem; `podpowiedz.py`: `mth.sqrt(2)` → `NameError: name 'mth' is not defined. Did you mean: 'math'?` i `str(blad)` bez podpowiedzi; `obiekt-wyjatku.py`: `except (ValueError, TypeError) as blad:` z `type(blad).__name__`, `str(blad)`, `blad.args`; `kolejnosc.py`: `except Exception` przed `except ValueError` — druga klauzula martwa; `else-finally.py`: `dziel(a, b)` z czterema klauzulami dla `(1, 2)` i `(1, 0)`; `finally-return.py` z ostrzeżeniem PEP 765; `wczytaj-liczbe.py`: `while True: try: return int(input(...)) except ValueError: print(...)` uruchomiony z `--stdin=abc|12`; wariant z `isdigit()` i jego ograniczenia w REPL.

**Wymagane zachowania do weryfikacji na 3.14.7.** `int("abc")` → `ValueError: invalid literal for int() with base 10: 'abc'`; `[][0]` → `IndexError: list index out of range`; `{}["klucz"]` → `KeyError: 'klucz'`, `repr` → `KeyError('klucz')`; `1 / 0` → `ZeroDivisionError: division by zero`; `None.x` → `AttributeError: 'NoneType' object has no attribute 'x'`; `open("brak.txt", encoding="utf-8")` → `FileNotFoundError: [Errno 2] No such file or directory: 'brak.txt'`, `.filename == 'brak.txt'`; `"a" + 1` → `TypeError: can only concatenate str (not "int") to str`; `mth.sqrt(2)` → `NameError: … Did you mean: 'math'?`, `str(blad)` bez dopisku; `except ValueError, TypeError:` działa, `except ValueError, TypeError as blad:` → `SyntaxError: multiple exception types must be parenthesized when using 'as'`; `return` w `finally` → `SyntaxWarning: 'return' in a 'finally' block` i wynik z `finally`; `StopIteration.value` → wartość z `return` generatora; kolejność klauzul (druga martwa) bez ostrzeżenia interpretera (sprawdzić, czy pylint/pyflakes ostrzega — jeśli tak, jedno zdanie).

**Źródła repozytorium.** `Wyklad_05.txt` sl. 19–21 (przykłady try/except, tabela wyjątków — z korektą „divisio”), 41 (walrus przy `input()`); `Wyklad_03.txt` sl. 33 (`while (linia := input())`); `PythonNotatki.txt` 2446–2460 (ślady IDLE — tylko jako kontrast historyczny, bez cytowania).

**Źródła zewnętrzne.** Tutorial *Errors and Exceptions* (8.1–8.3, 8.7); *Built-in Exceptions* (opisy jednozdaniowe, `add_note` nie tu); What's New 3.14 (PEP 758, PEP 765, *Improved error messages*); PEP 3134 tylko jako numer; `sys.exit` (kod wyjścia — przypomnienie).

**TODO/zapowiedzi do domknięcia.** `06-funkcje/funkcje-generatorowe.md:404–409` (odczyt `StopIteration.value`) → H3 „Obiekt wyjątku”; `07-moduly/argumenty-wiersza-polecen.md:117` i `07-moduly/moduly-i-import.md:401` („obsługę wyjątków poznamy w osobnym rozdziale”) → strona.

**Odłożone.** `raise` (strona 2); hierarchia (strona 2); `sys.exception()`; `traceback` (strona 5); `except*` (strona 3); `warnings`; `-X dev`.

**Ryzyka kolejności pojęć.** Tabela wyjątków wspomina `FileNotFoundError` przed `open()` — dopuszczalne jako czarna skrzynka (decyzja 10) z odsyłaczem prozą do rozdziału 9; `except Exception` na tej stronie tylko jako ilustracja kolejności, z zapowiedzią hierarchii; PEP 758 nie może sugerować, że nawiasy są przestarzałe.

**Orientacyjny rozmiar.** ok. 380–440 linii.

### 2. `zglaszanie-wyjatkow.md` — Zgłaszanie wyjątków

**Cel.** Czytelnik zgłasza wyjątki wbudowane instrukcją `raise` zamiast zwracać `None`, rozumie hierarchię (`BaseException` a `Exception`, `SystemExit`, `KeyboardInterrupt`, `LookupError`, `OSError`), ponownie zgłasza i łączy wyjątki w łańcuchy, dodaje notatki, wie, czym `assert` różni się od `raise` i co robi opcja `-O`.

**Kolejność H2/H3.**
1. Instrukcja `raise` (H3: Propagacja przez stos wywołań)
2. Hierarchia wyjątków
3. Ponowne zgłoszenie i łańcuchy wyjątków (H3: Notatki do wyjątku — `add_note()`)
4. Instrukcja `assert` a wyjątki
5. Przykład: konwersja liczb rzymskich z walidacją (nota „Zapowiedź: własne typy wyjątków”)

**Pojęcia wprowadzane.** `raise Typ("komunikat")`; `raise` a `return None` (domknięcie rozdziału 6: `silnia()` z `ValueError` zamiast `None`); propagacja — funkcja nie musi obsługiwać, wyjątek wędruje do wywołującego, aż do modułu; drzewo hierarchii z dokumentacji 3.14 (pełne drzewo jako blok `.text` — z dopiskiem, że pochodzi z dokumentacji, i zaznaczeniem gałęzi używanych w książce; albo drzewo skrócone do ok. 25 nazw z odsyłaczem — do decyzji przy pisaniu, preferowane skrócone z `ExceptionGroup`, `Warning` jednym wierszem); `Exception` jako baza wyjątków obsługiwanych; `BaseException`: `SystemExit` (mechanizm `sys.exit()` — domknięcie rozdziału 7; kod w `blad.code`), `KeyboardInterrupt` (++ctrl+c++), `GeneratorExit` jednym zdaniem; `except LookupError` przechwytuje `IndexError` i `KeyError`; `OSError` i `FileNotFoundError`; goły `raise` w `except` (ponowne zgłoszenie tego samego obiektu, ślad zachowany); `raise Nowy(...) from blad` (`The above exception was the direct cause…`), łańcuch niejawny przy błędzie w `except` (`During handling of the above exception…`), `from None`; `blad.add_note("…")` (3.11) i miejsce notatki w śladzie; `assert` (z rozdziału 7) jako wyjątek `AssertionError` pomijany przez `python -O` (`__debug__` → `False`), stąd zakaz walidacji danych przez `assert`; przykład z wykładu: `arabskie_na_rzymskie()` z `TypeError`/`ValueError` i użyciem z `try/except`; admonition „Zapowiedź: własne typy wyjątków” (klasa dziedzicząca z `Exception`, konwencja nazw `…Error`, rozdział 10).

**Zależności.** Strona 1; `return None` jako sygnał błędu (6: `definiowanie-funkcji.md#instrukcja-return`, `rekurencja.md`); `sys.exit()` i kody wyjścia (7); `assert` (7); `isinstance()` (3); `{x!r}` w f-stringu (wprowadzić w miejscu).

**Główne przykłady.** `silnia-raise.py`: `silnia(n)` z `raise ValueError(f"n musi być nieujemne, otrzymano {n!r}")` i `raise TypeError` dla `float`; wywołanie z `main()` → ślad z trzema ramkami; `hierarchia.py`: `except LookupError` dla `IndexError` i `KeyError`; `except Exception` nie przechwytuje `KeyboardInterrupt` (REPL/skrypt z jawnym `raise KeyboardInterrupt`) — i `SystemExit` z `sys.exit(3)` przechwycony `except SystemExit as blad` z `blad.code`; `ponowne.py`: `except ValueError as blad: print(...); raise`; `lancuch.py`: `wczytaj(tekst)` z `raise RuntimeError(...) from blad`; `lancuch-niejawny.py` (`1 / 0` w `except`); `from None`; `notatka.py` z `add_note()`; `zalozenie.py` uruchomione `python zalozenie.py` i `python -O zalozenie.py` (blok `powershell`), `print(__debug__)`; `rzymskie.py` (z W05 sl. 26, z docstringiem i `main()`).

**Wymagane zachowania do weryfikacji na 3.14.7.** Ślad `raise … from blad` z separatorem „The above exception was the direct cause of the following exception:”; łańcuch niejawny z „During handling of the above exception, another exception occurred:”; `from None` — tylko drugi ślad; `add_note` — notatka pod komunikatem; `python -O` pomija `assert`, `__debug__` → `False` (przy `-O`), `sys.flags.optimize` → 1; `except Exception` nie łapie `KeyboardInterrupt`; `SystemExit.code` → 3; `raise` bez aktywnego wyjątku → `RuntimeError: No active exception to reraise` (jedno zdanie, jeśli zostanie użyte); drzewo hierarchii zgodne z `exceptions.html` 3.14 (`PythonFinalizationError` pod `RuntimeError`, `ExceptionGroup`).

**Źródła repozytorium.** `Wyklad_05.txt` sl. 22 (raise, re-raise, `from`), 23 (hierarchia — uzupełniona), 24 (własne wyjątki — tylko zapowiedź), 26 (liczby rzymskie), 36 (tabela pułapek — częściowo); `Wyklad_03.txt` sl. 19 (KeyError); `PythonNotatki.txt` 2379 (`assert`, `raise` nie w lambda — jedno zdanie).

**Źródła zewnętrzne.** Tutorial *Errors and Exceptions* 8.4–8.6, 8.8; *Built-in Exceptions* (hierarchia, `add_note`, `__cause__`/`__context__`/`__suppress_context__`, `SystemExit`, `KeyboardInterrupt`); `python -O`, `PYTHONOPTIMIZE`, `__debug__` (cmdline, *Built-in Constants*); PEP 3134 (numer), PEP 678 (`add_note`, numer).

**TODO/zapowiedzi do domknięcia.** `06-funkcje/definiowanie-funkcji.md:101` i `06-funkcje/rekurencja.md:104` (`return None` → wyjątki) → sekcja 1; `07-moduly/argumenty-wiersza-polecen.md:264` (mechanizm `sys.exit()`) → sekcja 2; `07-moduly/struktura-projektu.md:83` (`assert`, opcja `-O`) → sekcja 4.

**Odłożone.** Własne klasy wyjątków (10); `__cause__`/`__context__` jako atrybuty (nota); `raise` w setterach (10); `warnings`; `ExceptionGroup` (strona 3); `sys.excepthook`.

**Ryzyka kolejności pojęć.** Drzewo hierarchii mówi o „klasach” i „dziedziczeniu” — używać sformułowań „typ ogólniejszy / szczegółowy”, „podtyp”, z jednym zdaniem, że mechanizm nazywa się dziedziczeniem i poznamy go w rozdziale 10 (jak „podklasa krotki” w rozdziale 7); `{n!r}` wprowadzić w miejscu użycia.

**Orientacyjny rozmiar.** ok. 320–380 linii.

### 3. `styl-i-testowanie.md` — Styl obsługi błędów i testy wyjątków

**Cel.** Czytelnik dobiera między sprawdzeniem „przed” (LBYL) a próbą i obsługą (EAFP), zna antywzorce (goły `except`, `except Exception: pass`, zbyt szeroki `try`), utrzymuje blok `try` wąski, testuje wyjątki w pytest; dla dociekliwych — grupy wyjątków.

**Kolejność H2/H3.**
1. Dwa style: LBYL i EAFP
2. Zasięg bloku `try`
3. Antywzorce obsługi błędów
4. Testy wyjątków w pytest
5. Grupy wyjątków i `except*` (dla dociekliwych)

**Pojęcia wprowadzane.** LBYL (`if klucz in slownik`) a EAFP (`try: … except KeyError`) a metoda `get()` z rozdziału 5 jako trzecia droga (często najlepsza); wyścig przy sprawdzaniu istnienia pliku (prozą, bez `os.path.exists`); koszt: od 3.11 wejście w `try` bez wyjątku jest bezpłatne („zero-cost”), zgłoszenie i przechwycenie kosztuje — EAFP dla przypadków rzadkich, LBYL dla częstych, bez dogmatu (korekta tezy „EAFP jest zawsze pythonowe”); wąski `try` — tylko instrukcja, która może zawieść; `else` jako narzędzie zawężania; antywzorce: goły `except:` (łapie `KeyboardInterrupt` i `SystemExit`), `except Exception: pass` (Zen: *Errors should never pass silently* z rozdziału 2), komunikat bez informacji („Coś poszło nie tak”), przechwycenie zbyt wcześnie (funkcja biblioteczna nie powinna decydować za wywołującego — zwykle `raise` dalej albo `from`); `pytest.raises(ValueError)` jako menedżer kontekstu (nazwa „menedżer kontekstu” zapowiedziana — pełne wyjaśnienie na stronie 4; tu: „konstrukcja `with`, którą omawiamy w następnym podrozdziale”), `match=` (wyrażenie regularne — w praktyce fragment komunikatu; znaki specjalne jak `(` wymagają `re.escape` — jedno zdanie), `excinfo.value`, kod po zgłoszeniu w bloku `with` nie wykonuje się; test dla `silnia(-1)` i `silnia(2.5)` w `tests/test_silnia.py`; `ExceptionGroup("…", [ValueError("a"), TypeError("b")])`, ślad grupy, `except* ValueError as grupa: grupa.exceptions` — zastosowanie w zbieraniu wielu błędów walidacji i we współbieżności (rozdział 15).

**Zależności.** Strony 1–2; `get()`/`in` (5); Zen (2); pytest: instalacja w venv, `python -m pytest`, `tests/` (7: `struktura-projektu.md#narzedzie-pytest`); `with` — zapowiedź strony 4.

**Główne przykłady.** `slownik-style.py`: trzy warianty odczytu; `wczytaj-liczbe` z `isdigit()` a `int()` (ograniczenia LBYL); `waski-try.py` (błąd: cała funkcja w `try` ukrywa `TypeError` z innej linii); `antywzorce.py`: goły `except` z `KeyboardInterrupt` (REPL: ++ctrl+c++ opisany prozą, w kodzie jawny `raise KeyboardInterrupt`), `except Exception: pass`; `tests/test_silnia.py` z `pytest.raises(ValueError, match="nieujemne")` i `excinfo.value`; wynik `python -m pytest` (2 passed) i wynik testu niezaliczonego, gdy `silnia` zwraca `None` (`Failed: DID NOT RAISE <class 'ValueError'>`); `grupa.py` z `except*`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `pytest.raises` — brzmienie `DID NOT RAISE`, nagłówek wyniku pytest z wersją (tymczasowy venv: `python -m pip install pytest`, wersja odnotowana; sieć potrzebna); ślad `ExceptionGroup` (format `+ Exception Group Traceback`, `+-+---------------- 1 ----------------`); `except*` → `grupa.exceptions` jako krotka; `"-5".isdigit()` → `False`, `int("-5")` → `-5`, `int(" 7 ")` → `7`, `int("1_000")` → `1000`.

**Źródła repozytorium.** `Wyklad_05.txt` sl. 25 (antywzorce), 30 (EAFP/LBYL — z korektą kosztu), 36 (pułapki), 45 (`ExceptionGroup`); `Wyklad_03.txt` sl. 19; `Wyklad_07.txt` sl. 24 (EAFP jako filozofia — jedno zdanie); `Wyklad_12.txt` sl. 5 (`pytest.raises`); `lab3` (pytest z rozdziału 7).

**Źródła zewnętrzne.** Glossary (EAFP, LBYL); What's New 3.11 (zero-cost exceptions, `except*`, PEP 654); pytest *How to write and report assertions* (`raises`, `match`, `excinfo`); Zen (PEP 20).

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich; domyka lukę planu „EAFP/LBYL (W03 s. 19)”.

**Odłożone.** `pytest.mark.parametrize` (16); `RaisesGroup`; `xfail`; `re` jako temat; mockowanie.

**Ryzyka kolejności pojęć.** `pytest.raises` używa `with` przed stroną 4 — dopuszczalne z zapowiedzią (jak `with open()` w wykładach); nie tłumaczyć protokołu tu. `except*` musi pozostać krótkie.

**Orientacyjny rozmiar.** ok. 260–320 linii.

### 4. `with-i-contextlib.md` — Instrukcja with i menedżery kontekstu

**Cel.** Czytelnik rozumie problem zwalniania zasobów, zapisuje go najpierw przez `try/finally`, a potem instrukcją `with`, wie, co `with` robi (protokół pojęciowo), tworzy własny menedżer kontekstu z funkcji generatorowej dekoratorem `contextlib.contextmanager` i zna narzędzia pomocnicze `contextlib`.

**Kolejność H2/H3.**
1. Problem zwalniania zasobów
2. Instrukcja `with` (H3: Kilka zasobów w jednej instrukcji)
3. Protokół menedżera kontekstu
4. Dekorator `contextlib.contextmanager` (H3: Wyjątek wewnątrz bloku `with`)
5. Narzędzia modułu `contextlib` (dla dociekliwych)

**Pojęcia wprowadzane.** Zasób (plik, połączenie, blokada, katalog roboczy, pomiar czasu) i konieczność zwolnienia także przy wyjątku; `plik = open(...)`, `try: … finally: plik.close()`; `with open("dane.txt", encoding="utf-8") as plik:` — plik zamknięty po bloku (`plik.closed` → `True`), także przy wyjątku; kilka zasobów po przecinku i w nawiasach (od 3.10); protokół: obiekt z metodami `__enter__()` (wynik trafia do nazwy po `as`) i `__exit__()` (wywoływana zawsze; otrzymuje informację o wyjątku; może go stłumić) — pojęciowo, „klasę z takimi metodami napiszemy w rozdziale 11”; `@contextlib.contextmanager`: funkcja generatorowa z dokładnie jednym `yield` (kod przed = `__enter__`, wartość `yield` = `as`, kod po = `__exit__`), `try/finally` wokół `yield`, bo wyjątek z bloku `with` jest zgłaszany w miejscu `yield`; `stoper(nazwa)` z `time.perf_counter()` (decyzja 11); `zasob(nazwa)` symulujący otwarcie/zamknięcie z wypisami — pokazuje kolejność zwalniania (odwrotna); `suppress(FileNotFoundError)` zamiast `try/except/pass` z uzasadnieniem, kiedy to nie jest antywzorzec; `nullcontext()` jako zasób pusty przy warunkowym `with`; `ExitStack` dla zmiennej liczby zasobów (lista `zasob(n)` w pętli); `chdir()` i `redirect_stdout()` wymienione (rozdział 9); jednorazowość menedżera z generatora (drugi `with` na tym samym obiekcie → błąd — jedno zdanie).

**Zależności.** Strony 1–2 (`try/finally`, propagacja); funkcje generatorowe, `yield`, dekoratory (6); `open()` jako czarna skrzynka (decyzja 10); `pytest.raises` jako pierwszy widziany `with` (strona 3).

**Główne przykłady.** `dane.txt` (trzy wiersze liczb) + `bez-with.py` (`open`/`try`/`finally`/`close`, `plik.closed`); `z-with.py` (to samo z `with`, `plik.closed` po bloku → `True`); `brak-pliku.py` (`FileNotFoundError` z `with` — plik nie został otwarty, `with` nic nie zamyka); `dwa-zasoby.py` z formą w nawiasach; `zasob.py` z `@contextmanager` i wypisami „otwieram/zamykam” dla dwóch zasobów (kolejność zamykania odwrotna); `stoper.py` (`with stoper("sortowanie"): sorted(range(10**6, 0, -1))` — czas oznaczony jako zależny od komputera, blok wyniku porównywany po masce liczby); `wyjatek-w-with.py` (`1 / 0` w bloku — „zamykam” wypisane przed śladem); `suppress.py`, `nullcontext.py`, `exitstack.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** Kolejność wypisów `otwieram a / otwieram b / … / zamykam b / zamykam a`; `plik.closed` → `True` po `with`; wyjątek w bloku `with` z menedżerem generatorowym: `finally` wykonane, ślad propaguje (sprawdzone: `zamykam c` przed `Traceback`); `suppress(FileNotFoundError)` pomija `open("brak.txt")` i wykonanie idzie dalej; drugi `with` na zużytym obiekcie z `@contextmanager` → `AttributeError`/`RuntimeError` (sprawdzić brzmienie; jeśli niejednoznaczne — tylko prozą); forma `with (a as x, b as y):` działa.

**Źródła repozytorium.** `Wyklad_05.txt` sl. 28 (with — z korektą `encoding`), 29 (protokół — tylko pojęciowo, klasa w 11), 45 (`suppress`); `Wyklad_08.txt` sl. 7 (with/protokół), 34 (`@contextmanager`, timer — z `try/finally`), 35 (`suppress`, `ExitStack`; `redirect_stdout` → 9), 36 (`chdir`, `nullcontext` — bez `/tmp`); `PythonNotatki.txt` 5433–5450 (`with open` przy `print(file=)` — rozdział 9).

**Źródła zewnętrzne.** Tutorial 8.9 *Predefined Clean-up Actions*; Language Reference *The with statement* (nawiasy od 3.10); `contextlib` (`contextmanager`, `suppress`, `nullcontext`, `ExitStack`, `chdir` 3.11, jednorazowość); `time.perf_counter()`.

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich (zapowiedź `with` w rozdziale 6 dotyczyła `pytest`/plików — brak komentarza TODO); przygotowuje rozdział 9 (każde `open()` z `with`) i 11 (protokół jako klasa).

**Odłożone.** `__enter__`/`__exit__` jako klasa (11); `ContextDecorator`; `AsyncExitStack`; `redirect_stdout`/`chdir` z przykładem (9); `threading.Lock` jako zasób (15).

**Ryzyka kolejności pojęć.** Plik `dane.txt` musi istnieć w katalogu uruchomienia — rozszerzenie `verify_page.py`; opisy „metoda `__enter__`” wymagają słowa „metoda” — znane z rozdziału 3 (metody typu `str`); nie opisywać `__exit__` z trzema argumentami poza jednym zdaniem.

**Orientacyjny rozmiar.** ok. 300–360 linii.

### 5. `diagnostyka.md` — Diagnostyka — ślad wywołań (traceback) i debugger

**Cel.** Czytelnik czyta ślad wywołań od dołu i przez łańcuchy, zapisuje go z programu modułem `traceback`, uruchamia program pod debuggerem VSC z pułapkami i wykonaniem krokowym, ogląda zmienne i stos wywołań, zna `breakpoint()` i podstawowe polecenia pdb.

**Kolejność H2/H3.**
1. Czytanie śladu wywołań
2. Moduł `traceback`
3. Debugger w Visual Studio Code (H3: Pułapki i uruchomienie; H3: Wykonanie krokowe i podgląd zmiennych; H3: Pułapki warunkowe i plik `launch.json`)
4. Funkcja `breakpoint()` i pdb (nota „Nowości Pythona 3.14” — PEP 768)

**Pojęcia wprowadzane.** Strategia czytania: ostatni wiersz (typ i komunikat) → ostatnia ramka (miejsce) → ramki wyżej (droga wywołań) → łańcuch (przyczyna); ramki z `<frozen runpy>` przy `python -m` (przypomnienie z rozdziału 7) i z bibliotek (własny kod wśród ramek cudzych); `traceback.print_exc()` w `except` (ślad na `stderr` bez przerwania programu), `traceback.format_exc()` jako łańcuch do zapisania (dziennik — strona 6); debugger: rozszerzenie Python Debugger (decyzja 12), pułapka (++f9++ lub kliknięcie w margines), ++f5++ i wybór „Python File”, wstrzymanie na pułapce, pasek: Continue ++f5++, Step Over ++f10++, Step Into ++f11++, Step Out ++shift+f11++, Restart, Stop; panele Variables (Locals/Globals), Watch, Call Stack (ramki rekurencji `silnia(4)` z rozdziału 6 — stos widoczny jak w opisie ramek), Breakpoints, Debug Console (wyrażenia w kontekście wstrzymania); pułapka warunkowa (Expression, Hit Count) i logpoint jednym zdaniem; `launch.json` minimalny (`"type": "debugpy"`, `"request": "launch"`, `"program": "${file}"`, `"console": "integratedTerminal"`, `"args"`, `"justMyCode"`); `breakpoint()` w kodzie → pdb w terminalu: `n`, `s`, `c`, `p wyrazenie`, `l`, `q`, `h`; `PYTHONBREAKPOINT=0` wyłącza; nota PEP 768: `sys.remote_exec()` i `python -m pdb -p PID` jako nowa możliwość 3.14, poza zakresem.

**Zależności.** Strony 1–2 (ślady, łańcuchy); rekurencja i ramki (6); `python -m` i `<frozen runpy>` (7); VSC z rozdziału 1 (`konfiguracja.md`: uruchamianie, Code Runner, ++f5++ — zapowiedź do domknięcia); `stderr` (7).

**Główne przykłady.** `lancuch-czytanie.py` — trzy funkcje, błąd na dole, jedna ramka biblioteczna? (bez bibliotek zewnętrznych — użyć `json`? nie; użyć `sorted(key=…)` z błędem w funkcji klucza: ramka `<built-in>`? — sprawdzić, jak 3.14 pokazuje ramkę wywołania z `sorted`; alternatywnie `map()`/`list()`); `traceback-log.py` z `print_exc()` w pętli przetwarzającej listę wartości (`["1", "x", "3"]`) — program kończy pracę mimo błędu; `debug-silnia.py` (rekurencja z rozdziału 6) jako program do sesji debuggera; `launch.json`; `pdb-sesja` jako blok `{ .python .no-copy }` z promptem `(Pdb)` odtworzonym z terminala (`python debug-silnia.py` z `breakpoint()`).

**Wymagane zachowania do weryfikacji na 3.14.7.** `traceback.print_exc()` wypisuje pełny ślad na `stderr` i program idzie dalej; `format_exc()` zwraca ten sam tekst; sesja pdb (prompt `(Pdb)`, `n`, `p n`, `l`, `c`, `q`) odtworzona ręcznie w terminalu — zapis z brzmieniem 3.14 (m.in. potwierdzenie przy `q` w trybie inline — What's New 3.14); nazwa rozszerzenia i skróty sprawdzone w VSC autora (zrzuty); `"type": "python"` → ostrzeżenie o przestarzałości w VSC (prozą, bez cytowania).

**Źródła repozytorium.** `Wyklad_05.txt` sl. 45 (`traceback.print_exc`/`format_exc` — z korektą gołego `except`); `01-instalacja/konfiguracja.md:136` (zapowiedź debugowania); docs VSC *Python debugging in VS Code* (materiał własny); `PythonNotatki.txt` 2446–2460 (ślady IDLE — kontrast, bez cytowania).

**Źródła zewnętrzne.** `traceback` (print_exc, format_exc, kolor od 3.13); `pdb` (polecenia, `breakpoint()`, zmiany 3.14: tryb inline, potwierdzenie `q`, `-p`); `sys.breakpointhook`, `PYTHONBREAKPOINT` (cmdline); What's New 3.14 (PEP 768, pdb); VS Code docs *Debugging* (Python Debugger `ms-python.debugpy`, `debugpy` type, konfiguracje).

**TODO/zapowiedzi do domknięcia.** `01-instalacja/konfiguracja.md:136` („Szersze omówienie debugowania nastąpi w dalszych rozdziałach”) → sekcja 3.

**Odłożone.** `pdb` poza podstawą; `faulthandler`; `-X dev`; profilowanie (13); testy w VSC (panel Testing, 16); zdalne debugowanie.

**Ryzyka kolejności pojęć.** Strona jest częściowo narzędziowa — treści terminalowe (pdb) jako bloki tekstowe, zrzuty tylko tam, gdzie obraz niesie układ okna; nie przepisywać dokumentacji VSC — tylko ścieżka pracy z jednym programem; sesja pdb musi być krótka (do ok. 20 wierszy).

**Orientacyjny rozmiar.** ok. 260–320 linii (+ 3 wpisy w `ZRZUTY.md`).

### 6. `logging.md` — Logowanie zamiast print

**Cel.** Czytelnik rejestruje zdarzenia programu modułem `logging` zamiast `print()`, dobiera poziom komunikatu, konfiguruje format i próg raz na początku programu, zapisuje wyjątek ze śladem metodą `exception()` i formatuje komunikaty leniwie.

**Kolejność H2/H3.**
1. Zadania `print()` i dziennika
2. Pierwszy dziennik
3. Poziomy komunikatów
4. Rejestrowanie wyjątków
5. Formatowanie komunikatów
6. Dziennik w pliku i dalsze możliwości (zapowiedź)

**Pojęcia wprowadzane.** Tabela z HOWTO „kiedy `print()`, kiedy `logging`, kiedy `raise`” (skrócona: wyjście programu dla użytkownika → `print()`; zdarzenia i diagnostyka → `logging`; błąd, którego nie da się obsłużyć → `raise`; `warnings.warn()` jednym zdaniem); `import logging`, `log = logging.getLogger(__name__)` (nazwa modułu, `__main__` w skrypcie — rozdział 7), `logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")` wywołany raz, przed pierwszym komunikatem (inaczej nie działa — konfiguracja domyślna zakłada `WARNING` na `stderr`); próg: komunikaty poniżej poziomu odrzucone; tabela `DEBUG`(10) `INFO`(20) `WARNING`(30) `ERROR`(40) `CRITICAL`(50) z opisem użycia; `log.exception("…")` w `except` — komunikat na poziomie `ERROR` ze śladem (odpowiednik `log.error(..., exc_info=True)`); leniwe formatowanie: `log.info("wczytano %d wierszy", n)` — argumenty osobno, `%d`/`%s` jako wieloznaczniki (pełne formatowanie `%` w rozdziale 9), dlaczego nie f-string (koszt formatowania komunikatu, który zostanie odrzucony; narzędzia agregujące); `%(asctime)s` z `datefmt=`; wyjście na `stderr` (nie miesza się z `print()` w potokach — przypomnienie strumieni z rozdziału 7); zapowiedź: `filename="program.log", encoding="utf-8"` (rozdział 9), tryb dopisywania, logowanie z wątków (15), `dictConfig` i handlery poza książką.

**Zależności.** Strony 1–2 (`except`, `raise`); `__name__` (7); `stderr` i kody wyjścia (7); `%` w f-stringach (3) — tu tylko `%s`/`%d`; `traceback.format_exc()` (strona 5) jako punkt odniesienia.

**Główne przykłady.** `pierwszy-dziennik.py` (cztery poziomy, próg `INFO` — `debug` niewidoczny); `poziomy.py` z `basicConfig(level=logging.DEBUG)`; `wyjatek-dziennik.py` — pętla przetwarzająca `["1", "x", "3"]` z `log.exception()` (odpowiednik `traceback.print_exc()` ze strony 5, ale z poziomem, nazwą i czasem); `leniwe.py` z `%s` i `%d`; `format-czas.py` z `%(asctime)s` (wynik z maską daty — blok `.no-copy` z zaznaczeniem, że data zależy od uruchomienia; weryfikacja ręczna); bez `print()` w skryptach logujących (zasada weryfikacji).

**Wymagane zachowania do weryfikacji na 3.14.7.** Domyślny próg `WARNING` i format `WARNING:root:…` bez `basicConfig`; `basicConfig` po pierwszym wywołaniu `logging.*` nie zmienia konfiguracji (root ma już handler) — pokazać jako pułapkę; `log.exception()` dodaje ślad pod komunikatem; `logging.getLogger().level` → 30 domyślnie; `basicConfig(encoding=…)` bez `filename=` — sprawdzić, czy jest ignorowane, czy zgłasza błąd (nie używać w przykładach konsolowych); `%(levelname)s %(name)s: %(message)s` daje `INFO __main__: …`.

**Źródła repozytorium.** `Wyklad_05.txt` sl. 37 (logging — z korektą f-stringów na `%s`), 36 (`logging.error(e)` w tabeli pułapek); `python_thread.txt` sl. 10–11, 18 (bez użytecznej treści o logging — wzmianka w planie zbiorczym nietrafiona; logowanie z wątków → 15).

**Źródła zewnętrzne.** *Logging HOWTO* (basic tutorial: tabela „when to use”, poziomy, `basicConfig`, `getLogger(__name__)`, `%`-style, `exception`, `stderr`); `logging` (`basicConfig` — `encoding` 3.9, `force`), `logging.handlers` tylko jako nazwa.

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich; domyka lukę planu „logging (W05 s. 37)”.

**Odłożone.** Dziennik w pliku (9); `RotatingFileHandler`; `dictConfig`; `logging` z wątków (15); `warnings`; `structlog`/`rich` (nie w książce).

**Ryzyka kolejności pojęć.** `%s`/`%d` bez pełnego mini-języka — dwa zdania i odsyłacz prozą do rozdziału 9; nie mieszać `print()` i `logging` w jednym skrypcie (kolejność strumieni w harnessie); `asctime` niedeterministyczny.

**Orientacyjny rozmiar.** ok. 220–270 linii.

### 7. `index.md` — Wprowadzenie

Wstęp (dwa–trzy akapity): błędy jako obiekty — od rozdziału 2 czytaliśmy je wyłącznie ze śladów wywołań (`ValueError` przy `int(input())`, `KeyError`, `IndexError`, `RecursionError`, `ModuleNotFoundError`, `AssertionError`), teraz je przechwytujemy, zgłaszamy i łączymy; drugi wątek: zasoby, które trzeba zwolnić niezależnie od błędu — instrukcja `with`; trzeci: warsztat diagnostyczny — ślad wywołań, debugger VSC zapowiedziany w rozdziale 1, dziennik zamiast `print()`. Nawiązanie do rozdziału 6 (`return None` jako rozwiązanie tymczasowe, `StopIteration` z generatorów) i 7 (`assert`, pytest, `sys.exit()`, kody wyjścia). Następnie `---` i `## W tym rozdziale` z sześcioma pozycjami „Tytuł — tematy”; ostatnia sekcja strony 4 i strona 5 (pdb) oznaczone jako uzupełniające tam, gdzie to prawda. Bez „Ściągi” i bez „Powiązanego laboratorium”. Orientacyjny rozmiar: ok. 18 linii.

## Nawigacja (dodawana wraz z powstającymi stronami, za zgodą autora)

```yaml
  - 8. Wyjątki i zarządzanie zasobami:
      - Wprowadzenie: 08-wyjatki/index.md
      - Obsługa wyjątków: 08-wyjatki/obsluga-wyjatkow.md
      - Zgłaszanie wyjątków: 08-wyjatki/zglaszanie-wyjatkow.md
      - Styl obsługi błędów i testy wyjątków: 08-wyjatki/styl-i-testowanie.md
      - Instrukcja with i menedżery kontekstu: 08-wyjatki/with-i-contextlib.md
      - Diagnostyka — ślad wywołań (traceback) i debugger: 08-wyjatki/diagnostyka.md
      - Logowanie zamiast print: 08-wyjatki/logging.md
```

Pozycja w `docs/index.md` (dodawana wraz z `index.md` rozdziału): „8. [Wyjątki i zarządzanie zasobami](08-wyjatki/index.md) — obsługa i zgłaszanie wyjątków, styl EAFP i testy wyjątków, instrukcja with, diagnostyka i debugger, logowanie”.

## Kolejność tworzenia stron i odbiór

Każda strona przechodzi cykl: research w dokumentacji 3.14 → napisanie → uruchomienie wszystkich przykładów (`scripts/verify_page.py` dla skryptów, osobna weryfikacja bloków REPL i sesji pdb, polecenia terminalowe ręcznie w katalogu próbnym poza repozytorium, pytest w tymczasowym venv) → `mkdocs build` i `mkdocs build -f mkdocs.clean.yml` → niezależna recenzja (styl, fakty, kolejność pojęć, aktualność 3.14) → naniesienie ustaleń → raport → akceptacja autora → commit. Kolejność: 1 `obsluga-wyjatkow.md`, 2 `zglaszanie-wyjatkow.md`, 3 `styl-i-testowanie.md`, 4 `with-i-contextlib.md` (przed nią rozszerzenie `verify_page.py` o pliki danych), 5 `diagnostyka.md` (+ `ZRZUTY.md`), 6 `logging.md`, 7 `index.md`. Wpis nav i pozycja na stronie głównej rosną wraz z powstającymi stronami. Funkcja `silnia()` ze strony 2 jest wspólna dla stron 2 i 3 i musi pozostać spójna; strona 5 celowo używa wersji rekurencyjnej z rozdziału 6 (stos wywołań w debuggerze).

## Zmiany w rozdziałach 1–7 (wyłącznie domknięcie zapowiedzi, zbiorczo po ukończeniu rozdziału 8)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `01-instalacja/konfiguracja.md:136` | „Szersze omówienie debugowania nastąpi w dalszych rozdziałach.” → odsyłacz do `diagnostyka.md#debugger-w-visual-studio-code` | zdanie zachowane, zmieniona końcówka |
| `06-funkcje/definiowanie-funkcji.md:101` | `TODO` → odsyłacz do `zglaszanie-wyjatkow.md#instrukcja-raise` | „właściwy mechanizm, wyjątki, poznamy…” → „omawiamy w sekcji …” |
| `06-funkcje/rekurencja.md:104` | `TODO` → odsyłacz do `zglaszanie-wyjatkow.md#instrukcja-raise` | |
| `06-funkcje/funkcje-generatorowe.md:404–409` | zdanie w nocie „jak odczytać ją z obiektu wyjątku, pokażemy w rozdziale o wyjątkach” → odsyłacz do `obsluga-wyjatkow.md#obiekt-wyjatku`; usunięcie `TODO` | tekst noty zachowany |
| `07-moduly/moduly-i-import.md:401` | „Wyjątki i ich obsługę omawia osobny rozdział” → odsyłacz do `obsluga-wyjatkow.md` | |
| `07-moduly/argumenty-wiersza-polecen.md:117` | „obsługę wyjątków poznamy w osobnym rozdziale” → odsyłacz do `obsluga-wyjatkow.md` | |
| `07-moduly/argumenty-wiersza-polecen.md:264` | „Mechanizm, którym `sys.exit()` przerywa program, poznamy w rozdziale o wyjątkach” → odsyłacz do `zglaszanie-wyjatkow.md#hierarchia-wyjatkow` (`SystemExit`) | |
| `07-moduly/struktura-projektu.md:83` | „poznamy w rozdziale o wyjątkach; tam też wrócimy do opcji interpretera…” → odsyłacze do `zglaszanie-wyjatkow.md#instrukcja-raise` i `#instrukcja-assert-a-wyjatki` | |
| `07-moduly/itertools.md:132` | „W następnym rozdziale zajmujemy się wyjątkami” → odsyłacz do `../08-wyjatki/index.md` | |
| `docs/index.md`, `mkdocs.yml` | pozycja „8. Wyjątki i zarządzanie zasobami” w spisie i w nav (blok wyżej) | nav rośnie wraz z powstającymi stronami |

Reguła: powyższe zmiany wykonujemy jednym zbiorczym etapem po zaakceptowaniu wszystkich stron rozdziału 8, z kontrolą semantyczną każdego zdania i sprawdzeniem kotwic w zbudowanym HTML (slugi MkDocs pomijają „ł”). Nie wykonujemy innych zmian w rozdziałach 1–7 (zdanie o EAFP w `05-typy-zlozone/slownik.md` i Zen w `02-konsola/konsola-w-praktyce.md` należą do osobnych etapów z sekcji 6 `PLAN_ROZWOJU.md`). Komentarze `TODO` wskazujące na klasy, narzędzia typów, tkinter i korutyny pozostają.

## CONTENT HANDOFF (rozbieżności ze źródłami)

Książka ma rację, materiały kursu do poprawki: (a) W05 sl. 19 literówka „divisio by zero”; (b) W05 sl. 21 i 28 `open()` bez `encoding` — książka zawsze z `encoding="utf-8"`; (c) W05 sl. 25 „`except Exception:` równie złe” — książka rozróżnia: `except Exception` z zapisem do dziennika i ponownym zgłoszeniem jest poprawnym wzorcem na najwyższym poziomie programu, goły `except:` nie jest nigdy; (d) W05 sl. 30 „EAFP jest często szybsze” — od 3.11 wejście w `try` jest bezpłatne, ale zgłoszony wyjątek kosztuje więcej niż sprawdzenie; wybór zależy od częstości błędu; (e) W05 sl. 36 „cykliczny import: przesuń import do wnętrza funkcji” — książka (rozdział 7) zaleca podział modułów; (f) W05 sl. 37 i 45 oraz W08 sl. 34: f-stringi w `logging` → `%s` z argumentami; goły `except:` przy `traceback.print_exc()` → `except Exception`; timer bez `try/finally` → z `try/finally`; (g) W08 sl. 36 `chdir('/tmp')` — ścieżka uniksowa, przykład pominięty; (h) W03 sl. 19 „pythonowy styl to EAFP — używaj try/except zamiast sprawdzania” — książka: `get()` jest zwykle najlepszym rozwiązaniem dla słownika; (i) plan zbiorczy wskazywał `python_thread.txt` sl. 10–11, 18 jako źródło o logging — slajdy nie zawierają takiej treści. Bez konfliktu: składnia `try/except/else/finally`, `raise … from`, hierarchia (uzupełniona o `ExceptionGroup`, `PythonFinalizationError` w 3.13), `pytest.raises`, `suppress`, `ExitStack`.

## Checklista weryfikacyjna strony (przed odbiorem)

1. Wszystkie deterministyczne przykłady uruchomione na `.venv` (3.14.7): skrypty przez `scripts/verify_page.py` (z plikami danych i `--stdin`), sesje REPL i pdb osobno, polecenia terminalowe (`python -O`, `python -m pytest`, `python -m pdb`) ręcznie w katalogu próbnym; pytest w tymczasowym venv z odnotowaną wersją; ślady wywołań, ostrzeżenia kompilatora, wyniki pytest i wpisy dziennika wpisane z uruchomienia; wartości zależne od komputera lub czasu oznaczone.
2. Brak mechanizmów z późniejszych rozdziałów: `class`, zapis do plików, `pathlib`/`os`/`tempfile`/`io`, wątki; `open()` wyłącznie w zakresie decyzji 10; własne wyjątki tylko w zapowiedzi.
3. Kolejność wewnątrz rozdziału: podrozdział używa wyłącznie pojęć z podrozdziałów wcześniejszych i rozdziałów 1–7; `with` przed stroną 4 tylko w `pytest.raises` z zapowiedzią; `{x!r}`, `__debug__`, `time.perf_counter()` wprowadzone w miejscu użycia.
4. Nazwy plików przykładowych bez kolizji z biblioteką standardową (nie: `logging.py`, `traceback.py`, `test.py`); funkcja `silnia()` spójna między stronami 2, 3 i 5; plik `dane.txt` spójny na stronie 4.
5. Formy składniowe: `except (A, B):` jako kanoniczna, PEP 758 raz; `as e` (decyzja 8); `raise Typ("komunikat")` z komunikatami po polsku; każdy `open()` z `encoding="utf-8"` i w `with` (poza sekcją pokazującą `try/finally`).
6. Ślady wywołań w brzmieniu 3.14.7 z maskowaniem ścieżek; podpowiedź „Did you mean” raz; kolory prozą; `<python-input-N>` numerowane od zera.
7. Terminologia i nagłówki zgodne z zasadami; „podrozdział” dla części książki; „menedżer kontekstu”, „pułapka”, „dziennik” z terminami angielskimi przy pierwszym użyciu.
8. Konwencje `CLAUDE.md`: bloki z `title=` albo `.no-copy`, `json title="launch.json"`, admonitions z polskimi tytułami, cudzysłowy „…”, klawisze `++…++`, `python -m pip`.
9. Zrzuty: znaczniki `TODO: screenshot` wyłącznie w `diagnostyka.md` (3), wpisy w `ZRZUTY.md` z nazwami plików od treści; wszystko inne jako tekst.
10. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml` (bez warstwy interaktywnej w wyniku); testy `python -m unittest discover -s tests` i `node --test` bez regresji.
11. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji (`id` sprawdzone w zbudowanym HTML); odsyłacze w przód wyłącznie prozą.
12. Struktura: do około 6 H2 jako wskazówka; sekcje uzupełniające oznaczone w tytule H2 „(dla dociekliwych)” albo notą; długość według treści.

## Checklista finalnego odbioru rozdziału

1. Wszystkie siedem plików zaakceptowanych; nav i `docs/index.md` zawierają komplet pozycji; H1 = etykieta nav (index: „Wprowadzenie” / H1 „8. Wyjątki i zarządzanie zasobami”).
2. Zbiorcza redakcja: ujednolicona terminologia, spójna `silnia()`, spójne maskowanie ścieżek, brak powtórzeń między stronami 1–2 (ślad) i 5 (ślad) oraz 5–6 (`print_exc` a `exception()`).
3. Tabela „Zmiany w rozdziałach 1–7” wykonana w całości; w `docs/06-funkcje/` i `docs/07-moduly/` nie pozostał żaden komentarz ani zdanie odsyłające do „rozdziału o wyjątkach” bez odsyłacza.
4. Pełny przebieg weryfikacji: `verify_page.py` dla wszystkich stron rozdziału, bloki REPL i pdb, polecenia terminalowe, pytest w tymczasowym venv, audyt kotwic, oba buildy, testy warstwy interaktywnej, `git diff --check`.
5. Ponowna kontrola faktów zależnych od wersji: PEP 758/765 (3.14), `add_note` (3.11), `except*` (3.11), nawiasy w `with` (3.10), `contextlib.chdir` (3.11), `basicConfig(encoding=)` (3.9), nazwa i identyfikator rozszerzenia debuggera, zmiany pdb w 3.14, wersja pytest.
6. `PLAN_ROZWOJU.md`: status rozdziału 8 „ukończony” z rzeczywistą liczbą linii; `ZRZUTY.md` z trzema wpisami; CONTENT HANDOFF przekazany autorowi w raporcie końcowym.
7. Commit końcowy; bez integracji do `dev` bez osobnego polecenia.
