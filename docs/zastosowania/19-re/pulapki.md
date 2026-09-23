# Pułapki, wydajność i testy

Wyrażenie regularne, które działa na przykładzie, może zawieść na innym tekście — dopasować za dużo, za mało albo działać całe sekundy. Ten podrozdział pokazuje, skąd biorą się te problemy, jak sprawdzać wzorce testami i kiedy sięgnąć po inne narzędzie.

## Nawroty

```python title="nawroty.py"
import re
import time


def pomiar(wzorzec, tekst):
    start = time.perf_counter()
    wynik = re.fullmatch(wzorzec, tekst)
    return f"{time.perf_counter() - start:.3f} s", wynik is not None


for n in (22, 24, 26):
    print(n, pomiar(r"(a+)+b", "a" * n))
print("dzierżawczy", pomiar(r"(a++)+b", "a" * 26))
print("atomowy", pomiar(r"(?>a+)+b", "a" * 26))
print(re.fullmatch(r"a++a", "aaa"), re.fullmatch(r"a+a", "aaa"))
```

```{ .text .no-copy }
22 ('0.113 s', False)
24 ('0.460 s', False)
26 ('1.913 s', False)
dzierżawczy ('0.000 s', False)
atomowy ('0.000 s', False)
None <re.Match object; span=(0, 3), match='aaa'>
```

Silnik `re` dopasowuje przez **nawroty** (ang. *backtracking*): gdy dalsza część wzorca zawodzi, cofa się i próbuje innego podziału tekstu między kwantyfikatory. Wzorzec `(a+)+b` na tekście z samych `a` ma wykładniczo wiele takich podziałów — każde dwa dodatkowe znaki wydłużają czas czterokrotnie, a kilkadziesiąt znaków wystarcza, by program przestał odpowiadać. Zjawisko nazywa się **nawrotami katastrofalnymi** (ang. *catastrophic backtracking*) i bierze się z zagnieżdżonych kwantyfikatorów lub alternatyw, które mogą dopasować to samo na wiele sposobów. Od Pythona 3.11 są dwa narzędzia obronne: **kwantyfikator dzierżawczy** (ang. *possessive quantifier*) `a++` nie oddaje raz dopasowanych znaków, a **grupa atomowa** (ang. *atomic group*) `(?>…)` robi to samo dla całego fragmentu — dopasowanie zawodzi natychmiast zamiast po milionach prób. Skutek uboczny: `a++a` nigdy nie pasuje, bo `a++` nie zostawi znaku dla ostatniego `a`. Wzorce stosowane do tekstu od użytkowników projektujemy tak, by kwantyfikatory nie nakładały się na siebie — klasa zanegowana zamiast `.+`, jeden kwantyfikator zamiast zagnieżdżonych.

## Walidacja

```python title="walidacja.py"
import re

KOD_POCZTOWY = re.compile(r"\d{2}-\d{3}")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NIP = re.compile(r"\d{10}")


def poprawny_nip(tekst):
    cyfry = re.sub(r"[\s-]", "", tekst)
    if not NIP.fullmatch(cyfry):
        return False
    wagi = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    suma = sum(int(c) * w for c, w in zip(cyfry, wagi))
    return suma % 11 == int(cyfry[9])


for kod in ("33-300", "33300", "33-3000", " 33-300"):
    print(repr(kod), bool(KOD_POCZTOWY.fullmatch(kod)), bool(KOD_POCZTOWY.search(kod)))
for adres in ("jan.kowalski@firma.pl", "jan@firma", "jan@@firma.pl", "anna+sklep@example.co.uk"):
    print(repr(adres), bool(EMAIL.fullmatch(adres)))
for nip in ("526-10-40-828", "5261040828", "1234567890", "526104082"):
    print(repr(nip), poprawny_nip(nip))
print("12345".isdigit(), bool(re.fullmatch(r"\d+", "12345")), "١٢٣".isdigit(), bool(re.fullmatch(r"\d+", "١٢٣")), bool(re.fullmatch(r"[0-9]+", "١٢٣")))
```

```{ .text .no-copy }
'33-300' True True
'33300' False False
'33-3000' False True
' 33-300' False True
'jan.kowalski@firma.pl' True
'jan@firma' False
'jan@@firma.pl' False
'anna+sklep@example.co.uk' True
'526-10-40-828' True
'5261040828' True
'1234567890' False
'526104082' False
True True True True False
```

