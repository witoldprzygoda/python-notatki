# Pliki tekstowe

W rozdziale 8 z funkcji `open()` korzystaliśmy bez wyjaśnienia: otwierała plik do odczytu, zawsze z argumentem `encoding="utf-8"`, a instrukcja `with` go zamykała. Teraz omawiamy ją w całości: tryby otwarcia, trzy sposoby odczytu, zapis i dopisywanie, kodowanie znaków — najczęstsze źródło problemów z plikami na Windows — oraz znaki końca wiersza. Po drodze domykamy zapowiedź z rozdziału 8, czyli dziennik `logging` zapisywany do pliku, a dla dociekliwych zostawiamy poruszanie się po pliku metodami `seek()` i `tell()`.

## Funkcja `open()` i tryby otwarcia

```{ .text .no-copy }
open(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
```

Pierwszy argument to ścieżka pliku — łańcuch albo obiekt `Path` z dalszego podrozdziału; ścieżka względna jest liczona od katalogu roboczego programu. Drugi, **tryb otwarcia** (ang. *mode*), to łańcuch złożony z liter:

| Litera | Znaczenie |
|---|---|
| `r` | odczyt (domyślnie); plik musi istnieć |
| `w` | zapis; plik jest tworzony, a istniejący — opróżniany bez ostrzeżenia |
| `a` | dopisywanie (ang. *append*) na końcu; plik jest tworzony, jeśli nie istnieje |
| `x` | tworzenie z zapisem; błąd `FileExistsError`, jeśli plik istnieje |
| `+` | dodatkowo odczyt i zapis (np. `r+`) |
| `t` | tryb tekstowy (domyślnie) — program pracuje na łańcuchach `str` |
| `b` | tryb binarny — program pracuje na bajtach `bytes` (następny podrozdział) |

Argumenty `encoding`, `errors` i `newline` dotyczą wyłącznie trybu tekstowego i omawiamy je w dalszych sekcjach; `buffering`, `closefd` i `opener` w tej książce pozostają przy wartościach domyślnych. Trzy tryby zapisu różnią się zachowaniem wobec istniejącego pliku:

```python title="tryby.py"
with open("notatki.txt", "w", encoding="utf-8") as plik:
    plik.write("pierwsza notatka\n")
with open("notatki.txt", "a", encoding="utf-8") as plik:
    plik.write("druga notatka\n")
with open("notatki.txt", encoding="utf-8") as plik:
    print(plik.read(), end="")

try:
    with open("notatki.txt", "x", encoding="utf-8") as plik:
        plik.write("to się nie zapisze\n")
except FileExistsError as e:
    print("nie nadpisuję:", e)
```

```{ .text .no-copy }
pierwsza notatka
druga notatka
nie nadpisuję: [Errno 17] File exists: 'notatki.txt'
```

Tryb `w` utworzył plik, `a` dopisał drugi wiersz, a `x` odmówił, bo plik już istniał — to tryb właściwy, gdy program ma nigdy nie nadpisać istniejących danych. Typowe wyjątki przy otwieraniu należą do rodziny `OSError` z rozdziału 8: `FileNotFoundError` przy odczycie nieistniejącego pliku, `FileExistsError` w trybie `x` i `PermissionError`, gdy system odmawia dostępu — na Windows także wtedy, gdy ścieżka wskazuje katalog (systemy uniksowe zgłaszają w tym przypadku `IsADirectoryError`).

## Odczyt

Obiekt pliku otwarty do odczytu udostępnia trzy metody i możliwość iteracji. W przykładach korzystamy z pliku o czterech wierszach, z których trzeci jest pusty:

```text title="wiersze.txt"
Pierwszy wiersz
Drugi wiersz

Czwarty wiersz po pustym
```

### Metody `read()`, `readline()` i `readlines()`

`read()` zwraca całą zawartość jako jeden łańcuch (z argumentem — najwyżej podaną liczbę znaków), `readline()` zwraca następny wiersz razem z końcowym `\n` (pusty łańcuch oznacza koniec pliku), a `readlines()` zwraca listę wszystkich wierszy:

```python title="odczyt.py"
with open("wiersze.txt", encoding="utf-8") as plik:
    calosc = plik.read()
print(repr(calosc))
print(len(calosc.splitlines()), "wierszy")

with open("wiersze.txt", encoding="utf-8") as plik:
    pierwszy = plik.readline()
    drugi = plik.readline()
print(repr(pierwszy), repr(drugi))

with open("wiersze.txt", encoding="utf-8") as plik:
    lista = plik.readlines()
print(lista)
```

