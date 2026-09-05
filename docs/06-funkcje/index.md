# 6. Funkcje

Funkcja pełni w Pythonie dwie role. Pierwsza jest wspólna dla większości języków: funkcja to **wydzielona jednostka kodu**, dzięki której unikamy powtórzeń, a fragmentom programu nadajemy czytelne nazwy. Druga rola wynika z modelu obiektów Pythona: funkcja jest **zwykłym obiektem**, takim jak liczba czy lista — można ją związać z nazwą, przekazać innej funkcji jako argument, zwrócić jako wynik, przechować w kolekcji i przekształcić dekoratorem. Rozdział przechodzi od pierwszej roli do drugiej: od składni definicji, przez gramatykę argumentów i reguły zasięgu nazw, po domknięcia, funkcje generatorowe i dekoratory.

Rozdział opiera się na fundamentach położonych wcześniej. Nazwy jako referencje do obiektów i model pamięci (rozdział [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md)) wyjaśniają, co dzieje się z argumentem przekazanym do funkcji; katalog typów i adnotacje (rozdział [3. Nazwy i typy](../03-nazwy-typy/konwersje-i-adnotacje.md)) wracają w sygnaturach funkcji; iteratory (rozdział [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md)) prowadzą do funkcji generatorowych; pakowanie i rozpakowywanie sekwencji, krotki i słowniki (rozdział [5. Typy złożone](../05-typy-zlozone/krotka.md)) leżą u podstaw parametrów `*args` i `**kwargs`, a złożenia i wyrażenie generatorowe (rozdział [5. Typy złożone](../05-typy-zlozone/zlozenia.md)) znajdują odpowiedniki w funkcjach `map()` i `filter()` oraz w potokach generatorów.

Cały rozdział obywa się bez nowych modułów: moduły `functools` i `itertools`, o których wspominamy w zapowiedziach, poznamy w następnym rozdziale, poświęconym modułom i bibliotece standardowej, a tam też wrócimy do funkcji modułu `sys` sterujących limitem rekurencji. Ten rozdział jest do tego przygotowaniem.

---

## W tym rozdziale

1. [Definiowanie funkcji](definiowanie-funkcji.md) — instrukcje def i return, docstring i help(), adnotacje w sygnaturze, funkcja jako obiekt
2. [Argumenty i parametry](argumenty-i-parametry.md) — wartości domyślne, przekazywanie referencji, `*args` i `**kwargs`, parametry tylko pozycyjne i tylko nazwane
3. [Zasięg nazw i domknięcia](zasieg-nazw-i-domkniecia.md) — przestrzenie nazw i model LEGB, global i nonlocal, domknięcia, późne wiązanie nazw
4. [Funkcje jako obiekty](funkcje-jako-obiekty.md) — funkcje pierwszej klasy i wyższego rzędu, obiekty wywoływalne, wyrażenie lambda, funkcje klucza, map() i filter()
5. [Rekurencja](rekurencja.md) — przypadek bazowy i krok rekurencyjny, rekurencja a iteracja, struktury zagnieżdżone, limit rekurencji
6. [Funkcje generatorowe](funkcje-generatorowe.md) — yield, wstrzymanie i wznowienie wykonania, leniwość, generatory nieskończone, potoki, yield from
7. [Dekoratory](dekoratory.md) — funkcja opakowująca, składnia @, stan w domknięciu i memoizacja, metadane funkcji, dekoratory z argumentami, składanie dekoratorów
