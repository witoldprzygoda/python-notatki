# Rozdział 9. Wejście, wyjście i pliki — plan implementacyjny

Skondensowany projekt stron rozdziału 9 według `PLAN_ROZWOJU.md` (sekcja 4, „9. Wejście, wyjście i pliki”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/09-wejscie-wyjscie` (z `dev` po integracji rozdziału 8, commit `ce4670a`). Stan odniesienia: Python 3.14.7 w `.venv` projektu (Windows, strona kodowa systemu na komputerze autora: cp1252; w polskim Windows zwykle cp1250), MkDocs Material.

## Decyzje autora (13 IX 2026)

1. **Bez not laboratoryjnych i bez „Ściągi”.** Materiały laboratorium 2 są źródłem przykładów, nie treścią do zaznaczania; `index.md` w układzie rozdziałów 6–8: wstęp prozą, `---`, `## W tym rozdziale`.
2. **Struktura:** index + 7 podrozdziałów w kolejności: formatowanie tekstu → funkcja `print` i strumienie → animacje w terminalu → pliki tekstowe → typ `bytes` i pliki binarne → ścieżki i system plików → formaty danych CSV i JSON.
3. **Nowości Pythona 3.14 jako zwykły materiał**, bez not „Nowości Pythona 3.14”: t-stringi (`string.templatelib`), separator tysięcy w części ułamkowej, `Path.copy()`/`move()`/`info`, `python -m json`, pakiet `compression` (`compression.zstd`). Wersję, od której coś istnieje, podajemy jednym dopiskiem „(od Pythona 3.14)” tam, gdzie czytelnik może trafić na starszy interpreter.
4. **Animacje w terminalu** pozostają osobnym podrozdziałem uzupełniającym z sekcji PRINT notatek autora; etykieta nav i H1 „Animacje w terminalu” bez dopisku, charakter uzupełniający zaznaczony w pierwszym akapicie i w `index.md` (jak `itertools` w rozdziale 7). Harness nie weryfikuje animacji — autor sprawdza je ręcznie w Windows Terminal; w książce wyniki opisujemy prozą, ewentualnie ostatnią klatką jako blok tekstowy.
5. **Przykłady samowystarczalne:** każdy skrypt, który czyta plik, wcześniej ten plik tworzy (albo plik jest podany blokiem `text title="…"` i zapisywany przez harness); żaden przykład nie zależy od plików spoza katalogu programu ani od katalogów użytkownika. Przykłady z przekierowaniem (`>`, `<`, `|`) i `python -m json` jako bloki `powershell title="Terminal"` weryfikowane ręcznie.
6. **Kodowanie:** każde `open()` z jawnym `encoding` (domyślnie `"utf-8"`), także `Path.read_text()`/`write_text()`; strona kodowa Windows opisana ogólnie („cp1250 lub cp1252, zależnie od ustawień regionalnych”), z pokazem odczytu pliku UTF-8 w złym kodowaniu i `UnicodeDecodeError`/`UnicodeEncodeError`; PEP 686 (UTF-8 domyślnie od Pythona 3.15) jako fakt bez etykiety nowości; tryb UTF-8 (`-X utf8`, `PYTHONUTF8=1`) jako sposób pracy do czasu 3.15.
7. **Szacunek rozmiaru** z `PLAN_ROZWOJU.md` (1000–1100 linii) orientacyjny; przy gęstości rozdziałów 6–8 spodziewane ok. 1800–2200 linii.
8. **Czyszczenie ekranu w animacjach:** sekwencje sterujące ANSI (`\033[2J\033[H`, `\033[F`) jako podstawa — działają w Windows Terminal i terminalach uniksowych; `os.system("cls")` z notatek autora jako wzmianka (uruchamia powłokę, zależne od systemu). Korekta tezy notatek „nie da się cofnąć kursora do poprzedniej linii”: sekwencje ANSI to umożliwiają.
9. **Zapowiedzi z rozdziału 8 domykane na miejscu:** dziennik `logging` w pliku (`basicConfig(filename=…, encoding="utf-8")`) jako krótka sekcja strony 4; `contextlib.redirect_stdout()` i `chdir()` na stronach 2 i 6; operator `%` na stronie 1; `open()` w pełni na stronie 4. Obiekt własny z metodą `write()` (klasa `Pisarz` z notatek) — zapowiedź „w rozdziale o modelu danych” z `TODO`.
10. **Zrzut ekranu IDLE z rozdziału 2** (sygnatura `print()`, `ZRZUTY.md` poz. 8): po napisaniu strony 2 zastępujemy w `02-konsola/konsola-w-praktyce.md` znacznik `TODO: screenshot` blokiem tekstowym z sygnaturą i odsyłaczem do strony 2, a pozycję 8 usuwamy z `ZRZUTY.md` (zgodnie z `PLAN_ROZWOJU.md`, sekcja 6). *(Do potwierdzenia.)*
11. **`pickle`:** wyłącznie ostrzeżenie prozą (format niebezpieczny dla danych z niezaufanego źródła, niestabilny między wersjami) bez przykładu; `tomllib` jednym przykładem odczytu `pyproject.toml` z rozdziału 7; `compression.zstd` jednym przykładem kompresji bajtów.
12. **Bez Gita, bez klas, bez wątków** (zasada 9 `PLAN_ROZWOJU.md`; klasy od rozdziału 10, wątki od 15).

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez `class` (`Pisarz`, własne menedżery kontekstu jako klasy — zapowiedź), bez wątków, bez NumPy, bez `dataclass`. Wyjątki zgłaszane i obsługiwane zgodnie z rozdziałem 8 (`try`/`except`, `with`, `raise` z komunikatem, `as e`).
- Moduły biblioteki standardowej użyte w kodzie: `sys`, `os` (tylko `os.linesep`, `os.name`, `os.getcwd()`, `os.path` w tabeli odpowiedników), `pathlib`, `shutil`, `tempfile`, `csv`, `json`, `struct`, `io` (`StringIO`, `BytesIO`), `pprint`, `string.templatelib`, `tomllib`, `compression` (`zstd`), `time` (`sleep()` w animacjach), `contextlib` (`redirect_stdout`, `chdir`), `logging` (dziennik w pliku), `locale` (`getencoding()` jednym wywołaniem). Żaden inny moduł nie pojawia się w kodzie; `pickle`, `codecs`, `glob`, `fileinput`, `mmap`, `zipfile`, `tarfile` co najwyżej prozą.
- Kolejność wewnątrz rozdziału: strona 1 (formatowanie) korzysta tylko z rozdziałów 1–8; strona 2 wprowadza strumienie i buforowanie przed animacjami (strona 3); strona 4 (`open()`) przed binarnymi (5); strona 6 (`pathlib`) po 4–5, bo używa `read_text`/`write_bytes`; strona 7 (CSV/JSON) po 4 i 6 (`newline`, kodowanie, `Path`). Strona 3 jest uzupełniająca — dalsze strony nie zależą od niej.
- Pojęcia wprowadzane jawnie w miejscu pierwszego użycia: „specyfikacja formatu” i „typ prezentacji”; „wieloznacznik” (znany z rozdziału 8) w kontekście `%`; „strumień standardowy” (`stdin`, `stdout`, `stderr` — `stdout`/`stderr` wprowadzone w rozdziale 8, tu uzupełnione o `stdin`); „przekierowanie” i „potok” w PowerShell; „buforowanie wierszowe / blokowe”; „sekwencja sterująca ANSI”; „kodowanie” a „strona kodowa”; „BOM”; „znacznik końca wiersza”; „bajt” a „znak”; „ścieżka bezwzględna / względna”; „katalog roboczy”; „serializacja (ang. *serialization*)”.
- Terminologia: „f-string”, „specyfikacja formatu (ang. *format specification*)”, „mini-język formatu (ang. *format specification mini-language*)”, „t-string (ang. *template string*)”, „strumień (ang. *stream*)”, „standardowe wejście/wyjście/strumień błędów”, „przekierowanie (ang. *redirection*)”, „potok (ang. *pipe*)”, „buforowanie (ang. *buffering*)”, „opróżnienie bufora (ang. *flush*)”, „kodowanie (ang. *encoding*)”, „strona kodowa (ang. *code page*)”, „znak (ang. *character*)” a „bajt (ang. *byte*)”, „plik tekstowy / binarny”, „tryb otwarcia (ang. *mode*)”, „ścieżka (ang. *path*)”, „serializacja / deserializacja”; „podrozdział” dla części książki.
- Nagłówki w formie rzeczownikowej; nazwy w nagłówkach w kodzie (np. „Funkcja `open()` i tryby otwarcia”, „Argument `file` i przekierowanie wyjścia”).
- Docstringi `"""Zwraca ..."""`, `"""Zapisuje ..."""`, `"""Wczytuje ..."""`; nazwy plików danych po polsku, bez kolizji z biblioteką standardową (nie: `csv.py`, `json.py`, `io.py`, `string.py`, `struct.py`, `compression.py`, `time.py`, `logging.py`).
- Konwencje `CLAUDE.md`: bloki `python title="plik.py"`, `text title="dane.txt"`/`csv title="oceny.csv"`/`json title="ustawienia.json"`/`toml title="pyproject.toml"` dla plików danych (harness zapisuje je przed uruchomieniem skryptów), `powershell title="Terminal"` dla poleceń (przekierowania, `python -X utf8`, `python -m json`), `{ .python .no-copy }` dla REPL, `{ .text .no-copy }` dla wyników, zawartości plików wypisywanej bajtami, tabel tekstowych i sygnatur; admonitions z polskimi tytułami; cudzysłowy „…”; klawisze `++ctrl+z++`, `++ctrl+c++`; terminy angielskie z „ang.” przy pierwszym użyciu.
- Zapowiedzi w przód prozą po temacie, bez numeru rozdziału, z komentarzem `<!-- TODO: link po powstaniu rozdziału o … -->` i wpisem w „Zapowiedzi i luki” właściwego rozdziału w `PLAN_ROZWOJU.md` (model danych: obiekt z `write()`, własny menedżer kontekstu; klasy danych: zapis obiektów do JSON; NumPy: pliki liczbowe; współbieżność: dziennik z wątków — jeśli padnie).
- Weryfikacja: `scripts/verify_page.py` na `.venv` (3.14.7, interpreter uruchamiany z `-X utf8` — harness) dla skryptów i plików danych; przykłady z `input()` przez `--stdin`; sesje REPL osobno; przekierowania, potoki, `python -X utf8`, `PYTHONUTF8`, `python -m json`, `EncodingWarning` (`-X warn_default_encoding`) i przykłady pokazujące stronę kodową — ręcznie w PowerShell **bez** trybu UTF-8 (wyniki wpisane z uruchomienia, z zaznaczeniem, że zależą od strony kodowej systemu); animacje — ręcznie przez autora; wyniki zależne od komputera (rozmiary plików w bajtach są deterministyczne; daty modyfikacji, ścieżki bezwzględne, `Path.home()` — maskowane albo opisane). Skrypty zapisujące pliki pracują w katalogu programu (harness: katalog tymczasowy).
- `index.md` w układzie rozdziałów 6–8. Odsyłacze do rozdziałów 1–8 wewnątrz nowych stron dozwolone od razu; zmiany w rozdziałach 1–8 (tabela na końcu) zbiorczo po ukończeniu wszystkich stron rozdziału 9. Strony rozdziału 4 z markerami aktywności nie są dotykane.

## Strony

### 1. `formatowanie.md` — Formatowanie tekstu

**Cel.** Czytelnik panuje nad wyglądem liczb i tekstu: zna mini-język specyfikacji formatu (szerokość, wyrównanie, znak, separatory, precyzja, typy prezentacji), buduje tabele, zna `format()`, `str.format()` i operator `%` (na potrzeby `logging` i kodu zastanego) oraz wie, czym są t-stringi i `pprint`.

**Kolejność H2/H3.**
1. F-stringi — wyrażenia, konwersje i pola zagnieżdżone (`{x!r}`, `{x=}`, `{x:{szer}}`)
2. Mini-język specyfikacji formatu (H3: Szerokość, wypełnienie i wyrównanie; H3: Liczby — znak, separatory, precyzja i systemy; H3: Typy prezentacji — tabela)
3. Wypisywanie tabel
4. Funkcja `format()` i metoda `str.format()`
5. Operator `%`
6. Szablony t-string i moduł `pprint` (dla dociekliwych)

**Pojęcia wprowadzane.** Składnia pola `{wyrażenie!konwersja:specyfikacja}`; konwersje `!r`, `!s`, `!a`; `=` do diagnostyki (`{x=}` → `x=…`, ze spacjami `{x = }`); pola zagnieżdżone w specyfikacji; gramatyka specyfikacji w bloku `.text` (`[[fill]align][sign][z][#][0][width][grouping][.precision][type]` w uproszczeniu); wyrównanie `<`, `>`, `^`, `=` z wypełnieniem; `+`, ` `; `,` i `_` (także w części ułamkowej od 3.14); `0` przed szerokością; precyzja dla `f`/`e`/`g` i jako obcięcie łańcucha; typy `d`, `b`, `o`, `x`, `X`, `#`, `c`, `f`, `e`, `g`, `%`, `s`; tabela wierszami z `{:<12}{:>8.2f}`; `format(x, spec)` jako to, co robi f-string; `str.format()` z indeksami i nazwami (kod zastany, szablony zapisane w zmiennej); operator `%` (`%s`, `%d`, `%.2f`, `%5s`, słownik `%(nazwa)s`) jako mechanizm `logging` z rozdziału 8 i starszego kodu — bez zalecania; t-string: literał `t"…"` zwraca `Template` (od 3.14), atrybuty `strings`, `interpolations`, `values`, `Interpolation` z `value`/`expression`/`conversion`/`format_spec`, przetwarzanie przed sklejeniem (np. wartości w nawiasach albo escape HTML jako motywacja) — jeden krótki przykład; `pprint.pprint()` z `width=` dla zagnieżdżonych struktur.

**Zależności.** F-stringi i `:.2f`, `08b`, `_` z rozdziału 3 (`typy-proste.md#f-stringi`); `repr()` (3), `{x!r}` (8); `%s`/`%r`/`%d` z `logging.md` (8); słowniki i listy (5); `sorted(key=)` (6) w tabeli.

**Główne przykłady.** `pola.py` (`!r`, `=`, zagnieżdżone `{szer}`); `wyrownanie.py` (`{'ab':>6}`, `*^`, `{42:05d}`, `{-3:=+6d}`); `liczby.py` (`,`, `_`, `.3e`, `g`, `.0%`, `#x`, `08b`, `.,` w części ułamkowej); `tabela.py` (lista krotek produkt–cena–ilość, nagłówek i wiersze z szerokościami, suma); `format-metoda.py` (`"{0} {1}".format`, `"{imie}".format(imie=…)`, szablon w zmiennej); `operator-procent.py` (`"%s ma %d lat" % (…)`, `%.2f`, `%(nazwa)s`); `tstring.py` (`t"…"`, `Template.strings/values`, prosta funkcja składająca z `format(value, format_spec)`); `pprint.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `f"{1234567.891:,.2f}"` → `'1,234,567.89'`; `f"{x:_.1f}"` → `'1_234_567.9'`; `f"{0.5:.0%}"` → `'50%'`; `f"{42:#x}"` → `'0x2a'`; `f"{'ab':*^6}"` → `'**ab**'`; `f"{'abcdef':.3}"` → `'abc'`; `f"{x=}"` → `x=1234567.891`; `f"{x=:.1f}"` → `x=1234567.9`; `f"{'ż'!a}"` → `'\u017c'`; `"%5.2f|%-6s|%x" % (3.14159, "ab", 255)` → `' 3.14|ab    |ff'`; `type(t"…").__name__` → `Template`, `.strings` → krotka o jeden element dłuższa od `.values`; grupowanie w części ułamkowej (`{x:,.,}` lub `{x:.,}`) — brzmienie wyniku sprawdzić przy pisaniu.

**Źródła repozytorium.** `Wyklad_01.txt` sl. 23 (f-string `.2f`); `Wyklad_02.txt` sl. 39 (`08b`, `#06x`, `_`); `03-nazwy-typy/typy-proste.md:232–254` (zapowiedź mini-języka); `PythonNotatki.txt` s. 126 (formatowanie i `pprint` odłożone — „na pewno poruszony tu materiał można będzie rozbudować”).

**Źródła zewnętrzne.** *Format Specification Mini-Language* (`string.html#formatspec`, w tym „Changed in version 3.14: grouping for the fractional part”); *printf-style String Formatting*; `string.templatelib` (3.14, PEP 750); `pprint`; tutorial *Fancier Output Formatting*.

**TODO/zapowiedzi do domknięcia.** `03-nazwy-typy/typy-proste.md:254` (odsyłacz do dokumentacji mini-języka → dodatkowo odsyłacz do strony); `08-wyjatki/logging.md:127` (`TODO` o operatorze `%`) → sekcja 5.

**Odłożone.** `string.Template` (klasyczny, `$nazwa`) — jedno zdanie; `locale` w formatowaniu (`n`); `Decimal` w formatowaniu (rozdział 3 wystarcza); `textwrap`.

**Ryzyka kolejności pojęć.** Gramatyka specyfikacji tylko w uproszczeniu i jako blok tekstowy, bez pełnej notacji dokumentacji; t-stringi wymagają `isinstance()` (rozdział 3) i iteracji po `Template` — krótko, bez `convert()`; nie sugerować, że `%` jest przestarzały w `logging`.

**Orientacyjny rozmiar.** ok. 320–380 linii.

### 2. `print-i-strumienie.md` — Funkcja print i strumienie

**Cel.** Czytelnik zna pełną sygnaturę `print()`, znaki sterujące terminala, trzy strumienie standardowe i ich przekierowania w PowerShell, rozumie buforowanie (`flush`, `-u`), kieruje wyjście do pliku argumentem `file` i wie, co robi `input()` przy końcu wejścia.

**Kolejność H2/H3.**
1. Pełna sygnatura `print()`
2. Znaki sterujące w `sep` i `end`
3. Strumienie standardowe (H3: Przekierowanie i potok w PowerShell; H3: Kodowanie strumieni — konsola a przekierowanie)
4. Buforowanie i argument `flush`
5. Argument `file` — wyjście do pliku i `redirect_stdout()`
6. Funkcja `input()` i koniec wejścia

**Pojęcia wprowadzane.** `print(*objects, sep=" ", end="\n", file=None, flush=False)` jako blok `.text` (domyka `TODO: screenshot` z rozdziału 2 — decyzja 10); `sep`/`end` jako argumenty tylko nazwane (rozdział 6), `print()` bez argumentów, `sep=""`; `\n`, `\t`, `\r`, `\b`, `\a` — efekt zależny od terminala (Windows Terminal), `\r` jako podstawa animacji; `sys.stdin`, `sys.stdout`, `sys.stderr` jako obiekty plików tekstowych (`TextIOWrapper`), `print(…, file=sys.stderr)`; PowerShell: `>` (nadpisanie), `>>` (dopisanie), `2>` (strumień błędów), `|` (potok, np. do `Select-String`), `<` — w PowerShell brak operatora `<`, wejście z pliku przez `Get-Content plik | python program.py`; kodowanie: konsola Windows przyjmuje UTF-8 niezależnie od strony kodowej, ale strumień przekierowany do pliku lub potoku używa strony kodowej systemu (cp1250/cp1252) — polskie znaki dają `UnicodeEncodeError` (pokaz ręczny), lekarstwo: `python -X utf8 program.py` albo `$env:PYTHONUTF8 = "1"`, od Pythona 3.15 tryb UTF-8 domyślny (PEP 686); `PYTHONIOENCODING` jednym zdaniem; buforowanie wierszowe (terminal) a blokowe (plik/potok), `flush=True`, opcja `-u`/`PYTHONUNBUFFERED` (dowolny niepusty łańcuch — korekta „TRUE” z notatek), testy w terminalu, nie w REPL ani panelu OUTPUT VSC (lab2); `file=plik` z `with open(…, "w", encoding="utf-8")`, `contextlib.redirect_stdout()` z rozdziału 8 zamiast ręcznej podmiany `sys.stdout` z notatek; obiekt z metodą `write()` — zapowiedź (klasa `Pisarz`, model danych, `TODO`); `input(prompt)` pisze zachętę na `stdout`, czyta ze `stdin` bez `\n`, `EOFError` przy końcu wejścia (`Get-Content dane.txt | python program.py` po ostatnim wierszu; ++ctrl+z++ i Enter w konsoli Windows).

**Zależności.** `print`/`input` (2); `sep`/`end` (2); argumenty nazwane (6); strumienie `stdout`/`stderr` i przekierowanie `>` (8: `obsluga-wyjatkow.md`); `with open()` i `redirect_stdout` (8); `sys.exit()` i kody wyjścia (7).

**Główne przykłady.** `sygnatura.py` (`sep`, `end`, pusty `print()`, `sep=""`); `znaki-sterujace.py` (`\t` tabela, `\r` nadpisanie wiersza — wynik końcowy jako tekst, `\b`); `strumienie.py` (`print` na `stdout` i `stderr`) + Terminal `python strumienie.py > wynik.txt` i `2> bledy.txt`, `Get-Content wynik.txt`; `polskie.py` z `print("zażółć")` + Terminal bez i z `-X utf8` (wynik z uruchomienia autora, cp1252/cp1250 zaznaczone); `bufor.py` (pętla z `sleep(0.5)`, `flush=False` a `True`; opis efektu prozą, bo harness nie widzi czasu) + Terminal `python -u bufor.py`; `do-pliku.py` (`file=plik`, `redirect_stdout`); `wejscie.py` (`input()` w pętli z `except EOFError`) z `--stdin` i Terminal `Get-Content dane.txt | python wejscie.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `print("a", "b", sep="-", end="!\n")` → `a-b!`; `print()` → pusty wiersz; `sys.stdout.line_buffering` → `True` w terminalu, `False` w potoku (pokaz ręczny); przekierowanie z polskimi znakami bez UTF-8 → `UnicodeEncodeError: 'charmap' codec can't encode character '\u017c' …` (na cp1252; na cp1250 zapis się powiedzie w cp1250 — opisać oba przypadki); z `-X utf8` plik w UTF-8; `input()` po końcu wejścia → `EOFError: EOF when reading a line`; `redirect_stdout()` przechwytuje `print()`; `PYTHONUNBUFFERED=x` działa jak `-u`.

**Źródła repozytorium.** `PythonNotatki.txt` s. 121–122, 124–126 (PRINT: sygnatura, znaki sterujące, `flush`, buforowanie, `-u`/`PYTHONUNBUFFERED`, `file=`, podmiana `sys.stdout`, `Pisarz`); `lab2.txt` sl. 3 (flush, panel OUTPUT z `-u`); `Wyklad_01.txt` sl. 23; `Wyklad_08.txt` sl. 6 (podmiana `sys.stdout` — do korekty), 37 (buforowanie, `buffering=`), 39 (`Pisarz`, `StringIO`); `02-konsola/konsola-w-praktyce.md:30–47`.

**Źródła zewnętrzne.** `print()`, `input()` (functions); `sys.stdin/stdout/stderr` i `io.TextIOWrapper` (line buffering, `reconfigure()`); cmdline: `-u`, `PYTHONUNBUFFERED`, `-X utf8`, `PYTHONUTF8`, `PYTHONIOENCODING`, `PYTHONLEGACYWINDOWSSTDIO` (jedno zdanie); PEP 686; PEP 528/529 (konsola Windows w UTF-8) jako numery; dokumentacja PowerShell o przekierowaniach (`about_Redirection`).

**TODO/zapowiedzi do domknięcia.** `02-konsola/konsola-w-praktyce.md:32–34` (sygnatura `print` — zrzut IDLE) → sekcja 1 (decyzja 10); `07-moduly/argumenty-wiersza-polecen.md:212` („w tej książce nie odróżniamy jeszcze strumienia błędów od zwykłego wyjścia”) → sekcja 3; `08-wyjatki/with-i-contextlib.md:280` (`redirect_stdout`) → sekcja 5.

**Odłożone.** `sys.stdout.reconfigure()` (jedno zdanie); `io.StringIO` (strona 5); `PYTHONLEGACYWINDOWSSTDIO`; `readline`; `getpass`; `argparse` w potokach.

**Ryzyka kolejności pojęć.** Przekierowania dotyczą PowerShell — Git Bash w zakładce `=== "Git Bash"` tylko tam, gdzie składnia się różni (`<` istnieje w Bashu); efekt `\b`/`\a` zależy od terminala — pisać ostrożnie; nie mylić kodowania konsoli (UTF-8 przez API Windows) z kodowaniem przekierowanego strumienia (strona kodowa).

**Orientacyjny rozmiar.** ok. 300–360 linii.

### 3. `animacje-w-terminalu.md` — Animacje w terminalu

**Cel.** Podrozdział uzupełniający: czytelnik wykorzystuje `\r`, `end=""`, `flush=True` i `time.sleep()` do prostych animacji w jednym wierszu, a sekwencje ANSI do przerysowania wielu wierszy; rozumie, dlaczego to działa i gdzie są granice.

**Kolejność H2/H3.**
1. Zasada: nadpisywanie wiersza
2. Wskaźnik postępu i „maszyna do pisania”
3. Odbijająca się piłeczka
4. Wiele wierszy — sekwencje sterujące ANSI
5. Ograniczenia i zastosowania

**Pojęcia wprowadzane.** `\r` + `end=""` + `flush=True` + `sleep()`; wskaźnik obrotowy (ang. *spinner*) `|/-\`; „maszyna do pisania” z `chr(0x2593)` ▓ (korekta: to kod Unicode U+2593, nie ASCII), `\b`; pasek postępu `[####    ]` z `f"{procent:3.0f}%"` (formatowanie ze strony 1); piłeczka w poziomie (`' ' * pozycja + 'O'`); sekwencje ANSI: `\033[2J` (czyszczenie ekranu), `\033[H` (kursor w lewy górny róg), `\033[nA`/`\033[F` (kursor w górę), ukrycie kursora `\033[?25l`/`\033[?25h` — obsługiwane przez Windows Terminal i terminale uniksowe; wzmianka o `os.system("cls")` jako wariancie z notatek; piłeczka w pionie i pulsujący kwadrat z `chr(0x2588)` █, `chr(0x2580)` ▀, `chr(0x2584)` ▄ (notatki, s. 123–124); ograniczenia: REPL, panel OUTPUT VSC i przekierowany strumień nie animują; zastosowania: pasek postępu przy długich obliczeniach (`tqdm` jako pakiet zewnętrzny — nazwa).

**Zależności.** Strona 2 (`\r`, `flush`, buforowanie); `time.sleep()` (nowe — jedno zdanie); `chr()` (3); f-stringi (1); pętle `while` z warunkiem czasowym (`time.time()`/`time.perf_counter()` — 8).

**Główne przykłady.** `spinner.py`; `maszyna.py`; `pasek-postepu.py`; `pileczka.py`; `ekran.py` (piłeczka w pionie z ANSI); `kwadrat.py` (pulsujący). Wyniki: prozą i ostatnia klatka jako `{ .text .no-copy }` tam, gdzie ma sens; wszystkie sprawdza ręcznie autor (decyzja 4). Harness: skrypty uruchamiane, ale bez bloku wyniku (albo z blokiem ostatniej klatki po masce) — ustalić przy pisaniu; `sleep()` skrócić parametrem, by harness nie czekał długo (np. stała `OPOZNIENIE`).

**Wymagane zachowania do weryfikacji.** Sekwencje ANSI działają w Windows Terminal 3.14 bez dodatkowej inicjalizacji (sprawdzić także w starym oknie `conhost` — jeśli nie, jedno zdanie o `os.system("")` włączającym obsługę VT); `chr(0x2593)` → `'▓'`; `\b` w Windows Terminal cofa kursor bez kasowania znaku (opisać).

**Źródła repozytorium.** `PythonNotatki.txt` s. 121–124 (spinner, maszyna, piłeczka pozioma i pionowa, kwadrat, `os.system('cls')`, teza o kursorze); `lab2.txt` sl. 4–5; `Wyklad_08.txt` sl. 37.

**Źródła zewnętrzne.** Dokumentacja Windows Terminal / *Console Virtual Terminal Sequences* (Microsoft Learn); ECMA-48 jako nazwa normy; `time.sleep()`.

**TODO/zapowiedzi do domknięcia.** Brak (materiał z notatek autora, dotąd nieobecny w książce).

**Odłożone.** `curses` (brak na Windows bez pakietu), `rich`, `tqdm` (nazwy); kolory ANSI (jedno zdanie z przykładem `\033[31m`?) — decyzja przy pisaniu, najwyżej jeden przykład.

**Ryzyka kolejności pojęć.** Strona nie może stać się kursem terminala — sześć przykładów, każdy do 25 wierszy; jasno oznaczyć, co zależy od terminala.

**Orientacyjny rozmiar.** ok. 220–280 linii.

### 4. `pliki-tekstowe.md` — Pliki tekstowe

**Cel.** Czytelnik otwiera pliki tekstowe we właściwym trybie i kodowaniu, czyta je w sposób oszczędny (iteracja), zapisuje i dopisuje, rozumie różnicę UTF-8 a strona kodowa Windows, wie, co robi `newline`, i prowadzi dziennik `logging` w pliku.

**Kolejność H2/H3.**
1. Funkcja `open()` i tryby otwarcia
2. Odczyt (H3: `read()`, `readline()`, `readlines()`; H3: Iteracja po wierszach)
3. Zapis i dopisywanie (H3: `write()`, `writelines()` i `print(file=)`; H3: Tryb `x` i nadpisywanie)
4. Kodowanie (H3: UTF-8 a strona kodowa Windows; H3: Znacznik BOM i `utf-8-sig`; H3: Obsługa błędów kodowania — `errors=`; H3: Tryb UTF-8 i Python 3.15)
5. Znaki końca wiersza — argument `newline`
6. Dziennik w pliku
7. Pozycja w pliku — `seek()` i `tell()` (dla dociekliwych)

**Pojęcia wprowadzane.** Sygnatura `open(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, …)` jako blok `.text`; tryby `r`, `w`, `a`, `x`, `+`, `t`/`b` — tabela; `FileExistsError` dla `x`; `read()` całość, `read(n)`, `readline()`, `readlines()`, iteracja jako wzorzec dla dużych plików (bez wczytywania całości), `strip()`/`rstrip("\n")`; `write()` nie dodaje `\n`, `writelines()`, `print(…, file=plik)`; `w` nadpisuje bez ostrzeżenia; domyślne kodowanie `locale.getencoding()` = strona kodowa (cp1250/cp1252) — pokaz: zapis w UTF-8, odczyt w cp1250 → tekst zniekształcony (`'zaĹĽĂłĹ‚Ä‡…'`), odczyt UTF-8 w cp1252 może zgłosić `UnicodeDecodeError`; `EncodingWarning` z `-X warn_default_encoding` (pokaz ręczny); BOM `\ufeff` z Notatnika/Excela, `utf-8-sig` do odczytu i zapisu dla Excela; `errors="replace"` (`�`), `"ignore"`, `"backslashreplace"`, `"surrogateescape"` jednym zdaniem; tryb UTF-8 i PEP 686 (od 3.15 domyślnie UTF-8; do tego czasu zawsze `encoding=`); `\r\n` w Windows: `os.linesep`, uniwersalne znaki końca wiersza przy odczycie, tłumaczenie `\n` → `\r\n` przy zapisie, `newline=""` wyłącza tłumaczenie (potrzebne w `csv`), podgląd bajtów przez `open(…, "rb")` (zapowiedź strony 5); `logging.basicConfig(filename="program.log", encoding="utf-8", level=…)` i odczyt pliku dziennika; `seek()`/`tell()` w trybie tekstowym: `tell()` zwraca nieprzezroczystą wartość, `seek(0)` na początek — korekta W08 sl. 38.

**Zależności.** `open()` jako czarna skrzynka, `with`, `FileNotFoundError` (8); `logging` (8); `str.strip()`, `split()`, sekwencje ucieczki, `r"…"` (3); `os.linesep` (nowe); `locale` (jedno wywołanie).

**Główne przykłady.** `tryby.py` (`w` → `a` → `x` z `FileExistsError` obsłużonym); `odczyt.py` (trzy metody na pliku `wiersze.txt` z bloku `text`); `iteracja.py` (zliczanie wierszy i słów); `zapis.py` (`write`, `writelines`, `print(file=)`); `kodowanie.py` (zapis UTF-8, odczyt w cp1250 → zniekształcenie, `encode()` porównanie bajtów); `bom.py` (`utf-8-sig`); `bledy-kodowania.py` (`errors="replace"`); Terminal: `python -X warn_default_encoding zle.py` (ręcznie); `newline.py` (bajty pliku z i bez `newline=""`); `dziennik-plik.py` (`basicConfig(filename, encoding)` + odczyt); `seek-tell.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** Zapis `"a\nb\n"` daje bajty `b'a\r\nb\r\n'`, z `newline=""` — `b'a\nb\n'`; odczyt bez `newline` → `'a\nb\n'`, z `newline=""` → `'a\r\nb\r\n'`; `"zażółć".encode("utf-8")` → 10 bajtów, `cp1250` → 6; odczyt pliku UTF-8 jako cp1250 → `'zaĹĽĂłĹ‚Ä‡ gÄ™Ĺ›lÄ… jaĹşĹ„'`; `errors="replace"` przy `ascii` → `'za���…'`; `-X warn_default_encoding` → `EncodingWarning: 'encoding' argument not specified`; `open("istnieje.txt", "x")` → `FileExistsError: [Errno 17] File exists: 'istnieje.txt'` (sprawdzić brzmienie); `locale.getencoding()` → `cp1252` na komputerze autora (opisać jako zależne od systemu); `utf-8-sig` zapisuje `b'\xef\xbb\xbf'`.

**Źródła repozytorium.** `Wyklad_08.txt` sl. 4–6 (open, odczyt, zapis — bez `encoding` do korekty), 12 (kodowanie; tabela `errors=` z przesuniętymi opisami do korekty; PEP 686), 38 (`seek`/`tell` — `tell()` nieprzezroczysty), 41 (niezamknięty plik); `lab2.txt`; `Wyklad_02.txt` sl. 17 („Python używa Unicode (UTF-8) domyślnie” — korekta: `str` to kody Unicode, UTF-8 to kodowanie).

**Źródła zewnętrzne.** `open()` (functions), `io` (*Text I/O*, `TextIOWrapper`, *Opt-in EncodingWarning*), `codecs` (lista kodowań — nazwy `cp1250`, `utf-8-sig`), PEP 597, PEP 686, tutorial *Reading and Writing Files*, `logging.basicConfig` (`filename`, `encoding`, `filemode`).

**TODO/zapowiedzi do domknięcia.** `08-wyjatki/with-i-contextlib.md:7` (`open()` pełne omówienie) → sekcje 1–4; `08-wyjatki/obsluga-wyjatkow.md:103` (`FileNotFoundError`/`open()`) → sekcja 1; `08-wyjatki/logging.md:156` (dziennik w pliku) → sekcja 6; `08-wyjatki/logging.md:158` i `08-wyjatki/index.md:7` (zapowiedź rozdziału) → strona/rozdział.

**Odłożone.** `buffering=` (jedno zdanie); `fileinput`; `codecs.open()`; pliki mapowane; `io.TextIOWrapper` jawnie; blokady plików.

**Ryzyka kolejności pojęć.** Strona kodowa komputera autora to cp1252, a plan zbiorczy zakładał cp1250 — teksty muszą opisywać oba przypadki i nie obiecywać konkretnego wyniku poza pokazem z zaznaczeniem systemu; `newline` tłumaczyć bez zagłębiania się w `io`; sekcja o dzienniku krótka (ok. 25 wierszy).

**Orientacyjny rozmiar.** ok. 380–440 linii.

### 5. `bytes-i-pliki-binarne.md` — Typ bytes i pliki binarne

**Cel.** Czytelnik odróżnia znaki od bajtów, koduje i dekoduje, zna typy `bytes`, `bytearray` i `memoryview` z katalogu typów rozdziału 3, czyta i zapisuje pliki binarne w blokach i rozpoznaje plik po nagłówku; dla dociekliwych — `struct` i pliki w pamięci.

**Kolejność H2/H3.**
1. Znaki a bajty — `encode()` i `decode()`
2. Typy `bytes`, `bytearray` i `memoryview`
3. Pliki binarne — tryby `rb` i `wb` (H3: Nagłówek pliku; H3: Kopiowanie w blokach)
4. Moduł `struct` (dla dociekliwych)
5. Pliki w pamięci — `io.StringIO` i `io.BytesIO` (dla dociekliwych)

**Pojęcia wprowadzane.** `str` jako ciąg kodów Unicode, `bytes` jako ciąg liczb 0–255; `len("zażółć")` = 6 a `len(b)` = 10 w UTF-8; literał `b"…"`, `repr` z `\x..`, indeks daje `int`, wycinek daje `bytes`; `bytes([80, 78, 71])`, `bytes.fromhex()`, `.hex()`; `bytearray` modyfikowalny; `memoryview` jako widok bez kopii (jedno zdanie i przykład); `int.to_bytes()`/`from_bytes()` z kolejnością bajtów; `open(…, "rb")` zwraca `bytes`, brak `encoding`, brak tłumaczenia `\r\n`; sygnatura PNG `b"\x89PNG\r\n\x1a\n"` — przykład tworzy własny plik binarny z tym nagłówkiem (samowystarczalność) i sprawdza go funkcją; kopiowanie w blokach `while (blok := f.read(65536))` (operator `:=` z rozdziału 4) i `shutil.copyfile()` jako gotowe; `struct.pack("<hHi", …)`/`unpack` z jawną kolejnością `<` (korekta W08: format bez prefiksu zależy od platformy), `calcsize`; `io.StringIO`/`io.BytesIO` jako plik w pamięci — `print(file=bufor)`, `getvalue()`; `redirect_stdout(io.StringIO())` do przechwycenia wyjścia w teście (łączy z rozdziałem 8 i pytest).

**Zależności.** Katalog typów (3: `nazwy-i-slowa-kluczowe.md:75` — typy binarne), `ord`/`chr` (3), kodowanie (strona 4), `with open()` (8), `:=` (4), `shutil` (strona 6 — tu tylko `copyfile`, zapowiedź).

**Główne przykłady.** `znaki-bajty.py`; `typy-binarne.py`; `naglowek.py` (zapis pliku z sygnaturą PNG + `rozpoznaj(sciezka)`); `kopiowanie.py` (bloki, porównanie rozmiarów); `struct-demo.py`; `w-pamieci.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `"zażółć".encode()` → `b'za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87'`, `len` 10; `b[0]` → `122`; `bytes([80, 78, 71])` → `b'PNG'`; `bytearray(b"abc")` z `ba[0] = 65` → `bytearray(b'Abc')`; `struct.pack("<hHi", -1, 65535, 100000)` → `b'\xff\xff\xff\xff\xa0\x86\x01\x00'`, `calcsize` → 8; `int.from_bytes(b"\x00\x10", "big")` → 16; `"zażółć".encode("ascii")` → `UnicodeEncodeError: 'ascii' codec can't encode characters in position 2-5: ordinal not in range(128)`.

**Źródła repozytorium.** `Wyklad_08.txt` sl. 8 (pliki binarne, `struct` — bez prefiksu do korekty), 39 (`StringIO`); `Wyklad_02.txt` sl. 17 (`ord`/`chr`); `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:75`.

**Źródła zewnętrzne.** *Binary Sequence Types* (stdtypes), `bytes.hex/fromhex`, `int.to_bytes`, `struct` (format characters, byte order), `io` (*Binary I/O*, `BytesIO`, `StringIO`), `shutil.copyfile`, specyfikacja PNG (sygnatura).

**TODO/zapowiedzi do domknięcia.** `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:75` (typy binarne w katalogu) → odsyłacz do strony (jedna edycja tekstu odsyłacza); `08-wyjatki/with-i-contextlib.md:280` (`redirect_stdout`) → sekcja 5 (razem ze stroną 2).

**Odłożone.** `memoryview` poza jednym przykładem; `array`; `mmap`; `base64` (jedno zdanie?); `hashlib` (rozdział o warsztacie?); obrazy (rozdział NumPy/Matplotlib).

**Ryzyka kolejności pojęć.** Nie wchodzić w Unicode poza tym, co potrzebne (UTF-8 zmiennej długości, BOM ze strony 4); `struct` tylko jako demonstracja; przykład PNG bez czytania prawdziwego obrazu (samowystarczalność), z prozą o zastosowaniu.

**Orientacyjny rozmiar.** ok. 260–320 linii.

### 6. `pathlib.md` — Ścieżki i system plików

**Cel.** Czytelnik operuje ścieżkami obiektowo (`Path`), zna katalog roboczy i ścieżki względne, przegląda katalogi wzorcami, tworzy, kopiuje, przenosi i usuwa pliki oraz katalogi, korzysta ze skrótów `read_text`/`write_text` i zna odpowiedniki w `os`, `shutil` i `tempfile`.

**Kolejność H2/H3.**
1. Ścieżki w systemie Windows i katalog roboczy
2. Obiekt `Path` (H3: Składanie ścieżek operatorem `/`; H3: Części ścieżki; H3: Pytania o plik — `exists()`, `is_file()`, `is_dir()`, `stat()`)
3. Przeglądanie katalogów — `iterdir()`, `glob()`, `rglob()` i `walk()`
4. Tworzenie, kopiowanie, przenoszenie i usuwanie
5. Odczyt i zapis skrótami — `read_text()` i `write_text()`
6. Moduły `os`, `shutil` i `tempfile`

**Pojęcia wprowadzane.** Separator `\` a `/`, `r"C:\…"`, ścieżka bezwzględna a względna, katalog roboczy (`Path.cwd()`, `os.getcwd()`), `Path.home()`; `Path("dane") / "raport.txt"`, `repr` → `WindowsPath('dane/raport.txt')`, `str(p)` → `dane\raport.txt`; `name`, `stem`, `suffix`, `parent`, `parts`, `with_suffix()`, `with_name()`, `resolve()`, `absolute()`; `exists()`, `is_file()`, `is_dir()`, `stat().st_size`, `Path.info` (od 3.14 — cache typu pliku, `info.is_file()`); `iterdir()`, `glob("*.txt")`, `rglob("*.py")`, `walk()` (od 3.12) — wyniki jako lista sortowana (kolejność systemu plików niedeterministyczna); `mkdir(parents=True, exist_ok=True)`, `touch()`, `copy()`/`copy_into()`/`move()`/`move_into()` (od 3.14), `rename()`/`replace()`, `unlink(missing_ok=True)`, `rmdir()` (tylko pusty), `shutil.rmtree()`, `shutil.copytree()`; `read_text(encoding="utf-8")`, `write_text(…, encoding="utf-8")`, `read_bytes()`, `write_bytes()`; tabela odpowiedników `os.path.join/exists/basename/splitext` → `Path`; `os.listdir`, `os.remove`, `os.makedirs`; `shutil.copy`/`move` jako starsze odpowiedniki; `tempfile.TemporaryDirectory()` jako menedżer kontekstu (rozdział 8) do bezpiecznych eksperymentów; `contextlib.chdir()` (8) jednym przykładem; `os.environ` jednym zdaniem (zmienne środowiskowe z rozdziału 1).

**Zależności.** `with` i menedżery kontekstu, `chdir()` (8); `open()` i kodowanie (strona 4); `bytes` (strona 5); `sorted()` (5); `sys.path` (7) jako lista ścieżek — nawiązanie; `r"…"` (3).

**Główne przykłady.** `sciezki.py` (`Path.cwd()`, składanie, części, `repr`/`str`); `pytania.py` (`exists`, `is_file`, `stat().st_size`, `info`); `przegladanie.py` (tworzy strukturę katalogów, `iterdir`, `glob`, `rglob`, `walk` — wyniki sortowane); `operacje.py` (`mkdir`, `touch`, `copy`, `move`, `unlink`, `rmdir`, `shutil.rmtree`); `skroty.py` (`write_text`/`read_text`/`read_bytes`); `tymczasowy.py` (`TemporaryDirectory` + `chdir`); tabela odpowiedników jako tabela Markdown.

**Wymagane zachowania do weryfikacji na 3.14.7.** `repr(Path("dane") / "raport.txt")` → `WindowsPath('dane/raport.txt')`, `str` → `dane\raport.txt`; `parts` → `('dane', 'raport.txt')`; `with_suffix(".csv")`; `copy()` zwraca nową `Path`, `info.is_file()` → `True`; `move()` → plik pod nową nazwą, stary nie istnieje; `unlink(missing_ok=True)` bez błędu; `rmdir()` niepustego → `OSError` (brzmienie na Windows sprawdzić); `write_text` do nieistniejącego katalogu → `FileNotFoundError: [Errno 2] … 'brak\\plik.txt'`; `walk()` krotki `(katalog, podkatalogi, pliki)`; `TemporaryDirectory` usuwa katalog po bloku.

**Źródła repozytorium.** `Wyklad_08.txt` sl. 9 (pathlib — `write_text` bez `encoding` do korekty); `Wyklad_05.txt` sl. 38 (os.path a pathlib — `read_text()` bez `encoding` do korekty); `Wyklad_08.txt` sl. 32 (pipeline z `Path.glob` — `open()` bez `with`/`encoding`, poza zakresem); `01-instalacja/sciezki-i-utrzymanie.md` (dwa znaczenia „ścieżki”).

**Źródła zewnętrzne.** `pathlib` (3.14: `copy`, `move`, `info`, `walk` 3.12, `glob` zmiany 3.13/3.14, tabela *Corresponding tools*), `shutil`, `tempfile`, `os.path`, `os.environ`, `contextlib.chdir`.

**TODO/zapowiedzi do domknięcia.** `08-wyjatki/with-i-contextlib.md:280` (`chdir()`) → sekcja 6; `01-instalacja/sciezki-i-utrzymanie.md` — bez zmian (dwa znaczenia „ścieżki” pozostają), ewentualnie jedno nawiązanie prozą na stronie.

**Odłożone.** `PurePath`/`PureWindowsPath` (jedno zdanie); `glob` moduł; `os.scandir`; uprawnienia, `chmod`; dowiązania symboliczne (`is_symlink()` jedno zdanie); `Path.owner()`.

**Ryzyka kolejności pojęć.** `Path.home()` i ścieżki bezwzględne w wynikach maskować; kolejność `iterdir()` niedeterministyczna — zawsze `sorted()`; nie dublować strony 4 (odczyt/zapis) — `read_text` jako skrót z odesłaniem.

**Orientacyjny rozmiar.** ok. 300–360 linii.

### 7. `csv-i-json.md` — Formaty danych: CSV i JSON

**Cel.** Czytelnik czyta i zapisuje dane tabelaryczne w CSV (w tym pliki z Excela: średnik, `utf-8-sig`) i dane zagnieżdżone w JSON, zna mapowanie typów i pułapki (klucze, krotki, `NaN`), używa `python -m json`, zapisuje i wczytuje stan programu; zna `tomllib`, ostrzeżenie o `pickle` i pakiet `compression`.

**Kolejność H2/H3.**
1. Format CSV i moduł `csv` (H3: `reader` i `writer`; H3: Argument `newline=""` w module `csv`)
2. Wiersze jako słowniki — `DictReader` i `DictWriter`
3. Pliki z Excela — średnik, cudzysłowy i `utf-8-sig`
4. Format JSON i moduł `json` (H3: `dumps()` i `loads()`; H3: Mapowanie typów; H3: `dump()` i `load()` z plikiem; H3: Błędy — `JSONDecodeError`)
5. Narzędzie `python -m json`
6. Zapis stanu programu
7. Inne formaty — `tomllib`, `pickle` i `compression` (dla dociekliwych)

**Pojęcia wprowadzane.** CSV jako tekst z separatorem; `csv.reader` zwraca listy łańcuchów (konwersja `int()`/`float()` po stronie programu); `csv.writer.writerow/writerows`; `newline=""` — pokaz bajtów `\r\r\n` bez niego (korekta wykładów pokazujących `open()` bez `encoding`); `DictReader` (`fieldnames` z nagłówka), `DictWriter(fieldnames=)`, `writeheader()`; dialekt `excel`, `delimiter=";"`, `quotechar`, `quoting=csv.QUOTE_MINIMAL` (jedno zdanie o `QUOTE_ALL`), `utf-8-sig` przy odczycie i zapisie dla Excela (`utf-8-sig` zapisuje BOM `b'\xef\xbb\xbf'`); JSON: składnia, `dumps(indent=2, ensure_ascii=False, sort_keys=True)`, `loads()`; tabela typów (dict→object, list/tuple→array, str, int/float→number, True/False→true/false, None→null i odwrotnie — krotka wraca jako lista); klucze zawsze `str` (`{1: "a"}` → `{"1": "a"}`, klucz-krotka → `TypeError`); `NaN`/`Infinity` niestandardowe; `dump()`/`load()` z `open(…, encoding="utf-8")`; `JSONDecodeError` jako odmiana `ValueError` z `lineno`/`colno`; obiekt nieserializowalny → `TypeError` i argument `default=` (np. `str`) jednym przykładem; `python -m json plik.json --indent 2`, `--sort-keys`, `--no-ensure-ascii`, potok z `Get-Content`; zapis stanu: lista zadań (słowniki) → `zadania.json` → wczytanie po restarcie (funkcje `zapisz()`/`wczytaj()` z obsługą braku pliku przez `FileNotFoundError` — 8); `tomllib.load()` na `pyproject.toml` z rozdziału 7 (tylko odczyt, od 3.11); `pickle` — ostrzeżenie prozą; `compression.zstd.compress()`/`decompress()` na bajtach z rozmiarami (od 3.14; `compression.gzip` jako nowa nazwa `gzip`).

**Zależności.** Słowniki i listy (5); `open()`, kodowanie, `newline` (strona 4); `bytes` (5); `Path` (6); wyjątki (8); `pyproject.toml` (7); `sorted(key=)` (6).

**Główne przykłady.** `oceny.csv` (blok `csv title=`) + `csv-odczyt.py` (`reader`, konwersja); `csv-zapis.py` (`writer` z `newline=""`, podgląd bajtów z i bez); `csv-slowniki.py` (`DictReader`/`DictWriter`); `excel.csv` (średnik, BOM opisany) + `excel.py` (`delimiter=";"`, `utf-8-sig`); `json-podstawy.py` (`dumps`/`loads`, `indent`, `ensure_ascii=False`); `json-typy.py` (krotka→lista, klucze→str, `TypeError` dla krotki jako klucza); `json-plik.py` (`dump`/`load`); `json-blad.py` (`JSONDecodeError` z `lineno`/`colno`); Terminal `python -m json ustawienia.json --indent 2`; `zadania.py` (zapis stanu); `tomllib-demo.py` + `toml title="pyproject.toml"`; `zstd-demo.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** Bajty CSV bez `newline=""` → `b'imi\xc4\x99,wiek\r\r\nAla,30\r\r\n…'`, z → `\r\n`; `DictReader` → `{'imię': 'Ala', 'wiek': '30'}`; `utf-8-sig` + `;` → `b'\xef\xbb\xbfimi\xc4\x99;wiek\r\n…'`; `json.dumps(dane)` z `ensure_ascii` domyślnym → `"imi\u0119"`; `ensure_ascii=False, indent=2` → polskie znaki i wcięcia; `json.loads` krotka → `list`; `json.loads("{'a': 1}")` → `JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)`; `json.dumps({(1, 2): "b"})` → `TypeError: keys must be str, int, float, bool or None, not tuple`; `json.dumps({1: "a", True: "c", None: "d"})` → `{"1": "a", "true": "c", "null": "d"}`; `json.dumps(float("nan"))` → `NaN`; `python -m json --indent 2` z domyślnym `ensure_ascii` → `"\u017c"`; `tomllib.loads(...)` → zagnieżdżony słownik; `zstd.compress(b"abc" * 100)` → 20 bajtów z 300 (sprawdzone), `decompress` odtwarza.

**Źródła repozytorium.** `Wyklad_08.txt` sl. 11 (csv — bez `encoding`), 13 (json — mapowanie typów, `open()` bez `encoding`); `Wyklad_05.txt` sl. 39 (json); `07-moduly/struktura-projektu.md` (`pyproject.toml`, TOML).

**Źródła zewnętrzne.** `csv` (nota o `newline=''`, dialekty, `DictReader`/`DictWriter`, `QUOTE_*`), `json` (tabele konwersji, `JSONDecodeError`, CLI `python -m json` 3.14 i `json.tool`), `tomllib`, `pickle` (ostrzeżenie w dokumentacji), `compression` (3.14: `zstd`, nowe nazwy modułów), RFC 8259 i RFC 4180 jako nazwy.

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich komentarzy; domyka lukę planu „csv (newline='', ';', utf-8-sig), json (ensure_ascii=False, mapowanie typów, python -m json)”. Zapowiedź w przód: zapis własnych obiektów (klas danych) do JSON — „w rozdziale o klasach danych” z `TODO`; przykład stanu programu wykorzystany w rozdziale o tkinter (bez zapowiedzi w tekście).

**Odłożone.** `csv.Sniffer`; `QUOTE_STRINGS`/`QUOTE_NOTNULL`; `object_hook`, `cls=JSONEncoder` (klasy); XML, YAML (nazwy); `zipfile`/`tarfile`; `shelve`, `sqlite3` (jedno zdanie o `sqlite3` w bibliotece standardowej).

**Ryzyka kolejności pojęć.** `default=str` w `dumps` bez wprowadzania obiektów — użyć `Decimal` z rozdziału 3 albo `Path` ze strony 6 jako obiektu nieserializowalnego; przykład stanu programu bez klas (lista słowników); polskie znaki w danych CSV wymagają `encoding="utf-8"` w każdym `open()` — spójnie.

**Orientacyjny rozmiar.** ok. 360–420 linii.

### 8. `index.md` — Wprowadzenie

Wstęp (dwa–trzy akapity): rozdział przekrojowy o wymianie danych między programem a światem — tekst sformatowany na ekranie, strumienie i terminal, pliki tekstowe i binarne, ścieżki, formaty danych; nawiązanie do rozdziału 2 (`print`/`input` — teraz w pełni), 3 (f-stringi, `str`, typy binarne w katalogu), 8 (`with open()` jako czarna skrzynka, strumień błędów, dziennik `logging`); wspólny model: strumień tekstowy (konsola, plik, pamięć) z kodowaniem między znakami a bajtami; podrozdział „Animacje w terminalu” oznaczony jako uzupełniający. Następnie `---` i `## W tym rozdziale` z siedmioma pozycjami „Tytuł — tematy”. Bez „Powiązanego laboratorium” i bez „Ściągi”. Orientacyjny rozmiar: ok. 20 linii.

## Nawigacja (dodawana wraz z powstającymi stronami, za zgodą autora)

```yaml
  - 9. Wejście, wyjście i pliki:
      - Wprowadzenie: 09-wejscie-wyjscie/index.md
      - Formatowanie tekstu: 09-wejscie-wyjscie/formatowanie.md
      - Funkcja print i strumienie: 09-wejscie-wyjscie/print-i-strumienie.md
      - Animacje w terminalu: 09-wejscie-wyjscie/animacje-w-terminalu.md
      - Pliki tekstowe: 09-wejscie-wyjscie/pliki-tekstowe.md
      - Typ bytes i pliki binarne: 09-wejscie-wyjscie/bytes-i-pliki-binarne.md
      - Ścieżki i system plików: 09-wejscie-wyjscie/pathlib.md
      - Formaty danych — CSV i JSON: 09-wejscie-wyjscie/csv-i-json.md
```

Pozycja w `docs/index.md` (dodawana wraz z `index.md` rozdziału): „9. [Wejście, wyjście i pliki](09-wejscie-wyjscie/index.md) — formatowanie tekstu, print i strumienie, animacje w terminalu, pliki tekstowe i binarne, ścieżki, CSV i JSON”.

## Kolejność tworzenia stron i odbiór

Każda strona przechodzi cykl: research w dokumentacji 3.14 → napisanie → uruchomienie wszystkich przykładów (`scripts/verify_page.py` dla skryptów i plików danych, `--stdin` dla `input()`, `--mask` dla wartości zależnych od komputera; sesje REPL osobno; przekierowania, tryb UTF-8, `EncodingWarning`, `python -m json` — ręcznie w PowerShell w katalogu próbnym poza repozytorium, także **bez** trybu UTF-8; animacje — autor) → `mkdocs build` i `mkdocs build -f mkdocs.clean.yml` → niezależna recenzja (styl, fakty, kolejność pojęć, aktualność 3.14) → naniesienie ustaleń → raport → akceptacja autora → commit. Kolejność: 1 `formatowanie.md`, 2 `print-i-strumienie.md`, 3 `animacje-w-terminalu.md`, 4 `pliki-tekstowe.md`, 5 `bytes-i-pliki-binarne.md`, 6 `pathlib.md`, 7 `csv-i-json.md`, 8 `index.md`. Wpis nav i pozycja na stronie głównej rosną wraz z powstającymi stronami. Plik danych `oceny.csv` i przykład stanu programu (`zadania.json`) mają pozostać spójne, jeśli wracają w dalszych rozdziałach.

## Zmiany w rozdziałach 1–8 (wyłącznie domknięcie zapowiedzi, zbiorczo po ukończeniu rozdziału 9)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `02-konsola/konsola-w-praktyce.md:32–34` | zdanie o podpowiedzi sygnatury w IDLE → odsyłacz do `print-i-strumienie.md#pelna-sygnatura-print`; usunięcie `<!-- TODO: screenshot … IDLE -->` | decyzja 10; `ZRZUTY.md` poz. 8 do usunięcia |
| `03-nazwy-typy/typy-proste.md:254` | „Pełny opis mini-języka formatowania zawiera dokumentacja: …” → dodatkowo odsyłacz do `formatowanie.md#mini-jezyk-specyfikacji-formatu` | odsyłacz do dokumentacji zachowany |
| `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:75` | „typy binarne …: `bytes`, `bytearray`, `memoryview`” → odsyłacz do `bytes-i-pliki-binarne.md` | tekst pozycji zachowany |
| `07-moduly/argumenty-wiersza-polecen.md:212` | „w tej książce nie odróżniamy jeszcze strumienia błędów od zwykłego wyjścia” → odsyłacz do `print-i-strumienie.md#strumienie-standardowe` | brzmienie zdania do dopasowania przy edycji |
| `08-wyjatki/obsluga-wyjatkow.md:103` | `TODO` (`open()`, `FileNotFoundError`) → odsyłacz do `pliki-tekstowe.md#funkcja-open-i-tryby-otwarcia` | |
| `08-wyjatki/with-i-contextlib.md:7` | `TODO` (pełne omówienie plików) → odsyłacz do `pliki-tekstowe.md` | |
| `08-wyjatki/with-i-contextlib.md:280` | `TODO` (`chdir()`, `redirect_stdout()`) → odsyłacze do `pathlib.md#moduly-os-shutil-i-tempfile` i `print-i-strumienie.md#argument-file-…` | slugi sprawdzić w HTML |
| `08-wyjatki/logging.md:127` | `TODO` (operator `%`) → odsyłacz do `formatowanie.md#operator` | slug do sprawdzenia |
| `08-wyjatki/logging.md:156` | `TODO` (dziennik w pliku) → odsyłacz do `pliki-tekstowe.md#dziennik-w-pliku` | |
| `08-wyjatki/logging.md:158`, `08-wyjatki/index.md:7` | `TODO` (zapowiedź rozdziału) → odsyłacz do `../09-wejscie-wyjscie/index.md` | |
| `docs/index.md`, `mkdocs.yml` | pozycja „9. Wejście, wyjście i pliki” w spisie i w nav (blok wyżej) | nav rośnie wraz z powstającymi stronami |
| `ZRZUTY.md` | usunięcie pozycji 8 (IDLE, sygnatura `print`) | decyzja 10 |

Reguła: powyższe zmiany wykonujemy jednym zbiorczym etapem po zaakceptowaniu wszystkich stron rozdziału 9, z kontrolą semantyczną każdego zdania i sprawdzeniem kotwic w zbudowanym HTML (slugi MkDocs pomijają „ł”). Nie wykonujemy innych zmian w rozdziałach 1–8 (pozostałe pozycje sekcji 6 `PLAN_ROZWOJU.md` dla rozdziałów 2–3 — sygnatura `print` jako blok w rozdziale 2, `IndentationError`, `\u`/`\U`, `isdigit` w rozdziale 3 — to osobne etapy). Komentarze `TODO` wskazujące na klasy, model danych, narzędzia typów, tkinter, wydajność i współbieżność pozostają.

## CONTENT HANDOFF (rozbieżności ze źródłami)

Książka ma rację, materiały kursu do poprawki: (a) W08 sl. 4–6, 9, 11, 13 i W05 sl. 38–39: `open()`, `read_text()`, `write_text()`, `json.dump()` bez `encoding` — książka zawsze z `encoding="utf-8"`; (b) W08 sl. 6 i notatki s. 125: ręczna podmiana `sys.stdout` → `contextlib.redirect_stdout()`; (c) W08 sl. 8: `struct.pack("if1s", …)` bez prefiksu kolejności bajtów → `"<…"`; (d) W08 sl. 12: tabela `errors=` ma przesunięte opisy (`ignore` pomija, `replace` wstawia �, `backslashreplace` wstawia `\xNN`); (e) W08 sl. 38: `tell()` w trybie tekstowym zwraca wartość nieprzezroczystą, nie liczbę znaków; (f) notatki s. 122 i lab2 sl. 5: „kod ASCII 9619” → kod Unicode U+2593; (g) notatki s. 122–123: „nie da się cofnąć kursora do poprzedniej linii” → sekwencje ANSI (`\033[F`) to umożliwiają, `os.system("cls")` jest jedną z metod; (h) notatki s. 124: `PYTHONUNBUFFERED="TRUE"` — działa dowolny niepusty łańcuch; (i) W02 sl. 17: „Python 3 używa Unicode (UTF-8) domyślnie” → `str` przechowuje kody Unicode, UTF-8 jest kodowaniem stosowanym przy zapisie; domyślne kodowanie `open()` na Windows to strona kodowa do Pythona 3.15; (j) W08 sl. 32: pipeline otwiera pliki bez `with` i `encoding`. Bez konfliktu: sygnatura `print`, `flush`/`-u`, mapowanie typów JSON, `newline=''` w csv, pathlib.

## Checklista weryfikacyjna strony (przed odbiorem)

1. Wszystkie deterministyczne przykłady uruchomione na `.venv` (3.14.7) przez `scripts/verify_page.py` (pliki danych z bloków `title=`, `--stdin`, `--mask`); przykłady ręczne (przekierowania, `-X utf8`, `EncodingWarning`, `python -m json`, animacje) wpisane z uruchomienia w PowerShell z zaznaczeniem, co zależy od strony kodowej lub terminala.
2. Brak mechanizmów z późniejszych rozdziałów: `class`, wątki, NumPy, `dataclass`; obiekt z `write()` tylko jako zapowiedź.
3. Kolejność wewnątrz rozdziału (strona 3 uzupełniająca; 4 przed 5–7; 6 przed 7); pojęcia z listy „do wprowadzenia jawnie” wprowadzone w miejscu pierwszego użycia.
4. Każde `open()`, `read_text()`, `write_text()`, `basicConfig(filename=)` z jawnym `encoding`; każde `open()` w `with`; `csv` zawsze z `newline=""`; nazwy plików przykładowych bez kolizji z biblioteką standardową; przykłady samowystarczalne (decyzja 5).
5. Strona kodowa opisana ogólnie (cp1250/cp1252), pokazy z zaznaczeniem systemu; PEP 686 jako fakt o 3.15; nowości 3.14 bez etykiety „nowości” (decyzja 3).
6. Konwencje `CLAUDE.md`: bloki z `title=` albo `.no-copy` (`csv`/`json`/`toml` z `title=`), `powershell title="Terminal"`, admonitions z polskimi tytułami, cudzysłowy „…”, terminy angielskie z „ang.”, klawisze `++…++`.
7. Wyniki zależne od komputera (ścieżki bezwzględne, `Path.home()`, daty, kolejność `iterdir()`) maskowane albo sortowane; rozmiary w bajtach deterministyczne.
8. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml`; testy warstwy interaktywnej bez regresji.
9. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji (`id` w HTML); zapowiedzi w przód prozą z `TODO` i wpisem w `PLAN_ROZWOJU.md`.
10. Struktura: do około 6–7 H2; sekcje uzupełniające oznaczone „(dla dociekliwych)”; długość według treści.

## Checklista finalnego odbioru rozdziału

1. Wszystkie osiem plików zaakceptowanych; nav i `docs/index.md` zawierają komplet pozycji; H1 = etykieta nav (index: „Wprowadzenie” / H1 „9. Wejście, wyjście i pliki”).
2. Zbiorcza redakcja: ujednolicona terminologia (strumień, kodowanie, strona kodowa, ścieżka, serializacja), spójne pliki danych, spójne maskowanie ścieżek, brak powtórzeń między stronami 2 i 4 (kodowanie strumieni a plików) oraz 4 i 6 (odczyt/zapis a `read_text`).
3. Tabela „Zmiany w rozdziałach 1–8” wykonana w całości; w `docs/08-wyjatki/` nie pozostał żaden komentarz `TODO` wskazujący na wejście i wyjście; `ZRZUTY.md` bez pozycji 8.
4. Pełny przebieg weryfikacji: harness dla wszystkich stron, sesje REPL, polecenia terminalowe, audyt kotwic, oba buildy, testy warstwy interaktywnej, `git diff --check`.
5. Ponowna kontrola faktów zależnych od wersji: grupowanie w części ułamkowej (3.14), t-stringi (3.14), `Path.copy`/`move`/`info` (3.14), `python -m json` (3.14), `compression.zstd` (3.14), `tomllib` (3.11), `walk()` (3.12), PEP 686 (3.15), `EncodingWarning` (3.10).
6. `PLAN_ROZWOJU.md`: status rozdziału 9 „ukończony” z rzeczywistą liczbą linii; zapowiedzi w przód zarejestrowane; CONTENT HANDOFF przekazany autorowi w raporcie końcowym.
7. Commit końcowy; bez integracji do `dev` bez osobnego polecenia.