```{ .text .no-copy }
'Pierwszy wiersz\nDrugi wiersz\n\nCzwarty wiersz po pustym\n'
4 wierszy
'Pierwszy wiersz\n' 'Drugi wiersz\n'
['Pierwszy wiersz\n', 'Drugi wiersz\n', '\n', 'Czwarty wiersz po pustym\n']
```

Obiekt pliku pamięta pozycję: drugie `readline()` zwróciło drugi wiersz, bo pierwsze przesunęło pozycję za koniec pierwszego. Metoda `splitlines()` łańcucha dzieli tekst na wiersze bez znaków końca wiersza — w odróżnieniu od `readlines()`, która je zachowuje. Do usunięcia `\n` z pojedynczego wiersza służy `rstrip("\n")` albo `strip()`, gdy przeszkadzają też inne białe znaki.

### Iteracja po wierszach

Metody `read()` i `readlines()` wczytują do pamięci całość; `readline()` w pętli byłoby oszczędne, ale prostsza i równie oszczędna jest iteracja pętlą `for` po obiekcie pliku, znana z rozdziału 8, która pobiera wiersze pojedynczo — obiekt pliku jest iteratorem w rozumieniu rozdziału 4:

```python title="iteracja.py"
liczba_wierszy = 0
liczba_slow = 0
with open("wiersze.txt", encoding="utf-8") as plik:
    for wiersz in plik:
        liczba_wierszy += 1
        liczba_slow += len(wiersz.split())
print(liczba_wierszy, "wierszy,", liczba_slow, "słów")
```

```{ .text .no-copy }
4 wierszy, 8 słów
```

Pętla przetworzyła plik, którego rozmiar nie ma znaczenia — w pamięci jest zawsze jeden wiersz. Ten wzorzec łączy się z potokami generatorów z rozdziału 6: obiekt pliku może być źródłem, po którym kolejne etapy filtrują i przekształcają wiersze.

## Zapis i dopisywanie

### Metody `write()` i `writelines()` oraz `print(file=)`

Metoda `write()` zapisuje łańcuch dokładnie taki, jaki dostała — bez dodawania `\n` — i zwraca liczbę zapisanych znaków. `writelines()` zapisuje wszystkie łańcuchy z obiektu iterowalnego, również bez separatorów, więc znaki końca wiersza muszą być w danych. Trzecią drogą jest `print()` z argumentem `file`, z podrozdziału o funkcji `print` i strumieniach — jedyną, która dodaje `\n` i rozdziela argumenty:

```python title="zapis.py"
oceny = {"Ala": 4.5, "Ola": 5.0, "Ela": 3.5}

with open("oceny.txt", "w", encoding="utf-8") as plik:
    plik.write("imię;ocena\n")
    plik.writelines(f"{imie};{ocena}\n" for imie, ocena in oceny.items())
    print("koniec listy", file=plik)

with open("oceny.txt", encoding="utf-8") as plik:
    print(plik.read(), end="")
```

```{ .text .no-copy }
imię;ocena
Ala;4.5
Ola;5.0
Ela;3.5
koniec listy
```

Argumentem `writelines()` jest wyrażenie generatorowe z rozdziału 5 — wiersze powstają na bieżąco, bez listy pośredniej. Zapisywać można wyłącznie łańcuchy; liczbę trzeba wcześniej zamienić na tekst, co f-string robi sam.

### Tryb `x` i nadpisywanie

Tryb `w` opróżnia istniejący plik w chwili otwarcia — przed pierwszym `write()` — więc program, który otworzy plik do zapisu i zawiedzie, zostawia go pustym. Gdy plik ma być modyfikowany bezpiecznie, zapisujemy nową wersję pod tymczasową nazwą i dopiero potem zastępujemy nią oryginał; narzędzia do tego, jak `Path.replace()`, poznamy w podrozdziale o ścieżkach. Gdy plik ma być tworzony tylko raz, tryb `x` z pierwszej sekcji zamienia ciche nadpisanie w wyjątek.

## Kodowanie

