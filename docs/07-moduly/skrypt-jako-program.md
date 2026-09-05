# Skrypt jako program

W poprzednim podrozdziale ustaliliśmy, że kod modułu wykonuje się podczas importu — cały, od góry do dołu. Skrypty pisane dotąd w książce nie ograniczały się jednak do definiowania funkcji: wypisywały wyniki, wczytywały dane, uruchamiały obliczenia. Ten podrozdział pokazuje, jak jeden plik może być zarazem modułem, z którego inne programy importują funkcje, i programem uruchamianym z terminala — bez wykonywania podczas każdego importu **części programowej**, czyli kodu mającego sens tylko przy bezpośrednim uruchomieniu. Pliki z tego podrozdziału, jak poprzednio, leżą w katalogu `projekt`, w którym otwieramy terminal.

## Ten sam plik jako moduł i jako program

Wróćmy do modułu `narzedzia.py` w uproszczonej postaci, bez stałej `SEPARATOR`, i dopiszmy na jego końcu wiersz, który pokazuje działanie funkcji na przykładzie — tak jak kończyły się dotychczasowe skrypty:

```python title="narzedzia.py"
"""Udostępnia proste narzędzia do pracy z tekstem."""


def policz_slowa(tekst):
    """Zwraca liczbę słów w tekście."""
    return len(tekst.split())


print(policz_slowa("Ala ma kota"))
```

```{ .text .no-copy }
3
```

Uruchomiony bezpośrednio poleceniem `python narzedzia.py`, plik zachowuje się jak każdy skrypt: definiuje funkcję i wypisuje `3`. Problem pojawia się, gdy z tej funkcji ma skorzystać inny program:

```python title="raport.py"
import narzedzia

print(narzedzia.policz_slowa("Litwo, ojczyzno moja"))
```

```{ .text .no-copy }
3
3
```

