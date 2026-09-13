# Ścieżki i system plików

Dotąd otwieraliśmy pliki, podając nazwę jako łańcuch, a plik leżał w katalogu programu. Prawdziwe programy przetwarzają pliki w podkatalogach, tworzą katalogi na wyniki, wyszukują pliki według wzorca, kopiują je i usuwają. Moduł `pathlib` z biblioteki standardowej reprezentuje ścieżki jako obiekty typu `Path`, które składa się operatorem `/`, dzieli na części i o które pyta się, czy istnieją; ten sam obiekt czyta i zapisuje pliki oraz przegląda katalogi. Na koniec zestawiamy `Path` ze starszymi modułami `os` i `os.path`, z `shutil` do operacji na całych drzewach katalogów i z `tempfile` do katalogów tymczasowych.

## Ścieżki w systemie Windows i katalog roboczy

**Ścieżka** (ang. *path*) wskazuje plik lub katalog. Windows rozdziela jej części odwrotnym ukośnikiem `\` — który w łańcuchach Pythona rozpoczyna sekwencje ucieczki, stąd zalecenie z podrozdziału [Typy proste](../03-nazwy-typy/typy-proste.md#typ-str), by ścieżki zapisywać jako surowe łańcuchy `r"C:\dane\raport.txt"` — ale przyjmuje także zwykły ukośnik `/`, jak systemy uniksowe. Ścieżka **bezwzględna** (ang. *absolute*) zaczyna się od litery dysku i wskazuje miejsce jednoznacznie; ścieżka **względna** (ang. *relative*), jak `dane/raport.txt`, jest interpretowana względem **katalogu roboczego** (ang. *working directory*) — katalogu, w którym uruchomiono program, znanego z sekcji [Ścieżka wyszukiwania modułów](../07-moduly/moduly-i-import.md#sciezka-wyszukiwania-moduow) jako „katalog bieżący terminala” przy `python -m`. Wszystkie dotychczasowe `open("plik.txt")` były ścieżkami względnymi, a program działał, bo katalogiem roboczym terminala był katalog z plikiem. Katalog domowy użytkownika (`C:\Users\…`) zwraca `Path.home()`.

## Obiekt `Path`

### Składanie ścieżek operatorem `/`

`Path` tworzymy z łańcucha, a części dołączamy operatorem `/`, który działa niezależnie od tego, jaki separator obowiązuje w systemie. Wynikiem jest obiekt, którego `str()` daje ścieżkę w zapisie systemowym — z odwrotnymi ukośnikami na Windows — a `repr()` pokazuje typ `WindowsPath` (na innych systemach `PosixPath`) i ścieżkę z ukośnikami:

```python title="sciezki.py"
from pathlib import Path

p = Path("dane") / "raporty" / "styczen.txt"
print(p)
print(repr(p))
print(p.name, "|", p.stem, "|", p.suffix, "|", p.parent)
print(p.parts)
print(p.with_suffix(".csv"), "|", p.with_name("luty.txt"))
print(p.is_absolute(), Path.cwd().is_absolute())
print(Path("C:/dane/raport.txt").parent, "|", Path(r"C:\dane\raport.txt").name)
```

```{ .text .no-copy }
dane\raporty\styczen.txt
WindowsPath('dane/raporty/styczen.txt')
styczen.txt | styczen | .txt | dane\raporty
('dane', 'raporty', 'styczen.txt')
dane\raporty\styczen.csv | dane\raporty\luty.txt
False True
C:\dane | raport.txt
```

### Części ścieżki

Atrybuty `name` (ostatnia część), `stem` (nazwa bez rozszerzenia), `suffix` (rozszerzenie z kropką), `parent` (katalog nadrzędny) i `parts` (krotka wszystkich części) dają dostęp do składników ścieżki bez żadnego dzielenia łańcuchów; metody `with_suffix()` i `with_name()` tworzą nową ścieżkę z podmienioną częścią, bez odwołania do systemu plików. Metoda `resolve()` zwraca ścieżkę bezwzględną w postaci kanonicznej — rozwija odwołania `..`, skrócone nazwy i dowiązania — i jako jedyna z wymienionych sięga do systemu plików. Obiekt `Path` jest niemodyfikowalny i haszowalny — nadaje się na klucz słownika i element zbioru. Obie formy zapisu ścieżki bezwzględnej z ostatniego wiersza — z `/` i z `\` w surowym łańcuchu — dają ten sam obiekt.

### Pytania o plik — `exists()`, `is_file()`, `is_dir()` i `stat()`

Dopiero te metody sięgają do systemu plików. `exists()` mówi, czy ścieżka istnieje, `is_file()` i `is_dir()` — czym jest, a `stat()` zwraca metadane, wśród nich rozmiar w bajtach `st_size` i czas modyfikacji `st_mtime`. Atrybut `info` (od Pythona 3.14) udostępnia te same pytania, ale zapamiętuje odpowiedzi, dzięki czemu kilka pytań o tę samą ścieżkę nie odpytuje systemu wielokrotnie — istotne przy przeglądaniu tysięcy plików; zapamiętane odpowiedzi nie odświeżają się po zmianach w systemie plików, więc `info` służy do jednorazowego przeglądu:

```python title="pytania.py"
from pathlib import Path

