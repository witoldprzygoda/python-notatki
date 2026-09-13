# Formaty danych — CSV i JSON

Plik tekstowy z dowolnym układem wierszy trzeba za każdym razem dzielić samodzielnie metodami `split()` i `strip()`. Dwa formaty tekstowe rozwiązują ten problem w sposób jednolity i są rozumiane przez niemal każde narzędzie: **CSV** (ang. *comma-separated values*) dla danych tabelarycznych — arkusze kalkulacyjne, eksporty z baz danych — oraz **JSON** (ang. *JavaScript Object Notation*) dla danych zagnieżdżonych — ustawienia, wymiana danych z aplikacjami internetowymi. Biblioteka standardowa obsługuje oba modułami `csv` i `json`; poznajemy je wraz z pułapkami, które w praktyce sprawiają najwięcej problemów: znakami końca wiersza w CSV, plikami z Excela i mapowaniem typów w JSON. Na koniec zapisujemy stan programu między uruchomieniami oraz, dla dociekliwych, omawiamy `tomllib`, `pickle` i pakiet `compression`.

## Format CSV i moduł `csv`

Plik CSV to tekst, w którym każdy wiersz jest rekordem, a pola rozdziela przecinek; pierwszy wiersz zwykle zawiera nazwy kolumn. Wartości są zawsze tekstem — o tym, że `4.5` jest liczbą, wie program, nie plik:

```csv title="oceny.csv"
imię,przedmiot,ocena
Ala,matematyka,4.5
Ala,fizyka,5.0
Ola,matematyka,3.5
```

### `reader` i `writer`

Funkcja `csv.reader()` opakowuje otwarty plik i zwraca iterator, który dla każdego wiersza daje listę pól — już bez znaków końca wiersza i z obsługą pól ujętych w cudzysłowy, zawierających przecinki. Nagłówek pobieramy funkcją `next()` z rozdziału 4, a liczby konwertujemy sami:

```python title="csv-odczyt.py"
import csv

with open("oceny.csv", encoding="utf-8", newline="") as plik:
    czytnik = csv.reader(plik)
    naglowek = next(czytnik)
    print(naglowek)
    suma = 0
    liczba = 0
    for imie, przedmiot, ocena in czytnik:
        print(imie, przedmiot, float(ocena))
        suma += float(ocena)
        liczba += 1
print(f"średnia: {suma / liczba:.2f}")
```

```{ .text .no-copy }
['imię', 'przedmiot', 'ocena']
Ala matematyka 4.5
Ala fizyka 5.0
Ola matematyka 3.5
średnia: 4.33
```

`csv.writer()` działa odwrotnie: metoda `writerow()` zapisuje jeden rekord z listy wartości (liczby zamienia na tekst sama), a `writerows()` — wiele rekordów z obiektu iterowalnego. Pola zawierające przecinek, cudzysłów albo znak nowego wiersza są automatycznie ujmowane w cudzysłowy:

```python title="csv-zapis.py"
import csv

wiersze = [["imię", "wiek", "uwagi"], ["Ala", 30, "lubi kawę, herbatę"], ["Ola", 25, ""]]
with open("osoby.csv", "w", encoding="utf-8", newline="") as plik:
    pisarz = csv.writer(plik)
    pisarz.writerows(wiersze)

with open("osoby.csv", encoding="utf-8") as plik:
    print(plik.read(), end="")
```

```{ .text .no-copy }
imię,wiek,uwagi
Ala,30,"lubi kawę, herbatę"
Ola,25,
```

### Argument `newline=""` w module `csv`

W obu przykładach plik otwarto z argumentem `newline=""` z podrozdziału o plikach tekstowych. Moduł `csv` sam zapisuje znaki końca wiersza — w domyślnych ustawieniach modułu `\r\n` — a obiekt pliku bez `newline=""` przetłumaczyłby zawarty w nich `\n` na `\r\n`, dając na Windows `\r\r\n` i puste wiersze między rekordami; przy odczycie `newline=""` pozwala modułowi poprawnie rozpoznać znaki nowego wiersza wewnątrz pól w cudzysłowach:

```python title="bez-newline.py"
import csv

with open("zle.csv", "w", encoding="utf-8") as plik:  # celowo bez newline=""
    csv.writer(plik).writerows([["a", 1], ["b", 2]])
with open("zle.csv", "rb") as plik:
    print(plik.read())
with open("zle.csv", encoding="utf-8") as plik:
    print(plik.read().splitlines())
```

