# 3. Nazwy i typy w języku Python

Oficjalnie nazwy zmiennych w Pythonie mogą mieć dowolną długość i mogą składać się z wielkich i małych liter (A–Z, a–z), cyfr (0–9) oraz znaku podkreślenia (`_`). Pierwszym znakiem nazwy zmiennej nie może być cyfra.

Python ma też zestaw **słów kluczowych**, które są słowami zastrzeżonymi — nie można ich używać jako nazw zmiennych, nazw funkcji ani żadnych innych identyfikatorów. Choć na tym etapie poznawania języka jest to całkowicie nudny katalog 33 nazw, warto się z nimi zapoznać, ich znaczenie będziemy poznawać:

```{ .text .no-copy }
and, as, assert, break, class, continue, def, del, elif, else,
except, False, finally, for, from, global, if, import, in, is,
lambda, None, nonlocal, not, or, pass, raise, return, True,
try, while, with, yield
```

Typ obiektu określany jest podczas jego tworzenia. W Pythonie mamy kilka typów prostych oraz typy złożone (klasyfikacja ze względu na strukturę składowania — *storage*). Mogą one być modyfikowalne lub niemodyfikowalne (klasyfikacja ze względu na modyfikowalność — *update*). Dostęp do nich może być bezpośredni (liczby) lub sekwencyjny — różne kontenery (klasyfikacja rodzaju dostępu — *access*). Można wykonywać konwersję (rzutowanie).

Oto lista typów:

- **Text Type:** `str`
- **Numeric Types:** `int`, `float`, `complex`
- **Sequence Types:** `list`, `tuple`, `range`
- **Mapping Type:** `dict`
- **Set Types:** `set`, `frozenset`
- **Boolean Type:** `bool`
- **Binary Types:** `bytes`, `bytearray`, `memoryview`

---

## W tym rozdziale

1. [Typy i konwersje](typy-i-konwersje.md) — sprawdzanie typu, rzutowanie, adnotacje typów
2. [Typy proste](typy-proste.md) — bool, int, float, complex, str
3. [Obiekty i pamięć](obiekty-i-pamiec.md) — referencje, id(), niemodyfikowalność, del
4. [Operatory](operatory.md) — przegląd, `==` vs `is`, `in`
5. [Wyrażenia warunkowe](wyrazenia-warunkowe.md) — if/elif/else, operator trójskładnikowy, match
6. [Pętle i iteratory](petle-i-iteratory.md) — for, while, range, iteratory i generatory