Plik tekstowy jest w rzeczywistości ciągiem bajtów, a kodowanie — pojęcie z podrozdziału o strumieniach — to reguła zamiany znaków na bajty przy zapisie i bajtów na znaki przy odczycie. Obiekt pliku w trybie tekstowym wykonuje tę zamianę sam; program widzi łańcuchy `str`. Reguła musi być po obu stronach ta sama — plik zapisany w jednym kodowaniu, a odczytany w innym, daje zniekształcony tekst albo błąd.

### UTF-8 a strona kodowa Windows

Standardem jest **UTF-8**: koduje wszystkie znaki Unicode, litery ASCII jednym bajtem, polskie litery dwoma. Gdy `open()` nie dostanie argumentu `encoding`, Python 3.14 używa kodowania systemowego (zwraca je funkcja `locale.getencoding()`), które na Windows jest stroną kodową zależną od ustawień regionalnych: cp1250 w polskim Windows, cp1252 w angielskim (komputer, na którym powstała ta książka, używa cp1252). Strony kodowe kodują każdy znak jednym bajtem, ale obejmują tylko wybrane litery. Zapiszmy polski tekst w UTF-8 i odczytajmy go jako cp1250:

```python title="kodowanie.py"
tekst = "zażółć gęślą jaźń"
with open("polskie.txt", "w", encoding="utf-8") as plik:
    plik.write(tekst + "\n")

with open("polskie.txt", encoding="utf-8") as plik:
    print("utf-8: ", plik.read(), end="")
with open("polskie.txt", encoding="cp1250") as plik:
    print("cp1250:", plik.read(), end="")
print(tekst.encode("utf-8"))
print(tekst.encode("cp1250"))
print(len(tekst), len(tekst.encode("utf-8")), len(tekst.encode("cp1250")))
```

```{ .text .no-copy }
utf-8:  zażółć gęślą jaźń
cp1250: zaĹĽĂłĹ‚Ä‡ gÄ™Ĺ›lÄ… jaĹşĹ„
b'za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87 g\xc4\x99\xc5\x9bl\xc4\x85 ja\xc5\xba\xc5\x84'
b'za\xbf\xf3\xb3\xe6 g\xea\x9cl\xb9 ja\x9f\xf1'
17 26 17
```

Odczyt w złym kodowaniu nie zgłosił błędu — każdy bajt UTF-8 został zinterpretowany jako jakiś znak strony cp1250, stąd para znaków w miejscu każdej polskiej litery; odczyt w cp1252 daje inny zniekształcony ciąg, a `UnicodeDecodeError` pojawia się dopiero wtedy, gdy wśród bajtów trafi się jeden z pięciu, którym cp1252 nie przypisuje żadnego znaku — na przykład drugi bajt litery „Ł”. Metoda `str.encode()` pokazuje bajty, które powstałyby przy zapisie: siedemnaście znaków to dwadzieścia sześć bajtów w UTF-8 (dziewięć polskich liter po dwa bajty) i siedemnaście w cp1250. Wniosek dla programów jest jeden — kodowanie podajemy zawsze jawnie, a wybieramy UTF-8, chyba że plik pochodzi z programu, który wymaga innego. Interpreter potrafi przypomnieć o pominiętym argumencie: opcja `-X warn_default_encoding` włącza ostrzeżenie `EncodingWarning` przy każdym `open()` bez `encoding`:

```python title="bez-kodowania.py"
with open("notatka.txt", "w") as plik:  # celowo bez encoding
    plik.write("notatka bez kodowania\n")
```

```powershell title="Terminal"
python -X warn_default_encoding bez-kodowania.py
```

```{ .text .no-copy }
bez-kodowania.py:1: EncodingWarning: 'encoding' argument not specified
  with open("notatka.txt", "w") as plik:  # celowo bez encoding
```

### Znacznik BOM i `utf-8-sig`

Niektóre programy na Windows — Notatnik przy wyborze „UTF-8 z BOM”, Excel w formacie „CSV UTF-8” — zapisują pliki UTF-8 z **BOM** (ang. *byte order mark*): trzema bajtami `EF BB BF` na początku, odpowiadającymi znakowi Unicode U+FEFF. Odczytany kodowaniem `utf-8` znacznik staje się niewidocznym pierwszym znakiem pierwszego wiersza, przez co porównania i nagłówki przestają się zgadzać. Kodowanie `utf-8-sig` pomija BOM przy odczycie i dodaje go przy zapisie — to kodowanie właściwe dla plików wymienianych z Excelem:

```python title="bom.py"
BOM = chr(0xFEFF)

with open("z-bom.txt", "w", encoding="utf-8-sig") as plik:
    plik.write("imię;ocena\n")
with open("z-bom.txt", "rb") as plik:
    print(plik.read(12))

with open("z-bom.txt", encoding="utf-8") as plik:
    pierwszy = plik.readline().rstrip("\n")
print(len(pierwszy), pierwszy.startswith(BOM), pierwszy == "imię;ocena")

with open("z-bom.txt", encoding="utf-8-sig") as plik:
    pierwszy = plik.readline().rstrip("\n")
print(len(pierwszy), pierwszy.startswith(BOM), pierwszy == "imię;ocena")
```

```{ .text .no-copy }
b'\xef\xbb\xbfimi\xc4\x99;oce'
11 True False
10 False True
```

Odczyt binarny (tryb `rb`, następny podrozdział) pokazuje trzy bajty znacznika przed tekstem. Odczytany jako `utf-8` nagłówek ma jedenaście znaków zamiast dziesięciu i nie jest równy oczekiwanemu łańcuchowi; `utf-8-sig` usuwa problem.

### Obsługa błędów kodowania — `errors=`

Gdy bajty nie dają się zdekodować (albo znak zakodować), domyślnie zgłaszany jest wyjątek `UnicodeDecodeError` (`UnicodeEncodeError`) — obie odmiany `ValueError`. Argument `errors` zmienia to zachowanie: `"replace"` wstawia znak zastępczy — `�` przy odczycie, `?` przy zapisie — za każdy błędny bajt lub znak, `"ignore"` je pomija, `"backslashreplace"` zapisuje je sekwencjami `\x..`, a `"surrogateescape"` pozwala odczytać i zapisać z powrotem bajty w nieznanym kodowaniu bez ich utraty:

```python title="bledy-kodowania.py"
with open("polskie.txt", "w", encoding="utf-8") as plik:
    plik.write("zażółć gęślą jaźń\n")

with open("polskie.txt", encoding="ascii", errors="replace") as plik:
    print(plik.read(), end="")
with open("polskie.txt", encoding="ascii", errors="ignore") as plik:
    print(plik.read(), end="")
try:
    with open("polskie.txt", encoding="ascii") as plik:
        plik.read()
except UnicodeDecodeError as e:
    print(e)
```

```{ .text .no-copy }
za�������� g����l�� ja����
za gl ja
'ascii' codec can't decode byte 0xc5 in position 2: ordinal not in range(128)
```

Odczyt z `errors="replace"` przydaje się do wstępnego obejrzenia zawartości pliku o nieznanym kodowaniu, `"ignore"` prowadzi do cichej utraty danych i w programach użytkowych go unikamy. Komunikat wyjątku wskazuje bajt i pozycję, od której należy zacząć poszukiwanie właściwego kodowania.

### Tryb UTF-8 i Python 3.15

