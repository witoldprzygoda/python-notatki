# Styl obsługi błędów i testy wyjątków

Dwa poprzednie podrozdziały dały nam składnię: `try`/`except` do przechwytywania i `raise` do zgłaszania. Ten podrozdział dotyczy decyzji, które składnia pozostawia programiście: czy sprawdzić warunek przed operacją, czy wykonać operację i obsłużyć błąd; jak szeroki powinien być blok `try`; których konstrukcji unikać, choć są poprawne składniowo; jak sprawdzić testem, że funkcja zgłasza wyjątek wtedy, gdy powinna. Na koniec, dla dociekliwych, poznajemy grupy wyjątków — mechanizm zgłaszania kilku błędów naraz.

## Dwa style: LBYL i EAFP

Ten sam problem — odczyt ceny owocu, którego może nie być w cenniku — można rozwiązać na trzy sposoby:

```python title="style-slownik.py"
ceny = {"jabłko": 3, "gruszka": 4}
zamowienie = ["jabłko", "banan"]

for owoc in zamowienie:
    if owoc in ceny:
        print(owoc, ceny[owoc])
    else:
        print(owoc, "brak w cenniku")

for owoc in zamowienie:
    try:
        print(owoc, ceny[owoc])
    except KeyError:
        print(owoc, "brak w cenniku")

for owoc in zamowienie:
    print(owoc, ceny.get(owoc, "brak w cenniku"))
```

```{ .text .no-copy }
jabłko 3
banan brak w cenniku
jabłko 3
banan brak w cenniku
jabłko 3
banan brak w cenniku
```

