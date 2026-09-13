# Typ bytes i pliki binarne

Katalog typów z podrozdziału [Nazwy i słowa kluczowe](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#klasyfikacja-typow) wymieniał typy binarne — `bytes`, `bytearray` i `memoryview` — których dotąd nie używaliśmy. Poprzedni podrozdział pokazał, że plik tekstowy jest w rzeczywistości ciągiem bajtów, a kodowanie zamienia znaki na bajty i z powrotem. Ten podrozdział dotyczy samych bajtów: plików otwieranych w trybie binarnym — obrazów, archiwów, plików z danymi o ustalonym układzie — oraz, dla dociekliwych, modułu `struct` i plików w pamięci.

## Znaki a bajty — `encode()` i `decode()`

Łańcuch `str` jest ciągiem **znaków** (ang. *character*) — kodów Unicode, które odczytuje funkcja `ord()` z rozdziału 3 — i nie ma z góry określonej postaci w pamięci ani na dysku. Obiekt `bytes` jest ciągiem **bajtów** (ang. *byte*): liczb całkowitych od 0 do 255. Między jednym a drugim przechodzi się przez kodowanie: metoda `str.encode()` zwraca bajty, `bytes.decode()` odtwarza tekst. W UTF-8 litery ASCII zajmują jeden bajt, polskie litery — dwa, dlatego długości obu obiektów się różnią:

```python title="znaki-bajty.py"
tekst = "zażółć"
bajty = tekst.encode("utf-8")

print(tekst, len(tekst))
print(bajty, len(bajty))
print(bajty[0], bajty[:2], type(bajty[0]).__name__)
print(bajty.decode("utf-8"))
print(list(bajty[:4]))
print(tekst.encode("cp1250"), len(tekst.encode("cp1250")))
try:
    tekst.encode("ascii")
except UnicodeEncodeError as e:
    print(e)
```

```{ .text .no-copy }
zażółć 6
b'za\xc5\xbc\xc3\xb3\xc5\x82\xc4\x87' 10
122 b'za' int
zażółć
[122, 97, 197, 188]
b'za\xbf\xf3\xb3\xe6' 6
'ascii' codec can't encode characters in position 2-5: ordinal not in range(128)
```

Reprezentacja obiektu `bytes` zaczyna się od przedrostka `b`; bajty odpowiadające drukowalnym znakom ASCII są pokazywane jako te znaki, pozostałe jako `\x` i dwie cyfry szesnastkowe. Indeks daje liczbę całkowitą, wycinek — obiekt `bytes`. Ten sam tekst ma w cp1250 sześć bajtów, a w ASCII nie da się go zapisać — kodowanie obejmuje tylko 128 znaków. W trybie tekstowym obiekt pliku wykonuje `encode()` i `decode()` sam; w tym podrozdziale wykonujemy je jawnie albo pomijamy, pracując na bajtach bezpośrednio.

## Typy `bytes`, `bytearray` i `memoryview`

Obiekt `bytes` tworzy literał `b"..."` (dopuszcza wyłącznie znaki ASCII i sekwencje ucieczki), wywołanie `bytes()` z listą liczb albo z liczbą (tyle bajtów zerowych) oraz metoda `bytes.fromhex()`; metoda `hex()` działa w drugą stronę. `bytes` jest niemodyfikowalny jak `str`; jego modyfikowalnym odpowiednikiem jest `bytearray`, obsługujący przypisanie do indeksu i `append()`. `memoryview` daje dostęp do bajtów innego obiektu bez kopiowania — przydatny przy dużych danych, gdy wycinek `bytes` tworzyłby kopię. Liczby całkowite zamienia na bajty metoda `int.to_bytes()`, a odtwarza `int.from_bytes()`; obie przyjmują **kolejność bajtów** (ang. *byte order*) — `"big"` od najbardziej znaczącego (domyślnie), `"little"` od najmniej znaczącego, jak w procesorach x86 — którą w przykładach podajemy jawnie:

```python title="typy-binarne.py"
sygnatura = bytes([0x89, 0x50, 0x4E, 0x47])
print(sygnatura, b"PNG", bytes(3))
print(bytes.fromhex("616263"), b"abc".hex())

bufor = bytearray(b"abc")
bufor[0] = 65
bufor.append(0x21)
print(bufor, bytes(bufor))

widok = memoryview(b"abcdef")
print(widok[2:4].tobytes(), len(widok))
print(int.from_bytes(b"\x00\x10", "big"), (255).to_bytes(2, "big"), (255).to_bytes(2, "little"))
```

```{ .text .no-copy }
b'\x89PNG' b'PNG' b'\x00\x00\x00'
b'abc' 616263
bytearray(b'Abc!') b'Abc!'
b'cd' 6
16 b'\x00\xff' b'\xff\x00'
```

Wszystkie trzy typy obsługują operacje sekwencji z rozdziału 5 — indeksowanie, wycinki, `len()`, `in`, iterację po liczbach — a `bytes` i `bytearray` także metody znane z `str`, jak `startswith()`, `split()`, `strip()` i `join()`, o ile ich argumenty są bajtami.

## Pliki binarne — tryby `rb` i `wb`

Litera `b` w trybie otwarcia zmienia typ danych, którymi operuje obiekt pliku: `read()` zwraca `bytes`, `write()` przyjmuje `bytes` lub `bytearray`, argument `encoding` jest niedozwolony, a znaki końca wiersza nie są tłumaczone — bajt `0x0A` pozostaje bajtem `0x0A`. W trybie binarnym otwieramy wszystko, co nie jest tekstem, oraz tekst, którego bajty chcemy obejrzeć — jak przy znaczniku BOM w poprzednim podrozdziale.

### Nagłówek pliku

Wiele formatów zaczyna się od stałej sekwencji bajtów — **sygnatury** (ang. *file signature*), po której program rozpoznaje format niezależnie od rozszerzenia: plik PNG zaczyna się od ośmiu bajtów `89 50 4E 47 0D 0A 1A 0A`, PDF od `%PDF`, archiwum ZIP od `PK`. Program poniżej tworzy plik z sygnaturą PNG (bez reszty obrazu — wystarczy do demonstracji) i plik tekstowy, po czym rozpoznaje oba po pierwszych bajtach:

```python title="naglowek.py"
SYGNATURA_PNG = b"\x89PNG\r\n\x1a\n"

with open("obrazek.png", "wb") as plik:
    plik.write(SYGNATURA_PNG)
    plik.write(bytes(16))
with open("tekst.txt", "w", encoding="utf-8") as plik:
    plik.write("to nie jest obrazek\n")


def rodzaj_pliku(sciezka):
    """Zwraca opis rodzaju pliku na podstawie jego pierwszych bajtów."""
    with open(sciezka, "rb") as plik:
        poczatek = plik.read(8)
    if poczatek.startswith(SYGNATURA_PNG):
        return "obraz PNG"
    if poczatek.startswith(b"%PDF"):
        return "dokument PDF"
    return "nieznany"


for nazwa in ["obrazek.png", "tekst.txt"]:
    print(nazwa, "->", rodzaj_pliku(nazwa))
```

```{ .text .no-copy }
obrazek.png -> obraz PNG
tekst.txt -> nieznany
```

Sygnatura PNG zawiera celowo znaki `\r\n` i `\n`: program, który otworzyłby plik w trybie tekstowym i przetłumaczył znaki końca wiersza, uszkodziłby ją — to jeden z powodów, dla których obrazów nie wolno otwierać jako tekstu. Funkcję można rozszerzyć o kolejne sygnatury z dokumentacji formatów; ten sam mechanizm stosują systemy operacyjne i narzędzia rozpoznające typ pliku.

### Kopiowanie w blokach

Pliku binarnego nie czytamy wierszami, bo nie ma w nim wierszy; czytamy go **blokami** (ang. *chunk*) o ustalonym rozmiarze, aż `read()` zwróci pusty obiekt `bytes`. Operator `:=` z podrozdziału [Wyrażenia warunkowe](../04-sterowanie/wyrazenia-warunkowe.md#operator-przypisania-w-wyrazeniu) pozwala zapisać to w jednej pętli:

```python title="kopiowanie.py"
import shutil

with open("duzy.bin", "wb") as plik:
    for numer in range(1000):
        plik.write(numer.to_bytes(4, "little"))

ROZMIAR_BLOKU = 1024
przeczytano = 0
with open("duzy.bin", "rb") as zrodlo, open("kopia.bin", "wb") as cel:
    while blok := zrodlo.read(ROZMIAR_BLOKU):
        cel.write(blok)
        przeczytano += len(blok)
print(przeczytano, "bajtów w blokach po", ROZMIAR_BLOKU)

shutil.copyfile("duzy.bin", "kopia2.bin")
with open("kopia.bin", "rb") as pierwsza, open("kopia2.bin", "rb") as druga:
    print(pierwsza.read() == druga.read())
```

```{ .text .no-copy }
4000 bajtów w blokach po 1024
True
```

Plik źródłowy ma cztery tysiące bajtów (tysiąc liczb po cztery bajty), więc pętla wykonała trzy pełne bloki i czwarty, krótszy; w pamięci był zawsze najwyżej jeden blok. Do samego kopiowania nie trzeba pisać pętli — funkcja `shutil.copyfile()` z modułu `shutil`, do którego wracamy w następnym podrozdziale, robi to samo — ale ten sam schemat służy do liczenia sum kontrolnych, wysyłania plików przez sieć czy przetwarzania danych większych od pamięci.

## Moduł `struct` (dla dociekliwych)

Pliki binarne o ustalonym układzie — rekordy z liczbami różnych rozmiarów — obsługuje moduł `struct`: `pack()` zamienia wartości na bajty według **łańcucha formatu**, `unpack()` odtwarza wartości, a `calcsize()` podaje rozmiar rekordu. Litery formatu oznaczają typy (`h` — liczba 16-bitowa ze znakiem, `H` — bez znaku, `i` — 32-bitowa ze znakiem, `d` — `float` 64-bitowy, `5s` — pięć bajtów), a pierwszy znak — kolejność bajtów: `<` to kolejność „od najmniej znaczącego”, stosowana w większości formatów plików. Prefiks podajemy zawsze, bo bez niego `struct` używa kolejności i wyrównania procesora, na którym program działa, i plik przestaje być przenośny:

```python title="struct-demo.py"
import struct

FORMAT = "<hHi"
dane = struct.pack(FORMAT, -1, 65535, 100000)
print(dane, len(dane), struct.calcsize(FORMAT))
print(struct.unpack(FORMAT, dane))

with open("rekord.bin", "wb") as plik:
    plik.write(struct.pack("<i5s", 42, "Ala".encode("utf-8")))
with open("rekord.bin", "rb") as plik:
    numer, imie = struct.unpack("<i5s", plik.read())
print(numer, imie, imie.rstrip(b"\x00").decode("utf-8"))
```

```{ .text .no-copy }
b'\xff\xff\xff\xff\xa0\x86\x01\x00' 8 8
(-1, 65535, 100000)
42 b'Ala\x00\x00' Ala
```

Liczba `-1` w dwóch bajtach ze znakiem to `ff ff`, `65535` bez znaku — również `ff ff`, a `100000` w czterech bajtach od najmniej znaczącego — `a0 86 01 00`. Pole tekstowe `5s` jest dopełniane bajtami zerowymi, które po odczycie usuwamy metodą `rstrip()`. Formaty plików w praktyce opisuje się właśnie takimi rekordami; ich czytanie w Pythonie to `struct.unpack()` na kolejnych fragmentach pliku.

## Pliki w pamięci — `io.StringIO` i `io.BytesIO` (dla dociekliwych)

Obiekt pliku jest interfejsem, a niekoniecznie plikiem na dysku. Moduł `io` dostarcza `StringIO` i `BytesIO` — obiekty zachowujące się jak plik tekstowy i binarny, lecz przechowujące dane w pamięci. `StringIO` przyjmuje `print(file=)` i `write()`, a zgromadzony tekst zwraca metodą `getvalue()`; w połączeniu z `redirect_stdout()` z drugiego podrozdziału przechwytuje wyjście funkcji, na przykład w teście sprawdzającym, co program wypisał:

```python title="w-pamieci.py"
import io
from contextlib import redirect_stdout

bufor = io.StringIO()
print("pierwszy wiersz", file=bufor)
print("drugi wiersz", file=bufor)
print(repr(bufor.getvalue()))

with redirect_stdout(io.StringIO()) as przechwycone:
    print("tekst przechwycony")
print("długość:", len(przechwycone.getvalue()))

dane = io.BytesIO(b"\x89PNG\r\n\x1a\n")
print(dane.read(4))
```

```{ .text .no-copy }
'pierwszy wiersz\ndrugi wiersz\n'
długość: 19
b'\x89PNG'
```

Menedżer `redirect_stdout()` zwraca z `__enter__()` przekazany obiekt, więc `as przechwycone` daje dostęp do bufora po bloku. `BytesIO` pełni tę samą rolę dla bajtów — pozwala na przykład przekazać dane z pamięci funkcji, która oczekuje pliku binarnego, jak funkcja `rodzaj_pliku()` po niewielkiej zmianie. Mając bajty, tekst i pliki, potrzebujemy jeszcze sprawnego poruszania się po katalogach — temat następnego podrozdziału.