Zależność domyślnego kodowania od systemu usuwa **tryb UTF-8** interpretera, poznany w podrozdziale [Funkcja print i strumienie](print-i-strumienie.md#kodowanie-strumieni-konsola-a-przekierowanie): z opcją `-X utf8` (albo zmienną `PYTHONUTF8=1`) `open()` bez argumentu `encoding` używa UTF-8, podobnie jak strumienie standardowe:

```powershell title="Terminal"
python -c "import locale; print(locale.getencoding())"
python -c "with open('proba.txt', 'w') as plik: print(plik.encoding)"
python -X utf8 -c "with open('proba.txt', 'w') as plik: print(plik.encoding)"
```

```{ .text .no-copy }
cp1252
cp1252
utf-8
```

Od Pythona 3.15 tryb UTF-8 ma być domyślny ([PEP 686](https://peps.python.org/pep-0686/)), a `open()` bez `encoding` będzie oznaczać UTF-8 na każdym systemie; kodowanie systemowe można zażądać jawnie zapisem `encoding="locale"`, dostępnym od Pythona 3.10. Do tego czasu jawne `encoding="utf-8"` pozostaje najprostszym sposobem, by program działał tak samo u każdego użytkownika.

## Znaki końca wiersza — argument `newline`

Windows kończy wiersze parą znaków `\r\n`, a systemy uniksowe pojedynczym `\n`; separator systemu przechowuje `os.linesep`. Obiekt pliku tekstowego ukrywa tę różnicę: przy zapisie zamienia `\n` na separator systemu, a przy odczycie rozpoznaje wszystkie trzy warianty (`\n`, `\r\n`, `\r`) i zwraca `\n` — jest to tryb **uniwersalnych znaków końca wiersza** (ang. *universal newlines*). Argument `newline=""` wyłącza tłumaczenie w obie strony, co można sprawdzić, oglądając plik bajt po bajcie:

```python title="newline.py"
with open("wiersze-win.txt", "w", encoding="utf-8") as plik:
    plik.write("a\nb\n")
with open("wiersze-win.txt", "rb") as plik:
    print(plik.read())

with open("wiersze-unix.txt", "w", encoding="utf-8", newline="") as plik:
    plik.write("a\nb\n")
with open("wiersze-unix.txt", "rb") as plik:
    print(plik.read())

with open("wiersze-win.txt", encoding="utf-8") as plik:
    print(repr(plik.read()))
with open("wiersze-win.txt", encoding="utf-8", newline="") as plik:
    print(repr(plik.read()))
```

```{ .text .no-copy }
b'a\r\nb\r\n'
b'a\nb\n'
'a\nb\n'
'a\r\nb\r\n'
```

W zwykłej pracy z tekstem tłumaczenie jest pożądane — program pisze `\n`, a plik dostaje separator właściwy dla systemu. Argument `newline=""` jest potrzebny w jednym ważnym przypadku: przy zapisie i odczycie plików CSV modułem `csv`, który sam obsługuje znaki końca wiersza; wracamy do tego w ostatnim podrozdziale.

## Dziennik w pliku

W podrozdziale [Logowanie zamiast print](../08-wyjatki/logging.md#dziennik-w-pliku-i-dalsze-mozliwosci) zapowiedzieliśmy dziennik zapisywany do pliku. Wystarczy podać funkcji `basicConfig()` argument `filename=` — i, z omówionych wyżej powodów, `encoding="utf-8"`; wpisy są domyślnie dopisywane na końcu istniejącego pliku, jak w trybie `a`, a `filemode="w"` zaczyna plik od nowa przy każdym uruchomieniu:

```python title="dziennik-plik.py"
import logging

logging.basicConfig(
    filename="program.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

log.info("start programu")
log.warning("brak pliku ustawień, przyjmuję domyślne")
logging.shutdown()

with open("program.log", encoding="utf-8") as plik:
    print(plik.read(), end="")
```

```{ .text .no-copy }
10:15:42 INFO start programu
10:15:42 WARNING brak pliku ustawień, przyjmuję domyślne
```

Godziny zależą od chwili uruchomienia. Wywołanie `logging.shutdown()` zamyka plik dziennika przed jego odczytem; w zwykłym programie nie jest potrzebne, bo moduł zamyka plik przy zakończeniu interpretera. Dziennik w pliku przydaje się przede wszystkim w programach uruchamianych bez nadzoru — wpisy przetrwają zamknięcie okna terminala.

## Pozycja w pliku — `seek()` i `tell()` (dla dociekliwych)

Obiekt pliku przechowuje bieżącą pozycję, przesuwaną przez każdy odczyt i zapis. Metoda `tell()` ją zwraca, a `seek(pozycja)` ustawia; `seek(0)` wraca na początek, co pozwala odczytać plik ponownie bez zamykania:

```python title="seek-tell.py"
with open("wiersze.txt", encoding="utf-8") as plik:
    print(plik.tell())
    print(repr(plik.readline()))
    print(plik.tell())
    plik.seek(0)
    print(repr(plik.readline()))
```

```{ .text .no-copy }
0
'Pierwszy wiersz\n'
17
'Pierwszy wiersz\n'
```

W trybie tekstowym wartość z `tell()` jest nieprzezroczysta: liczy bajty w pliku (tu siedemnaście, bo plik zapisano ze znakami `\r\n`; zapisany z samym `\n` dałby szesnaście), a przy kodowaniach wielobajtowych nie odpowiada liczbie znaków, więc nie należy jej używać do arytmetyki — jedynie przekazywać z powrotem do `seek()`. Swobodne poruszanie się po pliku ma sens w trybie binarnym, gdzie pozycja jest numerem bajtu; przykłady znajdziemy w następnym podrozdziale.