```{ .text .no-copy }
b'a,1\r\r\nb,2\r\r\n'
['a,1', '', 'b,2', '']
```

Podgląd bajtów pokazuje podwojony `\r`, a odczyt w trybie tekstowym — pusty wiersz po każdym rekordzie. Dokumentacja modułu formułuje regułę wprost: plik dla `csv` otwieramy zawsze z `newline=""`, do odczytu i do zapisu.

## Wiersze jako słowniki — `DictReader` i `DictWriter`

Dostęp do pól przez indeks listy jest podatny na błędy — zmiana kolejności kolumn w pliku powoduje błędne działanie programu. `csv.DictReader` odczytuje nagłówek sam i zwraca każdy rekord jako słownik z nazwami kolumn jako kluczami; `csv.DictWriter` z listą `fieldnames` zapisuje słowniki, a `writeheader()` wypisuje wiersz nagłówka:

```python title="csv-slowniki.py"
import csv

with open("oceny.csv", encoding="utf-8", newline="") as plik:
    for rekord in csv.DictReader(plik):
        print(rekord)

srednie = {"Ala": 4.75, "Ola": 3.5}
with open("srednie.csv", "w", encoding="utf-8", newline="") as plik:
    pisarz = csv.DictWriter(plik, fieldnames=["imię", "średnia"])
    pisarz.writeheader()
    for imie, srednia in srednie.items():
        pisarz.writerow({"imię": imie, "średnia": srednia})

with open("srednie.csv", encoding="utf-8") as plik:
    print(plik.read(), end="")
```

```{ .text .no-copy }
{'imię': 'Ala', 'przedmiot': 'matematyka', 'ocena': '4.5'}
{'imię': 'Ala', 'przedmiot': 'fizyka', 'ocena': '5.0'}
{'imię': 'Ola', 'przedmiot': 'matematyka', 'ocena': '3.5'}
imię,średnia
Ala,4.75
Ola,3.5
```

Wartości w słownikach nadal są łańcuchami; konwersję wykonuje program, który wie, że kolumna `ocena` zawiera liczby. Do obliczeń na kolumnach — średnich, grupowania według przedmiotu — wystarczą narzędzia z rozdziałów 5 i 7 (`defaultdict`, `Counter`); przy większych danych sięga się po pakiet zewnętrzny pandas, któremu poświęcamy osobny rozdział. <!-- TODO: link po powstaniu rozdziału o pandas -->

## Pliki z Excela — średnik, cudzysłowy i `utf-8-sig`

Plik CSV zapisany przez polskiego Excela w formacie „CSV UTF-8” różni się od standardowego w trzech miejscach: pola rozdziela średnik (bo przecinek jest w polskich ustawieniach separatorem dziesiętnym), liczby mają przecinek dziesiętny, a plik zaczyna się od znacznika BOM (zwykły format „CSV” zapisuje tekst w stronie kodowej systemu, bez znacznika). Moduł `csv` obsługuje to argumentem `delimiter=";"`, konwersję liczb zostawia programowi, a znacznik BOM obsługuje kodowanie `utf-8-sig` z podrozdziału o plikach tekstowych — także przy zapisie, bo dzięki znacznikowi Excel rozpozna plik jako UTF-8 i poprawnie wyświetli polskie litery:

```python title="excel.py"
import csv

produkty = [
    ["produkt", "cena", "uwagi"],
    ["chleb", "4,50", "świeży"],
    ["masło", "8,99", 'opakowanie "extra"'],
]
with open("produkty.csv", "w", encoding="utf-8-sig", newline="") as plik:
    csv.writer(plik, delimiter=";").writerows(produkty)
with open("produkty.csv", "rb") as plik:
    print(plik.read())

with open("produkty.csv", encoding="utf-8-sig", newline="") as plik:
    for produkt, cena, uwagi in csv.reader(plik, delimiter=";"):
        print(produkt, "|", cena.replace(",", "."), "|", uwagi)
```

```{ .text .no-copy }
b'\xef\xbb\xbfprodukt;cena;uwagi\r\nchleb;4,50;\xc5\x9bwie\xc5\xbcy\r\nmas\xc5\x82o;8,99;"opakowanie ""extra"""\r\n'
produkt | cena | uwagi
chleb | 4.50 | świeży
masło | 8.99 | opakowanie "extra"
```

