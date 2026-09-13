# 2. NumPy w praktyce

Rozdział 14 „Python Notatki” wprowadził tablice `ndarray`: tworzenie, typy elementów, indeksowanie i maski, widok a kopia, funkcje uniwersalne, rozgłaszanie, agregacje z osią i generator liczb losowych. Ten rozdział idzie dalej — do zadań, które w analizie danych pojawiają się codziennie, a w rozdziale 14 zmieściły się co najwyżej w jednym zdaniu: tablice o trzech i więcej osiach, kwantyle i histogramy, sortowanie tabel i wartości unikatowe, brakujące dane, układy równań i dopasowanie prostej, symulacje losowe oraz to, jak NumPy gospodaruje pamięcią i czasem.

Rozdział buduje na materiale „Python Notatki” — rozdziale 14 w całości, rozdziale 13 (pomiary czasu, Numba) i 15 (procesy) — oraz na rozdziale 1 tej części: przykłady są skryptami, ale każdy działa tak samo jako komórki notatnika. Wykresy pojawiają się w zakresie znanym z rozdziału 14; ich pełne omówienie to następny rozdział ścieżki. Wersje odniesienia: NumPy 2.5.3 i Matplotlib 3.11.2 na Pythonie 3.14.7.

---

## W tym rozdziale

1. [Tablice wielowymiarowe](tablice-wielowymiarowe.md) — osie i kształt, nowe osie i rozgłaszanie, agregacje wzdłuż wielu osi, łączenie i przestawianie, indeksowanie tablicami indeksów
2. [Statystyka i porządkowanie danych](statystyka-i-porzadkowanie.md) — kwantyle i histogram, sortowanie tabel, wartości unikatowe, warunki i przekształcenia, brakujące wartości
3. [Algebra liniowa i dopasowanie](algebra-liniowa.md) — układy równań, najmniejsze kwadraty, wektory własne, przekształcenia geometryczne, normy i odległości
4. [Losowość i symulacje](losowosc-i-symulacje.md) — rozkłady, ziarno i niezależne strumienie, Monte Carlo, błądzenie losowe, próbkowanie ponowne
5. [Wydajność i pamięć](wydajnosc-i-pamiec.md) — typ elementów a pamięć, operacje w miejscu, prawdziwa wektoryzacja, duże dane i `memmap`, typowe pułapki