Pierwszy wiersz wyniku nie pochodzi z pliku `raport.py`. Wypisał go wiersz demonstracyjny z `narzedzia.py`, wykonany podczas importu — dokładnie tak, jak opisuje sekcja [Wykonywanie modułu podczas importu](moduly-i-import.md#wykonywanie-moduu-podczas-importu). Dla programu importującego moduł ten wynik jest zbędny; potrzebna jest tylko funkcja. Wiersz demonstracyjny powinien więc wykonywać się wyłącznie wtedy, gdy plik uruchomiono bezpośrednio, a nie wtedy, gdy został zaimportowany. Żeby to rozróżnić, potrzebujemy informacji, w jakiej roli plik jest właśnie wykonywany.

## Atrybut `__name__` i nazwa `"__main__"`

Tej informacji dostarcza atrybut `__name__`. W poprzednim podrozdziale odczytywaliśmy go z zewnątrz, jako `narzedzia.__name__`; wewnątrz modułu ta sama wartość jest dostępna jako zwykła nazwa globalna `__name__`, bo atrybuty modułu i jego nazwy globalne to jedna przestrzeń nazw (sekcja [Przestrzeń nazw modułu](moduly-i-import.md#przestrzen-nazw-moduu)). Sprawdźmy, co widzi moduł w obu rolach. Plik uruchomiony poleceniem `python nazwa.py` wypisuje:

```python title="nazwa.py"
print("wartość __name__:", __name__)
```

```{ .text .no-copy }
wartość __name__: __main__
```

Ten sam plik zaimportowany z innego pliku, uruchomionego poleceniem `python wczytaj.py`, widzi już inną wartość:

```python title="wczytaj.py"
import nazwa

print("nazwa.__name__:", nazwa.__name__)
print("w wczytaj.py:", __name__)
```

```{ .text .no-copy }
wartość __name__: nazwa
nazwa.__name__: nazwa
w wczytaj.py: __main__
```

Plik uruchomiony bezpośrednio otrzymuje nazwę `__main__`; ten sam plik zaimportowany nosi nazwę `nazwa`, czyli nazwę modułu. Reguła jest ogólna: interpreter przy starcie tworzy moduł o nazwie `__main__` — jest w `sys.modules` pod tym kluczem — i w jego przestrzeni nazw wykonuje kod, który otrzymał do uruchomienia: plik podany w poleceniu, kod po opcji `-c` albo instrukcje wpisywane w konsoli. Taki moduł nazywamy **modułem głównym** (ang. *main module*); jest nim zawsze moduł, od którego rozpoczyna się wykonywanie programu, także w konsoli interaktywnej:

```{ .python .no-copy }
>>> __name__
'__main__'
>>> type(__name__)
<class 'str'>
```

`"__main__"` to zwykły łańcuch znaków przypisany nazwie `__name__` modułu głównego — nie istnieje żadna specjalna funkcja ani słowo kluczowe o tej nazwie. Podwójne podkreślenia oznaczają nazwę należącą do mechanizmów języka, jak `__doc__` i `__file__` z poprzedniego podrozdziału; wartość `__name__` przypisuje interpreter w chwili tworzenia obiektu modułu.

Ta reguła wyjaśnia dwa zapisy z rozdziału 6, które wtedy pozostawiliśmy bez pełnego objaśnienia. Funkcja `help()` opisywała funkcję zdefiniowaną w uruchomionym skrypcie jako „in module `__main__`” (sekcja [Docstring i funkcja help()](../06-funkcje/definiowanie-funkcji.md#docstring-i-funkcja-help)) — skrypt był modułem głównym, więc tak nazywa się moduł, w którym funkcja powstała. W komunikatach `TypeError` z sekcji [Rozpakowanie argumentów w wywołaniu](../06-funkcje/argumenty-i-parametry.md#rozpakowanie-argumentow-w-wywoaniu) nazwę funkcji poprzedzał z tego samego powodu przedrostek `__main__.`:

```python title="przedstaw.py"
def przedstaw(imie, wiek):
    """Wypisuje przedstawienie osoby."""
    print(f"{imie}, {wiek} lat")


przedstaw(**[1, 2])
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "przedstaw.py", line 6, in <module>
    przedstaw(**[1, 2])
    ~~~~~~~~~^^^^^^^^^^
TypeError: __main__.przedstaw() argument after ** must be a mapping, not list
```

Przedrostek to nazwa modułu, w którym funkcja została zdefiniowana. Ta sama funkcja umieszczona w module `powitania` i wywołana z innego pliku zgłasza błąd z przedrostkiem `powitania.`:

```python title="powitania.py"
"""Udostępnia funkcje powitalne."""


def przedstaw(imie, wiek):
    """Wypisuje przedstawienie osoby."""
    print(f"{imie}, {wiek} lat")
```

```python title="uzyj.py"
import powitania

powitania.przedstaw(**[1, 2])
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "uzyj.py", line 3, in <module>
    powitania.przedstaw(**[1, 2])
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
TypeError: powitania.przedstaw() argument after ** must be a mapping, not list
```

Przy okazji nazwijmy trzeci zapis, obecny w śladach wywołań od rozdziału 5: ramka `<module>` oznacza kod wykonywany na poziomie modułu, poza wszelką funkcją — w każdym module, nie tylko głównym.

## Warunek `if __name__ == "__main__"`

Skoro moduł potrafi sprawdzić, w jakiej roli jest wykonywany, wiersz demonstracyjny wystarczy objąć zwykłą instrukcją warunkową z rozdziału [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md), porównującą wartość nazwy `__name__` z łańcuchem `"__main__"`:

```python title="narzedzia.py"
"""Udostępnia proste narzędzia do pracy z tekstem."""


def policz_slowa(tekst):
    """Zwraca liczbę słów w tekście."""
    return len(tekst.split())


if __name__ == "__main__":
    print(policz_slowa("Ala ma kota"))
```

Bezpośrednie uruchomienie nadal wykonuje część programową, bo w module głównym warunek jest prawdziwy:

```powershell title="Terminal"
python narzedzia.py
```

```{ .text .no-copy }
3
```

Import udostępnia funkcję, ale części programowej już nie uruchamia — w zaimportowanym module `__name__` ma wartość `"narzedzia"`, więc warunek jest fałszywy i blok zostaje pominięty:

```powershell title="Terminal"
python raport.py
```

```{ .text .no-copy }
3
```

Konstrukcję tę nazywamy **warunkiem uruchomienia modułu** (zwyczajowo ang. *main guard*). Nie jest to dyrektywa ani szczególna składnia: interpreter wykonuje kod modułu od góry do dołu, dochodzi do zwykłej instrukcji `if`, porównuje dwa łańcuchy i wykonuje blok albo go pomija. Działa, bo o wartości `__name__` decyduje sposób uruchomienia pliku, a nie jego treść. Do bloku warunku trafia wszystko, co ma sens tylko dla programu: demonstracje, wypisywanie wyników, wczytywanie danych od użytkownika. Definicje funkcji i stałych pozostają na zewnątrz, bo z nich właśnie korzystają importujące programy.

## Konwencja `main()`

Gdy część programowa rozrasta się do kilkunastu wierszy, blok warunku staje się nieczytelny, a wszystkie utworzone w nim nazwy trafiają do globalnej przestrzeni modułu. Przyjętym rozwiązaniem jest umieszczenie tej części w osobnej funkcji, zwyczajowo nazywanej `main()`, i wywołanie jej w bloku warunku uruchomienia modułu:

```python title="narzedzia.py"
"""Udostępnia proste narzędzia do pracy z tekstem."""


def policz_slowa(tekst):
    """Zwraca liczbę słów w tekście."""
    return len(tekst.split())


def main():
    """Uruchamia demonstrację modułu."""
    zdanie = "Ala ma kota"
    print(zdanie, "->", policz_slowa(zdanie))


if __name__ == "__main__":
    main()
```

```{ .text .no-copy }
Ala ma kota -> 3
```

Nazwa `main` nie jest w Pythonie wyróżniona — język nie wymaga takiej funkcji ani nie wywołuje jej samoczynnie, a program działałby tak samo pod nazwą `uruchom()`. Jest to konwencja, która porządkuje plik na trzy sposoby. Po pierwsze, oddziela definicje (funkcje, stałe) od działania programu, skupionego w jednym miejscu na końcu pliku. Po drugie, ogranicza liczbę nazw i operacji wykonywanych bezpośrednio na poziomie modułu: nazwa `zdanie` jest teraz lokalna w `main()`, a nie globalna w module, zgodnie z modelem LEGB z podrozdziału [Zasięg nazw i domknięcia](../06-funkcje/zasieg-nazw-i-domkniecia.md#nazwy-lokalne). Po trzecie, ułatwia ponowne wykorzystanie: program importujący moduł może wywołać część programową świadomie, kiedy chce, bo `main()` jest zwykłą funkcją modułu:

```{ .python .no-copy }
>>> import narzedzia
>>> narzedzia.policz_slowa("Litwo, ojczyzno moja")
3
>>> narzedzia.main()
Ala ma kota -> 3
```

Taki układ — funkcje u góry, `main()` na dole, warunek uruchomienia modułu na końcu — dokumentacja Pythona przedstawia jako idiomatyczny kształt skryptu uruchamianego jako program (udokumentowany przykład ma jeszcze jeden element, do którego wracamy w następnym podrozdziale). Od tego podrozdziału będą go miały wszystkie programy w książce przeznaczone zarazem do importu; krótkie skrypty ćwiczebne, które nie są przeznaczone do importowania, mogą pozostać przy prostszej postaci.

## Uruchamianie przez `python -m`

Poprawnie zbudowany moduł można uruchomić jeszcze inaczej. Opcję `-m`, spotkaną przy `python -m pip` w podrozdziale [Pip — zarządzanie pakietami](../01-instalacja/pip.md), przy `python -m venv` w podrozdziale [Wirtualne środowisko venv](../01-instalacja/venv.md) oraz przy `python -m calendar` w rozdziale [2. Konsola](../02-konsola/pierwszy-skrypt.md#python-bez-wchodzenia-do-konsoli-opcje-c-m-oraz-i), można zastosować także do własnego modułu:

```powershell title="Terminal"
python -m narzedzia
```

```{ .text .no-copy }
Ala ma kota -> 3
```

Wynik jest ten sam co dla `python narzedzia.py`, ale model działania jest inny. Polecenie `python narzedzia.py` wskazuje **plik**: interpreter otwiera go i wykonuje jako moduł główny. Polecenie `python -m narzedzia` podaje **nazwę modułu**: interpreter prosi system importu o odnalezienie modułu tak, jak robiłaby to instrukcja `import narzedzia`, a następnie wykonuje go jako moduł główny — również z `__name__` równym `"__main__"`, więc warunek uruchomienia modułu działa bez zmian. Odnajdywanie odbywa się według listy `sys.path` z sekcji [Ścieżka wyszukiwania modułów](moduly-i-import.md#sciezka-wyszukiwania-moduow); przy `-m` jej pierwszym elementem jest katalog bieżący terminala. Różnicę widać po uruchomieniu skryptu `sciezka.py` z poprzedniego podrozdziału z katalogu nadrzędnego:

```powershell title="Terminal"
cd ..
python projekt\sciezka.py
python -m sciezka
```

```{ .text .no-copy }
'C:\\...\\projekt'
C:\...\python.exe: No module named sciezka
```

Ścieżka do pliku działa z dowolnego miejsca, bo wskazuje plik wprost; ponieważ interpreter wstawia przy tym katalog skryptu na początek `sys.path`, działają też importy modułów leżących obok niego, jak w przykładzie z `program.py` z poprzedniego podrozdziału. Nazwa modułu wymaga natomiast, by moduł był osiągalny z katalogu bieżącego albo z pozostałych pozycji listy. Dlatego moduły biblioteki standardowej zapisane w plikach `.py`, jak `calendar`, uruchamiają się przez `-m` z każdego katalogu (o ile nie leży w nim własny plik o tej samej nazwie — pułapka z poprzedniego podrozdziału dotyczy także `-m`), a moduł własny, dopóki nie zostanie zainstalowany w środowisku wirtualnym, tylko z katalogu, w którym leży:

```powershell title="Terminal"
python -m calendar 2026 9
```

```{ .text .no-copy }
   September 2026
Mo Tu We Th Fr Sa Su
    1  2  3  4  5  6
 7  8  9 10 11 12 13
14 15 16 17 18 19 20
21 22 23 24 25 26 27
28 29 30
```

Komunikat `No module named sciezka` jest krótszy niż `ModuleNotFoundError` z poprzedniego podrozdziału i nie ma śladu wywołań, bo zgłasza go mechanizm uruchamiający interpretera, zanim jakikolwiek kod modułu zostanie wykonany; jego brzmienie jest szczegółem CPythona. Uboczna różnica obu sposobów uruchamiania: moduł uruchomiony przez `-m` przechodzi przez system importu, więc CPython zapisuje jego skompilowaną postać w `__pycache__`, czego przy `python narzedzia.py` nie robi — szczegół implementacji opisany w nocie poprzedniego podrozdziału. Właściwość odnajdywania po nazwie zadecyduje o sposobie uruchamiania modułów zgrupowanych w pakiety, do których wracamy dwa podrozdziały dalej.

Po opcji `-m` podajemy nazwę modułu, nie nazwę pliku. Zapis z rozszerzeniem jest błędem, bo kropka w nazwie oznacza dla systemu importu granicę między modułem nadrzędnym a podrzędnym. Wracamy do katalogu `projekt` i sprawdzamy:

```powershell title="Terminal"
cd projekt
python -m narzedzia.py
```

```{ .text .no-copy }
C:\...\python.exe: Error while finding module specification for 'narzedzia.py' (ModuleNotFoundError: __path__ attribute not found on 'narzedzia' while trying to find 'narzedzia.py'). Try using 'narzedzia' instead of 'narzedzia.py' as the module name.
```

Interpreter szukał modułu `py` wewnątrz modułu `narzedzia` (importując przy tym sam moduł `narzedzia` — dzięki warunkowi uruchomienia modułu bez skutków ubocznych) i w ostatnim zdaniu podpowiada poprawną formę. Brzmienie komunikatu, jak poprzedniego, może się zmieniać między wersjami CPythona; niezmienna jest zasada z jego ostatniego zdania: po `-m` podajemy nazwę modułu bez rozszerzenia.

Plik zorganizowany w ten sposób jest już programem: ma wydzieloną część programową, a jego funkcje można importować bez skutków ubocznych. Brakuje mu tylko jednego — sposobu przyjmowania danych z wiersza poleceń zamiast wartości wpisanych na stałe w `main()`. Tym zajmuje się następny podrozdział.