Pierwsza pętla sprawdza warunek przed operacją. Dokumentacja Pythona nazywa ten styl **LBYL** (ang. *look before you leap* — „patrz, zanim skoczysz”). Druga pętla wykonuje operację i obsługuje wyjątek — styl **EAFP** (ang. *easier to ask forgiveness than permission* — „łatwiej prosić o wybaczenie niż o pozwolenie”). Trzecia pętla nie potrzebuje ani warunku, ani wyjątku, bo metoda `get()` z podrozdziału [Słownik (dict)](../05-typy-zlozone/slownik.md#metody-sownika) obsługuje brak klucza sama; tam, gdzie taka metoda istnieje, jest zwykle najlepszym wyborem.

Między dwoma pierwszymi stylami wybieramy według dwóch kryteriów. Pierwsze to wierność sprawdzenia. Warunek LBYL musi odtworzyć reguły operacji, którą poprzedza, a to nie zawsze jest proste: w poprzednim podrozdziale `isdigit()` odrzucało liczby ujemne i zapisy ze spacjami, które `int()` przyjmuje. Operacja sama zna swoje reguły najlepiej i sama je sprawdza — EAFP nie powtarza tej logiki. Sprawdzenie może też stracić ważność, zanim operacja się wykona: plik istniejący w chwili sprawdzenia może zostać usunięty przed otwarciem, a w programach wielowątkowych inna część programu może zmienić słownik między `in` a odczytem; próba z obsługą wyjątku nie ma tej luki. Drugie kryterium to częstość niepowodzeń. Od Pythona 3.11 wejście w blok `try`, w którym wyjątek nie wystąpił, nie kosztuje nic; zgłoszenie i przechwycenie wyjątku kosztuje natomiast więcej niż proste porównanie. EAFP jest więc właściwe dla sytuacji wyjątkowych — takich, które zdarzają się rzadko — a LBYL dla rozgałęzień, w których obie drogi są równie zwyczajne. Sformułowanie „Python preferuje EAFP”, spotykane w materiałach kursowych, należy czytać z tym zastrzeżeniem: chodzi o unikanie sprawdzeń, które powielają regułę operacji, nie o zastępowanie każdej instrukcji `if` blokiem `try`.

## Zasięg bloku `try`

Blok `try` powinien obejmować wyłącznie tę instrukcję, po której spodziewamy się wyjątku. Zbyt szeroki blok przechwytuje więcej, niż zamierzaliśmy — także błędy tego samego typu z zupełnie innych przyczyn:

```python title="szeroki-try.py"
def sredni_wiek(wpisy):
    """Zwraca średni wiek z listy wpisów w formacie „imię;wiek”."""
    wieki = []
    for wpis in wpisy:
        try:
            imie, wiek = wpis.split(";")
            wieki.append(int(wiek))
        except ValueError:
            print(f"pomijam wpis {wpis!r}")
    return sum(wieki) / len(wieki)


print(sredni_wiek(["Ala;30", "Ola;abc", "Ela;40"]))
print(sredni_wiek(["Ala;30;Kraków", "Ela;40"]))
```

```{ .text .no-copy }
pomijam wpis 'Ola;abc'
35.0
pomijam wpis 'Ala;30;Kraków'
40.0
```

Drugie wywołanie ujawnia problem. Wpis `Ala;30;Kraków` ma trzy pola, więc rozpakowanie `imie, wiek = …` zgłasza `ValueError` — ten sam typ, który zgłasza `int()` dla wieku niebędącego liczbą. Klauzula `except ValueError` przechwyciła oba przypadki i oba opisała jako „pomijam wpis”, choć drugi jest błędem formatu danych, o którym program powinien poinformować, a nie go ukryć. Zawężamy blok `try` do konwersji, a rozpakowanie zostawiamy poza nim; instrukcje wykonywane tylko po udanej konwersji trafiają do klauzuli `else`:

```python title="waski-try.py"
def sredni_wiek(wpisy):
    """Zwraca średni wiek z listy wpisów w formacie „imię;wiek”."""
    wieki = []
    for wpis in wpisy:
        imie, wiek = wpis.split(";")
        try:
            wiek_liczba = int(wiek)
        except ValueError:
            print(f"pomijam wpis {wpis!r}: {wiek!r} nie jest liczbą")
        else:
            wieki.append(wiek_liczba)
    return sum(wieki) / len(wieki)


print(sredni_wiek(["Ala;30", "Ola;abc", "Ela;40"]))
print(sredni_wiek(["Ala;30;Kraków", "Ela;40"]))
```

```{ .text .no-copy }
pomijam wpis 'Ola;abc': 'abc' nie jest liczbą
35.0
Traceback (most recent call last):
  File "waski-try.py", line 16, in <module>
    print(sredni_wiek(["Ala;30;Kraków", "Ela;40"]))
          ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "waski-try.py", line 5, in sredni_wiek
    imie, wiek = wpis.split(";")
    ^^^^^^^^^^
ValueError: too many values to unpack (expected 2, got 3)
```

Błąd formatu przerywa teraz program ze śladem wskazującym dokładnie rozpakowanie, a komunikat o pomijanym wpisie może zawierać wartość, która zawiodła, bo klauzula `except` obsługuje tylko jedną, znaną sobie sytuację. Wąski blok `try` ma jeszcze jedną zaletę: czytelnik kodu od razu widzi, która instrukcja może zawieść.

## Antywzorce obsługi błędów

Trzy konstrukcje są poprawne składniowo, a mimo to należy ich unikać. Pierwszą jest klauzula `except` bez typu, zwana **gołym `except`** (ang. *bare except*). Przechwytuje ona każdy wyjątek, włącznie z `KeyboardInterrupt` i `SystemExit` z hierarchii z poprzedniego podrozdziału, więc program przestaje reagować na ++ctrl+c++ i na własne `sys.exit()`:

```python title="goly-except.py"
def dluga_operacja():
    """Symuluje operację przerwaną przez użytkownika z klawiatury."""
    raise KeyboardInterrupt


try:
    dluga_operacja()
except:
    print("wystąpił błąd, kontynuuję")
print("program działa dalej mimo przerwania")
```

```{ .text .no-copy }
wystąpił błąd, kontynuuję
program działa dalej mimo przerwania
```

W prawdziwym programie `KeyboardInterrupt` zgłosiłby interpreter po naciśnięciu ++ctrl+c++ w trakcie długiej operacji; tu zgłaszamy go jawnie, by wynik był powtarzalny. Zamiast gołego `except` piszemy `except Exception`, gdy naprawdę trzeba przechwycić wszystkie błędy — na przykład na najwyższym poziomie programu, by zapisać ślad do dziennika przed zakończeniem, o czym mowa w podrozdziale o logowaniu — a w pozostałych przypadkach wymieniamy konkretne typy.

Drugą konstrukcją jest **połykanie wyjątków** (ang. *swallowing exceptions*): klauzula `except`, która nic nie robi. Jeden z aforyzmów Zen Pythona ([PEP 20](https://peps.python.org/pep-0020/), poznanego w podrozdziale [Konsola w praktyce](../02-konsola/konsola-w-praktyce.md#zen-pythona)) brzmi *Errors should never pass silently. Unless explicitly silenced* — błędy nie powinny przechodzić niezauważone, chyba że uciszono je celowo. Funkcja poniżej ucisza je bez celu:

```python title="polykanie.py"
def srednia(dane):
    """Zwraca średnią elementów albo None przy jakimkolwiek błędzie."""
    try:
        return sum(dane) / len(dane)
    except Exception:
        pass


print(srednia([1, 2, 3]))
print(srednia([]))
print(srednia("abc"))
```

```{ .text .no-copy }
2.0
None
None
```

Pusta lista i łańcuch znaków to dwa różne błędy — `ZeroDivisionError` i `TypeError` — a program otrzymał w obu przypadkach `None` bez żadnej informacji. Błąd ujawni się dopiero tam, gdzie ktoś spróbuje użyć `None` jako liczby, daleko od przyczyny; jest to dokładnie sytuacja, z której wyprowadziła nas instrukcja `raise`. Uciszenie wyjątku jest uzasadnione tylko wtedy, gdy wiemy, jaki wyjątek uciszamy i dlaczego jego wystąpienie nie ma znaczenia — na przykład brak pliku z ustawieniami, który wolno pominąć; taki przypadek zapisuje się jawnie, wskazanym typem, a w następnym podrozdziale poznamy przeznaczoną do tego konstrukcję `contextlib.suppress`.

Trzecią konstrukcją jest **obsługa zbyt wcześnie**: funkcja pomocnicza, która przechwytuje wyjątek i wypisuje komunikat, choć nie wie, jak program powinien zareagować. Funkcja `silnia()` z poprzedniego podrozdziału zgłasza `ValueError` i nie próbuje go obsłużyć, bo nie wie, czy program chce wypisać komunikat, poprosić o inną wartość, czy zakończyć pracę. Obsługę umieszczamy tak wysoko, jak to możliwe, i tak nisko, jak to konieczne — tam, gdzie znane są konsekwencje błędu.

## Testy wyjątków w pytest

Skoro zgłoszenie wyjątku dla błędnego argumentu jest częścią kontraktu funkcji, powinno być sprawdzane testem tak samo jak poprawne wyniki. Test z instrukcją `assert` z podrozdziału [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md#katalog-tests) nie nadaje się do tego wprost: wywołanie `silnia(-3)` zgłasza wyjątek, który przerwałby test, zanim `assert` zdążyłby cokolwiek sprawdzić. Narzędzie pytest dostarcza `pytest.raises()`, które oczekuje wyjątku podanego typu (albo jego odmiany) w objętym nim bloku: test jest zaliczony, gdy taki wyjątek wystąpił, niezaliczony, gdy go zabrakło, a wyjątek innego typu opuszcza blok i kończy test błędem. Konstrukcja `with`, w której `pytest.raises()` występuje, jest tematem następnego podrozdziału — tu wystarczy wiedzieć, że wcięty blok pod `with` jest kodem, który ma zgłosić wyjątek. Umieszczamy `silnia()` w module `obliczenia.py` w katalogu projektu; dla pojedynczego modułu bez pakietu wystarcza układ płaski z rozdziału 7 — układ `src` z `pyproject.toml` ma sens, gdy kod tworzy pakiet przeznaczony do instalacji:

```{ .text .no-copy }
projekt/
├── obliczenia.py
└── tests/
    ├── __init__.py
    └── test_obliczenia.py
```

```python title="obliczenia.py"
"""Udostępnia funkcje obliczeniowe z kontrolą argumentów."""


def silnia(n):
    """Zwraca n! dla nieujemnej liczby całkowitej n."""
    if not isinstance(n, int):
        raise TypeError(f"n musi być liczbą całkowitą, otrzymano {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n musi być nieujemne, otrzymano {n}")
    wynik = 1
    for k in range(2, n + 1):
        wynik *= k
    return wynik
```

```python title="tests/test_obliczenia.py"
"""Sprawdza funkcję silnia z modułu obliczenia."""

import pytest

from obliczenia import silnia


def test_silnia_wartosci():
    """Sprawdza wartości dla 0, 1 i 5."""
    assert silnia(0) == 1
    assert silnia(1) == 1
    assert silnia(5) == 120


def test_silnia_ujemne():
    """Sprawdza, że ujemny argument zgłasza ValueError."""
    with pytest.raises(ValueError, match="nieujemne"):
        silnia(-3)


def test_silnia_typ():
    """Sprawdza, że argument innego typu zgłasza TypeError."""
    with pytest.raises(TypeError, match="całkowitą") as excinfo:
        silnia(2.5)
    assert "float" in str(excinfo.value)
```

```powershell title="Terminal"
python -m pytest
```

```{ .text .no-copy }
...
collected 3 items

tests\test_obliczenia.py ...                                             [100%]

============================== 3 passed in 0.02s ==============================
```

Argument `match=` zawęża oczekiwanie do wyjątków, których komunikat zawiera podany fragment — formalnie jest to wyrażenie regularne, w praktyce zwykle fragment tekstu, przy czym znaki specjalne wyrażeń regularnych, jak nawias, trzeba w nim poprzedzić ukośnikiem odwrotnym albo przepuścić przez `re.escape()`; dzięki niemu test odróżnia `ValueError` z kontroli zakresu od `ValueError` z innej przyczyny. Dopisek `as excinfo` daje dostęp do zgłoszonego wyjątku po zakończeniu bloku: `excinfo.value` jest obiektem wyjątku, `excinfo.type` jego typem. Kod następujący w bloku po instrukcji, która zgłosiła wyjątek, nie wykonuje się — dlatego w bloku `with` umieszczamy wyłącznie wywołanie, po którym spodziewamy się wyjątku, a dalsze sprawdzenia piszemy pod nim, tak jak w `test_silnia_typ()`.

Gdyby ktoś usunął kontrolę argumentów z `silnia()`, pierwszy test nadal by przechodził, a dwa pozostałe wykryłyby zmianę. Fragment raportu pytest dla wersji bez kontroli:

```{ .text .no-copy }
...
tests\test_obliczenia.py .FF                                             [100%]

================================== FAILURES ===================================
_____________________________ test_silnia_ujemne ______________________________

    def test_silnia_ujemne():
        """Sprawdza, że ujemny argument zgłasza ValueError."""
>       with pytest.raises(ValueError, match="nieujemne"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests\test_obliczenia.py:17: Failed
_______________________________ test_silnia_typ _______________________________

    def test_silnia_typ():
        """Sprawdza, że argument innego typu zgłasza TypeError."""
>       with pytest.raises(TypeError, match="całkowitą") as excinfo:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: Regex pattern did not match.
E         Expected regex: 'całkowitą'
E         Actual message: "'float' object cannot be interpreted as an integer"

tests\test_obliczenia.py:23: AssertionError
...
========================= 2 failed, 1 passed in 0.08s =========================
```

Komunikat `DID NOT RAISE` mówi wprost, czego zabrakło. Trzeci test bez argumentu `match=` przeszedłby mimo usunięcia kontroli, bo `range()` sam zgłasza `TypeError` dla argumentu `2.5` — tyle że z własnym komunikatem; dopiero `match=` sprawdza, że wyjątek pochodzi z kontroli argumentów, a nie z przypadkowego miejsca w obliczeniach. Testy wyjątków są wobec tego równie istotne, jak testy wartości: dokumentują, że funkcja odrzuca błędne dane, i chronią tę właściwość przed przypadkową zmianą.

## Grupy wyjątków i `except*` (dla dociekliwych)

Instrukcja `raise` zgłasza jeden wyjątek, a pierwszy błąd przerywa operację. Czasem lepiej zebrać wszystkie błędy naraz — na przykład sprawdzić cały plik z danymi i zgłosić listę wszystkich niepoprawnych wpisów, zamiast zatrzymywać się na pierwszym. Od Pythona 3.11 służy do tego **grupa wyjątków** (ang. *exception group*): typ `ExceptionGroup` przyjmuje komunikat i listę wyjątków, a ślad wypisuje je wszystkie:

```python title="grupa.py"
def sprawdz_wpisy(wpisy):
    """Zgłasza grupę wyjątków z wszystkimi błędnymi wpisami."""
    bledy = []
    for wpis in wpisy:
        try:
            int(wpis)
        except ValueError as e:
            bledy.append(e)
    if bledy:
        raise ExceptionGroup("błędne wpisy", bledy)


sprawdz_wpisy(["1", "x", "3", "y"])
```

```{ .text .no-copy }
  + Exception Group Traceback (most recent call last):
  |   File "grupa.py", line 13, in <module>
  |     sprawdz_wpisy(["1", "x", "3", "y"])
  |     ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  |   File "grupa.py", line 10, in sprawdz_wpisy
  |     raise ExceptionGroup("błędne wpisy", bledy)
  | ExceptionGroup: błędne wpisy (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "grupa.py", line 6, in sprawdz_wpisy
    |     int(wpis)
    |     ~~~^^^^^^
    | ValueError: invalid literal for int() with base 10: 'x'
    +---------------- 2 ----------------
    | Traceback (most recent call last):
    |   File "grupa.py", line 6, in sprawdz_wpisy
    |     int(wpis)
    |     ~~~^^^^^^
    | ValueError: invalid literal for int() with base 10: 'y'
    +------------------------------------
```

Grupę obsługuje klauzula `except*`, która z grupy wybiera wyjątki podanego typu i udostępnia je jako podgrupę z atrybutem `exceptions`; wyjątki innych typów pozostają w grupie i wędrują dalej:

```python title="grupa-obsluga.py"
def sprawdz_wpisy(wpisy):
    """Zgłasza grupę wyjątków z wszystkimi błędnymi wpisami."""
    bledy = []
    for wpis in wpisy:
        try:
            int(wpis)
        except ValueError as e:
            bledy.append(e)
    if bledy:
        raise ExceptionGroup("błędne wpisy", bledy)


try:
    sprawdz_wpisy(["1", "x", "3", "y"])
except* ValueError as grupa:
    print(len(grupa.exceptions), "błędne wpisy:")
    for e in grupa.exceptions:
        print("-", e)
```

```{ .text .no-copy }
2 błędne wpisy:
- invalid literal for int() with base 10: 'x'
- invalid literal for int() with base 10: 'y'
```

Grupy wyjątków powstały z myślą o programach współbieżnych, w których kilka zadań może zawieść jednocześnie, i tam wrócą w rozdziale o współbieżności; w programach sekwencyjnych przydają się przy walidacji zbiorów danych. <!-- TODO: link po powstaniu rozdziału o współbieżności --> Do codziennej pracy wystarczą zwykłe `raise` i `except`.

Pozostał ostatni element składni związany z wyjątkami: instrukcja `with`, którą widzieliśmy przy `pytest.raises()`. Jej właściwym zadaniem jest zwalnianie zasobów niezależnie od tego, czy wystąpił wyjątek — temat następnego podrozdziału.