katalog = Path("dane")
katalog.mkdir(exist_ok=True)
plik = katalog / "raport.txt"
plik.write_text("linia 1\nlinia 2\n", encoding="utf-8")

print(plik.exists(), plik.is_file(), plik.is_dir())
print(katalog.exists(), katalog.is_dir())
print((katalog / "brak.txt").exists())
print(plik.stat().st_size, "bajtów")
print(plik.info.is_file(), katalog.info.is_dir())
```

```{ .text .no-copy }
True True False
True True
False
18 bajtów
True True
```

Plik o dwóch wierszach po siedem znaków ma osiemnaście bajtów, bo `write_text()` — jak `open()` w trybie tekstowym — zapisał znaki końca wiersza jako `\r\n`. Metody `mkdir()` i `write_text()` wyjaśniamy w dalszych sekcjach; tu tworzą dane do pytań.

## Przeglądanie katalogów — `iterdir()`, `glob()`, `rglob()` i `walk()`

`iterdir()` zwraca zawartość katalogu jako obiekty `Path`, `glob(wzorzec)` — pozycje pasujące do wzorca z symbolami `*` (dowolny ciąg znaków) i `?` (jeden znak), `rglob(wzorzec)` przeszukuje także podkatalogi, a `walk()` (od Pythona 3.12) przechodzi drzewo katalog po katalogu, zwracając dla każdego krotkę: ścieżkę, listę podkatalogów i listę plików. Kolejność zwracanych pozycji zależy od systemu plików, dlatego w przykładach — i w programach, których wynik ma być powtarzalny — sortujemy wyniki:

```python title="przegladanie.py"
from pathlib import Path

for sciezka in [
    "projekt/dane/a.csv",
    "projekt/dane/b.csv",
    "projekt/dane/notatki.txt",
    "projekt/kod/main.py",
    "projekt/kod/narzedzia/pomoc.py",
]:
    p = Path(sciezka)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")

projekt = Path("projekt")
print(sorted(str(x) for x in projekt.iterdir()))
print(sorted(x.name for x in (projekt / "dane").glob("*.csv")))
print(sorted(str(x) for x in projekt.rglob("*.py")))
for katalog, podkatalogi, pliki in projekt.walk():
    print(katalog, sorted(podkatalogi), sorted(pliki))