Cudzysłów wewnątrz pola jest w CSV podwajany, a całe pole ujmowane w cudzysłowy — `csv` zrobił to przy zapisie i odwrócił przy odczycie. Cenę z przecinkiem dziesiętnym zamieniamy na kropkę metodą `replace()` przed konwersją `float()` albo `Decimal()`. Zestaw reguł — separator, znak cudzysłowu, koniec wiersza — nazywa się w module **dialektem** (ang. *dialect*); domyślny `excel` odpowiada angielskiemu Excelowi, a pojedyncze argumenty, jak `delimiter`, nadpisują jego ustawienia. Argument `quoting=csv.QUOTE_ALL` każe ujmować w cudzysłowy wszystkie pola, domyślny `csv.QUOTE_MINIMAL` — tylko te, które tego wymagają, a znak cudzysłowu zmienia `quotechar`.

## Format JSON i moduł `json`

JSON zapisuje dane zagnieżdżone: obiekty w nawiasach klamrowych, tablice w kwadratowych, łańcuchy w cudzysłowach podwójnych, liczby, wartości `true`, `false` i `null`. Wygląda niemal jak literał słownika Pythona, ale nie jest kodem Pythona: cudzysłowy muszą być podwójne, a przecinek po ostatnim elemencie jest błędem.

### `dumps()` i `loads()`

`json.dumps()` zamienia obiekt Pythona na łańcuch JSON — jest to **serializacja** (ang. *serialization*) — a `json.loads()` odtwarza obiekt z łańcucha (deserializacja). Argument `indent` włącza układ wielowierszowy z wcięciami, a `ensure_ascii=False` pozwala zapisać polskie litery wprost zamiast sekwencjami `\u…`:

```python title="json-podstawy.py"
import json

dane = {"imię": "Ala", "wiek": 30, "oceny": [4.5, 5.0], "aktywna": True, "adres": None}
tekst = json.dumps(dane)
print(tekst)
print(json.dumps(dane, ensure_ascii=False, indent=2))
wczytane = json.loads(tekst)
print(wczytane == dane, wczytane["oceny"][1])
```

```{ .text .no-copy }
{"imi\u0119": "Ala", "wiek": 30, "oceny": [4.5, 5.0], "aktywna": true, "adres": null}
{
  "imię": "Ala",
  "wiek": 30,
  "oceny": [
    4.5,
    5.0
  ],
  "aktywna": true,
  "adres": null
}
True 5.0
```

Domyślny zapis ze znakami spoza ASCII w postaci `\u0119` jest poprawnym JSON-em i każde narzędzie go odczyta, ale dla człowieka jest nieczytelny; w plikach zapisywanych w UTF-8 stosujemy `ensure_ascii=False`. Argument `sort_keys=True` porządkuje klucze alfabetycznie, co ułatwia porównywanie plików.

### Mapowanie typów

JSON ma mniej typów niż Python, więc konwersja w obie strony nie jest odwracalna dla wszystkiego:

| Python | zapis JSON | JSON → Python |
|---|---|---|
| `dict` | obiekt `{}` | `dict` |
| `list`, `tuple` | tablica `[]` | `list` |
| `str` | łańcuch | `str` |
| `int`, `float` | liczba | `int` albo `float` |
| `True`, `False` | `true`, `false` | `True`, `False` |
| `None` | `null` | `None` |

```python title="json-typy.py"
import json
from decimal import Decimal

print(json.dumps((1, 2)), type(json.loads("[1, 2]")).__name__)
print(json.dumps({2: "a", 2.5: "b", True: "c", None: "d"}))
try:
    json.dumps({(1, 2): "b"})
except TypeError as e:
    print("TypeError:", e)
print(json.dumps(float("nan")), json.dumps(10 ** 20))
try:
    json.dumps(Decimal("1.10"))
except TypeError as e:
    print("TypeError:", e)
print(json.dumps(Decimal("1.10"), default=str))
```

```{ .text .no-copy }
[1, 2] list
{"2": "a", "2.5": "b", "true": "c", "null": "d"}
TypeError: keys must be str, int, float, bool or None, not tuple
NaN 100000000000000000000
TypeError: Object of type Decimal is not JSON serializable
"1.10"
```