Do sprawdzania formatu służy `fullmatch()`, nie `search()` — `search()` znajdzie kod pocztowy wewnątrz `33-3000` i uzna błędny wpis za poprawny. Wyrażenie sprawdza tylko kształt: NIP o dobrym kształcie może mieć złą sumę kontrolną, którą liczymy zwykłym kodem; adres e-mail o dobrym kształcie może nie istnieć. `\d` i `str.isdigit()` przyjmują także cyfry innych systemów pisma (arabsko-indyjskie `١٢٣`); gdy chodzi wyłącznie o `0`–`9`, piszemy `[0-9]` albo używamy flagi `ASCII`.

## Testy wzorców

```python title="test_wzorce.py"
import re

import pytest

DATA = re.compile(r"\b(?P<d>\d{1,2})\.(?P<m>\d{1,2})\.(?P<rok>\d{4})\b")


@pytest.mark.parametrize("tekst, oczekiwane", [
    ("z dnia 23.09.2026", ("23", "09", "2026")),
    ("7.10.2026 płatna", ("7", "10", "2026")),
    ("1.1.2026", ("1", "1", "2026")),
])
def test_data_pasuje(tekst, oczekiwane):
    m = DATA.search(tekst)
    assert m is not None
    assert (m["d"], m["m"], m["rok"]) == oczekiwane


@pytest.mark.parametrize("tekst", ["2026-09-23", "123.09.2026", "23.09.26", "23/09/2026", "wersja 1.2.2026x"])
def test_data_nie_pasuje(tekst):
    assert DATA.search(tekst) is None
```

```powershell title="Terminal"
python -m pytest -q test_wzorce.py
```

```{ .text .no-copy }
........                                                                 [100%]
8 passed in 0.02s
```

Wzorzec to kod, więc ma testy: lista tekstów, które mają pasować, z oczekiwanymi grupami, i lista tych, które pasować nie mogą — `parametrize` z rozdziału 16 „Python Notatki” zamienia każdą pozycję w osobny test. Przypadki negatywne są ważniejsze od pozytywnych, bo to one wykrywają wzorzec zbyt luźny; przy każdej poprawce wzorca dopisujemy przypadek, który ją wymusił.

## Granice zastosowania

Wyrażenie regularne jest właściwe, gdy tekst ma kształt, który da się opisać w jednym wierszu. Gdy `str` wystarcza — `startswith()`, `in`, `split(";")`, `removeprefix()`, `strip()` — jest czytelniejszy i szybszy. Gdy dane mają format, mają też parser: `csv` i `json` z rozdziału 9 „Python Notatki”, `datetime.strptime()` dla dat, `urllib.parse` dla adresów z rozdziału 14 tej części, a dla HTML parser z rozdziału o pobieraniu stron — wyrażenie na znaczniki działa do pierwszego zagnieżdżenia. Poza biblioteką standardową istnieje moduł `regex` z tym samym interfejsem i dodatkami (klasy właściwości Unicode `\p{…}`, dopasowania rozmyte), potrzebny rzadko. Wzorce dłuższe niż kilkadziesiąt znaków piszemy w trybie `VERBOSE` z komentarzami — bez nich szybko stają się nieczytelne także dla autora.

## Lista kontrolna

- **Surowe łańcuchy** `r"…"` dla wzorców i tekstów zastępczych.
- **Klasy zanegowane** zamiast `.+`; kwantyfikatory bez zagnieżdżania; `fullmatch()` do walidacji.
- **Grupy nazwane** i `VERBOSE` dla wzorców dłuższych niż kilkadziesiąt znaków; `compile()` dla wzorców wielokrotnego użytku.
- **`re.escape()`** dla tekstu dopasowywanego dosłownie; `PatternError` obsłużony dla wzorców z zewnątrz.
- **Testy** z przypadkami negatywnymi; pomiar czasu na najdłuższym oczekiwanym tekście.
- **Parser zamiast wyrażenia** dla formatów, które go mają.

## Dalej: wiersz poleceń

Wzorce z tego rozdziału trafią do narzędzi uruchamianych z terminala: [następny rozdział](../20-cli/index.md) buduje programy wiersza poleceń z opcjami, plikami wejściowymi i kodami wyjścia, a dalszy — pobiera i parsuje strony, na których wyrażenia regularne ustępują parserowi HTML <!-- TODO: link po powstaniu rozdziału o pobieraniu i parsowaniu stron -->.