```

```{ .text .no-copy }
['projekt\\dane', 'projekt\\kod']
['a.csv', 'b.csv']
['projekt\\kod\\main.py', 'projekt\\kod\\narzedzia\\pomoc.py']
projekt ['dane', 'kod'] []
projekt\dane [] ['a.csv', 'b.csv', 'notatki.txt']
projekt\kod ['narzedzia'] ['main.py']
projekt\kod\narzedzia [] ['pomoc.py']
```

Pętla tworząca pliki pokazuje typowy zapis `mkdir(parents=True, exist_ok=True)`: tworzy brakujące katalogi nadrzędne i nie zgłasza błędu, gdy katalog już istnieje. W listach ścieżki są wypisane przez `repr()`, stąd podwojone ukośniki; `print()` pojedynczej ścieżki, jak w pętli `walk()`, pokazuje je pojedynczo. Wzorzec `rglob("*.py")` jest skrótem dla `glob("**/*.py")`, gdzie `**` oznacza dowolną liczbę poziomów katalogów.

## Tworzenie, kopiowanie, przenoszenie i usuwanie

Do tworzenia służą `mkdir()` i `touch()` (pusty plik albo aktualizacja czasu modyfikacji), do kopiowania i przenoszenia — `copy()` i `move()` (od Pythona 3.14; obie zwracają ścieżkę docelową), do zmiany nazwy `rename()`, a do usuwania `unlink()` dla plików i `rmdir()` dla pustych katalogów. Katalog z zawartością usuwa funkcja `shutil.rmtree()`, a kopiuje w całości `shutil.copytree()`:

```python title="operacje.py"
import shutil
from pathlib import Path

baza = Path("archiwum")
shutil.rmtree(baza, ignore_errors=True)
(baza / "2025").mkdir(parents=True)
plik = baza / "2025" / "raport.txt"
plik.write_text("dane\n", encoding="utf-8")
(baza / "puste.txt").touch()

kopia = plik.copy(baza / "2025" / "raport-kopia.txt")
przeniesiony = kopia.move(baza / "raport-2025.txt")
print(sorted(str(x) for x in baza.rglob("*")))
print(kopia.exists(), przeniesiony.exists(), repr(przeniesiony.read_text(encoding="utf-8")))

przeniesiony.unlink()
(baza / "puste.txt").unlink()
(baza / "nieistniejacy.txt").unlink(missing_ok=True)
plik.unlink()
(baza / "2025").rmdir()
print(sorted(str(x) for x in baza.rglob("*")))
shutil.rmtree(baza)
print(baza.exists())
```

```{ .text .no-copy }
['archiwum\\2025', 'archiwum\\2025\\raport.txt', 'archiwum\\puste.txt', 'archiwum\\raport-2025.txt']
False True 'dane\n'
[]
False
```

Program zaczyna od `shutil.rmtree(baza, ignore_errors=True)`, by każde uruchomienie rozpoczynało się od pustego katalogu. Po skopiowaniu i przeniesieniu kopia pod starą nazwą nie istnieje, a pod nową — tak; `unlink(missing_ok=True)` nie zgłasza błędu dla brakującego pliku, w odróżnieniu od domyślnego `unlink()`, które zgłasza `FileNotFoundError`. `rmdir()` usuwa wyłącznie pusty katalog — dlatego wcześniej usunęliśmy `raport.txt` — a `shutil.rmtree()` usuwa całe drzewo bez potwierdzenia, więc ścieżkę przekazywaną do tej funkcji warto sprawdzić szczególnie uważnie. Metoda `replace()` działa jak `rename()`, ale nadpisuje istniejący cel; to ona realizuje bezpieczny zapis z podrozdziału o plikach tekstowych — zapis nowej wersji do pliku tymczasowego i podmianę oryginału jednym wywołaniem.

## Odczyt i zapis skrótami — `read_text()` i `write_text()`

Dla plików czytanych albo zapisywanych w całości `Path` ma skróty: `read_text(encoding=…)` zwraca zawartość jako łańcuch, `write_text(dane, encoding=…)` zapisuje łańcuch (tworząc plik albo opróżniając istniejący, jak tryb `w`), a `read_bytes()` i `write_bytes()` robią to samo dla bajtów. Kodowanie podajemy z tych samych powodów, co przy `open()`. Gdy plik ma być przetwarzany wierszami albo dopisywany, `Path` udostępnia metodę `open()` o tych samych argumentach, co funkcja wbudowana:

```python title="skroty.py"
from pathlib import Path

plik = Path("notatka.txt")
plik.write_text("pierwsza linia\ndruga linia\n", encoding="utf-8")
print(plik.read_text(encoding="utf-8").splitlines())
print(plik.read_bytes()[:16])