Krotka wraca jako lista, a klucze słownika — zawsze jako łańcuchy, bo klucze obiektu JSON muszą być tekstem; klucz-krotka nie ma odpowiednika i kończy się `TypeError`. Zapis `NaN` nie należy do standardu JSON i inne języki mogą go odrzucić (argument `allow_nan=False` zamienia go w błąd), a bardzo duże liczby całkowite są zapisywane bez ograniczeń. Obiekt spoza tabeli — tu `Decimal` z rozdziału 3 — nie jest serializowalny; argument `default=` podaje funkcję, która zamieni go na coś serializowalnego, najprościej `str`. Własne typy danych zapisujemy do JSON w podrozdziale [Klasy danych — dataclass, NamedTuple i Enum](../12-oop-zaawansowane/klasy-danych.md#funkcje-asdict-replace-i-zapis-do-json) rozdziału 12.

### `dump()` i `load()` z plikiem

Odpowiedniki bez `s` w nazwie pracują na otwartym pliku tekstowym — `json.dump(obiekt, plik)` zapisuje, `json.load(plik)` wczytuje — z tymi samymi argumentami. Plik otwieramy w trybie tekstowym z `encoding="utf-8"`:

```python title="json-plik.py"
import json

ustawienia = {"motyw": "ciemny", "rozmiar_czcionki": 12, "ostatnie_pliki": ["a.txt", "b.txt"]}
with open("ustawienia.json", "w", encoding="utf-8") as plik:
    json.dump(ustawienia, plik, ensure_ascii=False, indent=2)

with open("ustawienia.json", encoding="utf-8") as plik:
    print(plik.read())
with open("ustawienia.json", encoding="utf-8") as plik:
    wczytane = json.load(plik)
print(wczytane == ustawienia)
```

```{ .text .no-copy }
{
  "motyw": "ciemny",
  "rozmiar_czcionki": 12,
  "ostatnie_pliki": [
    "a.txt",
    "b.txt"
  ]
}
True
```

### Błędy — `JSONDecodeError`

Niepoprawny tekst zgłasza `json.JSONDecodeError` — odmianę `ValueError` z rozdziału 8 — z atrybutami `msg`, `lineno` i `colno` wskazującymi miejsce błędu. Dwie najczęstsze przyczyny to cudzysłowy pojedyncze i przecinek po ostatnim elemencie, nawyki przeniesione z Pythona:

```python title="json-blad.py"
import json

for tekst in ['{"a": 1}', "{'a': 1}", '{"a": 1,}', ""]:
    try:
        print(json.loads(tekst))
    except json.JSONDecodeError as e:
        print("błąd:", e.msg, "| wiersz", e.lineno, "kolumna", e.colno)
```

```{ .text .no-copy }
{'a': 1}
błąd: Expecting property name enclosed in double quotes | wiersz 1 kolumna 2
błąd: Illegal trailing comma before end of object | wiersz 1 kolumna 8
błąd: Expecting value | wiersz 1 kolumna 1
```

Pusty łańcuch — na przykład z pustego pliku ustawień — również jest błędem; program wczytujący plik JSON powinien przewidzieć zarówno brak pliku, jak i jego uszkodzenie.

## Narzędzie `python -m json`

Moduł `json` uruchomiony jako program (od Pythona 3.14 `python -m json`; wcześniejsza nazwa `python -m json.tool` nadal działa) sprawdza poprawność pliku i wypisuje go w czytelnym układzie — w terminalu obsługującym kolory z wyróżnieniem składni:

```powershell title="Terminal"
python -m json ustawienia.json --indent 4
python -m json --compact ustawienia.json
```

```{ .text .no-copy }
{
    "motyw": "ciemny",
    "rozmiar_czcionki": 12,
    "ostatnie_pliki": [
        "a.txt",
        "b.txt"
    ]
}
{"motyw":"ciemny","rozmiar_czcionki":12,"ostatnie_pliki":["a.txt","b.txt"]}
```

Opcja `--sort-keys` porządkuje klucze, `--no-ensure-ascii` wypisuje polskie litery wprost, a bez nazwy pliku narzędzie czyta standardowe wejście, więc nadaje się na koniec potoku: `Get-Content dane.json | python -m json`.

## Zapis stanu programu

Typowym zastosowaniem JSON jest zachowanie stanu programu między uruchomieniami: listy zadań, ustawień, ostatnio otwartych plików. Dwie funkcje — wczytująca z obsługą braku pliku i zapisująca — wystarczą, a struktura danych to zwykłe listy i słowniki:

```python title="zadania.py"
import json
from pathlib import Path

PLIK = Path("zadania.json")


def wczytaj():
    """Zwraca listę zadań z pliku albo pustą listę, gdy pliku nie ma."""
    try:
        with PLIK.open(encoding="utf-8") as plik:
            return json.load(plik)
    except FileNotFoundError:
        return []


def zapisz(zadania):
    """Zapisuje listę zadań do pliku."""
    with PLIK.open("w", encoding="utf-8") as plik:
        json.dump(zadania, plik, ensure_ascii=False, indent=2)


zadania = wczytaj()
print("wczytano:", len(zadania), "zadań")
zadania.append({"tytuł": "kupić chleb", "zrobione": False})
zadania.append({"tytuł": "oddać książkę", "zrobione": True})
zapisz(zadania)
print(PLIK.read_text(encoding="utf-8"))
print("po ponownym wczytaniu:", len(wczytaj()), "zadań")
```

```{ .text .no-copy }
wczytano: 0 zadań
[
  {
    "tytuł": "kupić chleb",
    "zrobione": false
  },
  {
    "tytuł": "oddać książkę",
    "zrobione": true
  }
]
po ponownym wczytaniu: 2 zadań
```

Przy pierwszym uruchomieniu pliku nie ma i `wczytaj()` zwraca pustą listę; każde kolejne uruchomienie zaczyna od dwóch zapisanych zadań i dopisuje następne — w prawdziwym programie nowe zadania pochodziłyby od użytkownika. Wzorzec „wczytaj, zmień, zapisz” z jawnym `encoding` i `ensure_ascii=False` wystarcza dla danych, które mieszczą się w pamięci; przy większych zbiorach właściwa jest baza danych, na przykład wbudowany moduł `sqlite3`.

## Inne formaty — `tomllib`, `pickle` i `compression` (dla dociekliwych)

Format TOML poznaliśmy w rozdziale 7 jako zapis pliku `pyproject.toml` (tu w uproszczonej postaci); moduł `tomllib` (od Pythona 3.11) go odczytuje — wyłącznie odczytuje, plik otwarty w trybie binarnym — do zagnieżdżonych słowników:

```toml title="pyproject.toml"
[project]
name = "geometria"
version = "0.1.0"
dependencies = []
```

```python title="tomllib-demo.py"
import tomllib

with open("pyproject.toml", "rb") as plik:
    konfiguracja = tomllib.load(plik)
print(konfiguracja)
print(konfiguracja["project"]["version"])
```

```{ .text .no-copy }
{'project': {'name': 'geometria', 'version': '0.1.0', 'dependencies': []}}
0.1.0
```

Moduł `pickle` serializuje niemal dowolne obiekty Pythona do postaci binarnej, także takie, których JSON nie obsługuje. Ma dwie wady, przez które w tej książce nie zapisujemy nim własnych danych — pośrednio korzystają z niego jednak `multiprocessing` i `concurrent.futures` z rozdziału [15. Współbieżność — wątki, procesy i GIL](../15-wspolbieznosc/procesy-i-executory.md), przesyłając nim argumenty i wyniki między procesami: odczyt danych `pickle` z niezaufanego źródła może wykonać dowolny kod — dokumentacja ostrzega o tym wprost — a format jest zrozumiały tylko dla Pythona: nowszy interpreter odczyta starsze dane, ale nie odwrotnie, a każda zmiana własnych typów danych w programie unieważnia zapisane pliki. Do wymiany danych i ich przechowywania wybieramy JSON albo CSV.

Pakiet `compression` (od Pythona 3.14) zbiera moduły kompresji pod wspólną nazwą — `compression.gzip`, `compression.bz2`, `compression.lzma`, `compression.zlib` — i dodaje `compression.zstd`, obsługujący nowoczesny algorytm Zstandard. Kompresja działa na bajtach, więc tekst najpierw kodujemy:

```python title="zstd-demo.py"
from compression import zstd

dane = ("wiersz danych;" * 200).encode("utf-8")
skompresowane = zstd.compress(dane)
print(len(dane), "->", len(skompresowane), "bajtów")
print(zstd.decompress(skompresowane) == dane)
```

```{ .text .no-copy }
2800 -> 32 bajtów
True
```

Powtarzalne dane kompresują się bardzo dobrze; dla danych losowych zysk jest znikomy. Te same moduły obsługują skompresowane pliki (`compression.gzip.open()` zwraca obiekt pliku), a moduły `zipfile` i `tarfile` — całe archiwa.

Tym podrozdziałem kończymy rozdział o wejściu i wyjściu. Od formatowania pojedynczej liczby przeszliśmy przez strumienie i terminal do plików tekstowych i binarnych, ścieżek oraz formatów danych; wspólny model — strumień tekstowy z kodowaniem między znakami a bajtami — pozostaje ten sam niezależnie od tego, czy po drugiej stronie jest ekran, plik czy inny program.
