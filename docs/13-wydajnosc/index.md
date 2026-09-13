# 13. Wydajność i optymalizacja

Dotąd pisaliśmy programy tak, aby były poprawne i czytelne; ten krótki rozdział dodaje trzecie kryterium — szybkość — ale w ustalonej kolejności. Program ma najpierw działać, potem zostać zmierzony, a poprawki wprowadzamy tylko tam, gdzie pomiar wskazał wąskie gardło. Rozdział daje do tego narzędzia z biblioteki standardowej: pomiar czasu funkcją `time.perf_counter()` i modułem `timeit`, profilowanie modułem `cProfile`, pomiar pamięci modułem `tracemalloc`. Następnie zbiera to, co w zwykłym kodzie przyspiesza najbardziej — wybór struktury danych, kilka idiomów, memoizację — i mierzy oszczędność pamięci z `__slots__`, domykając zapowiedzi z rozdziałów 8 i 10. Ostatni podrozdział, uzupełniający, przegląda drogi wyjścia poza czysty Python: wektoryzację w NumPy, kompilację w locie, kompilację do rozszerzeń, inny interpreter i wiele rdzeni.

Rozdział jest pomostem między blokiem obiektowym a częścią numeryczną książki. Pomiar z trzeciego podrozdziału pokazuje, że operacja na tablicy NumPy z następnego rozdziału przebiega kilkanaście razy szybciej niż pętla po liście, a omówienie kosztu interpretacji wyjaśnia, dlaczego; uwagi o wielu rdzeniach zapowiadają rozdział o współbieżności. Wszystkie liczby w rozdziale pochodzą z uruchomień na komputerze autora i na innym sprzęcie będą inne; istotne są proporcje, nie wartości.

---

## W tym rozdziale

1. [Pomiar czasu i profilowanie](pomiar-i-profilowanie.md) — zasada „najpierw pomiar”, `perf_counter()` i dekorator mierzący czas, `timeit`, `cProfile` i `pstats`, `sys.getsizeof()` i `tracemalloc`, porównanie wersji funkcji Fibonacciego
2. [Optymalizacja kodu](optymalizacja-kodu.md) — zasady optymalizacji, złożoność obliczeniowa i struktury danych, idiomy szybkiego kodu, memoizacja, `__slots__` z pomiarem, moduł `dis`
3. [Drogi przyspieszania](przyspieszanie-pythona.md) — podrozdział uzupełniający: koszt interpretacji, wektoryzacja w NumPy, Numba, Cython i mypyc, PyPy, `3.14t` i procesy, pakiet `profiling` w Pythonie 3.15