with plik.open(encoding="utf-8") as f:
    print(f.readline(), end="")
```

```{ .text .no-copy }
['pierwsza linia', 'druga linia']
b'pierwsza linia\r\n'
pierwsza linia
```

Skróty są wygodne w skryptach i przy małych plikach; dla dużych plików pozostaje iteracja po wierszach z podrozdziału o plikach tekstowych, bo `read_text()` wczytuje całość do pamięci.

## Moduły `os`, `shutil` i `tempfile`

Przed `pathlib` (dodanym w Pythonie 3.4) ścieżki były łańcuchami, a operacje na nich wykonywały funkcje modułów `os` i `os.path`; spotkamy je w starszym kodzie i w dokumentacji, a `Path` przyjmuje i zwraca zwykłe łańcuchy tam, gdzie trzeba (`str(sciezka)`, `os.fspath()`). Odpowiedniki zbiera tabela:

| `os` / `os.path` | `pathlib.Path` |
|---|---|
| `os.getcwd()` | `Path.cwd()` |
| `os.path.join(a, b)` | `Path(a) / b` |
| `os.path.basename(p)`, `os.path.dirname(p)` | `p.name`, `p.parent` |
| `os.path.splitext(p)[1]` | `p.suffix` |
| `os.path.exists(p)`, `os.path.isfile(p)`, `os.path.isdir(p)` | `p.exists()`, `p.is_file()`, `p.is_dir()` |
| `os.path.abspath(p)`, `os.path.realpath(p)` | `p.absolute()`, `p.resolve()` |
| `os.listdir(p)` | `p.iterdir()` |
| `os.makedirs(p, exist_ok=True)` | `p.mkdir(parents=True, exist_ok=True)` |
| `os.remove(p)`, `os.rmdir(p)` | `p.unlink()`, `p.rmdir()` |
| `os.rename(a, b)`, `os.replace(a, b)` | `a.rename(b)`, `a.replace(b)` |
| `shutil.copyfile(a, b)`, `shutil.move(a, b)` | `a.copy(b)`, `a.move(b)` |

Moduł `os` zawiera też to, czego `pathlib` nie obejmuje: `os.environ` — słownik zmiennych środowiskowych z rozdziału 1 (`os.environ.get("PYTHONUTF8")`), `os.name` (`"nt"` na Windows) i `os.linesep`. Moduł `shutil` operuje na całych drzewach (`copytree()`, `rmtree()`) i archiwach. Moduł `tempfile` tworzy pliki i katalogi tymczasowe w miejscu przewidzianym przez system; `TemporaryDirectory()` jest menedżerem kontekstu z rozdziału 8, który usuwa katalog wraz z zawartością po bloku `with`, a `contextlib.chdir()` — zapowiedziany tam — tymczasowo zmienia katalog roboczy:

```python title="tymczasowy.py"
import os
import tempfile
from contextlib import chdir
from pathlib import Path

with tempfile.TemporaryDirectory() as nazwa:
    katalog = Path(nazwa)
    with chdir(katalog):
        Path("proba.txt").write_text("test\n", encoding="utf-8")
        print(Path.cwd() == katalog.resolve(), sorted(p.name for p in Path().iterdir()))
    print(katalog.exists())
print(katalog.exists())
print(os.path.join("dane", "raport.txt"), os.path.exists("brak"), os.getcwd() == str(Path.cwd()))
```

```{ .text .no-copy }
True ['proba.txt']
True
False
dane\raport.txt False True
```

Wewnątrz bloku `chdir()` ścieżki względne odnoszą się do katalogu tymczasowego, po bloku katalog roboczy wraca do poprzedniego, a po wyjściu z `TemporaryDirectory()` katalog znika — to bezpieczne miejsce na eksperymenty z plikami i na dane pośrednie, których program nie powinien zostawiać po sobie. W ostatnim podrozdziale rozdziału wykorzystamy ścieżki i pliki tekstowe do pracy z dwoma formatami danych: CSV i JSON.
