# Pierwszy skrypt

Konsola interaktywna nadaje się do eksperymentów, ale programy zapisuje się w plikach z rozszerzeniem `.py`, nazywanych **skryptami**. Niniejszy podrozdział opisuje uruchamianie kodu z pliku oraz dwa elementy składni, które przy kodzie wieloliniowym stają się istotne: wcięcia i komentarze.

## Uruchomienie skryptu

W dowolnym edytorze (może być systemowy Notatnik, docelowo — Visual Studio Code, opisany w podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md)) tworzymy w katalogu roboczym plik `hello.py`:

```python title="hello.py"
imie = input("Podaj imie: ")
print("Witaj,", imie)
print("Liczba liter imienia:", len(imie))
```

Skrypt uruchamiamy w terminalu, przekazując interpreterowi nazwę pliku:

```powershell title="Terminal"
python hello.py
```

```{ .text .no-copy }
Podaj imie: Anna
Witaj, Anna
Liczba liter imienia: 4
```

Konkretną wersję interpretera można wskazać składnią `py -V:<TAG>` (opis w podrozdziale [Instalacja Pythona](../01-instalacja/instalacja.md)):

```powershell title="Terminal"
py -V:3.14 hello.py
```

!!! note "Różnica między konsolą a skryptem"
    W konsoli interaktywnej wartość każdego wpisanego wyrażenia jest automatycznie
    wypisywana na ekran — dlatego samo `2 + 2` pokazuje wynik. W skrypcie tak nie
    jest: linia `2 + 2` zostanie obliczona i porzucona bez śladu. Wszystko, co ma
    zostać wypisane, musi przejść przez funkcję `print`.

## Formatowanie kodu — wcięcia

Bloki kodu w Pythonie wyznacza się za pomocą `:` (dwukropka) oraz odpowiednich wcięć. Standard **PEP 8** zaleca wcięcia o szerokości **4 spacji** na każdy poziom. W praktyce najwygodniej skonfigurować edytor tak, aby klawisz ++tab++ wstawiał 4 spacje — Visual Studio Code robi tak w plikach Pythona domyślnie.

!!! tip "Tab size w Visual Studio Code"
    W Visual Studio Code (skrót ++ctrl+comma++) po wpisaniu „tab size” dostępne
    jest pole, w którym ustawiamy odpowiednią wartość.

**Nie można mieszać rodzaju wcięć.**

Nawet wizualnie dobrze sformatowany kod, jeżeli ma pomieszane tabulacje i spacje, może być błędny. Aby tego doświadczyć, trzeba najpierw zapisać plik, w którym jedno wcięcie będzie rzeczywiście wypełnione znakiem tabulacji, a drugie zbudowane ze spacji. Taką sytuację można uzyskać np. pisząc fragment kodu w prostym edytorze typu Notatnik (Windows) i jedno wcięcie tworząc klawiszem ++tab++, a drugie wstawiając 8 spacji. Optycznie wyglądają identycznie, jednak po skopiowaniu takiego kodu do interpretera (np. w oknie IDLE) pojawi się błąd niespójności znaków użytych we wcięciach (`TabError`).

## Komentarze

Komentarz znajduje się na prawo od znaku `#`. Komentarz zapisany w wielu liniach osiąga się przez stworzenie wielolinijkowego łańcucha znakowego, bez jego przypisania. Tworzy się go za pomocą trzykrotnie powtórzonego pojedynczego `'''` lub podwójnego `"""` cudzysłowu:

```{ .python .no-copy }
"""
To jest komentarz
zapisany w wielu liniach
"""
```

Łańcuch tego rodzaju umieszczony na początku modułu lub funkcji pełni szczególną rolę dokumentacyjną — jest to **docstring** (ang. *documentation string*), wspomniany w podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md); szersze omówienie zawiera rozdział [6. Funkcje](../06-funkcje/definiowanie-funkcji.md#docstring-i-funkcja-help).

!!! tip "Komentowanie wielu linii w Visual Studio Code"
    Po zaznaczeniu kilku linii kodu skrótem klawiszowym ++ctrl+k++ ++ctrl+c++
    (lub prościej ++ctrl+slash++) dodajemy znak komentarza `#`,
    a skrótem ++ctrl+k++ ++ctrl+u++ go usuwamy — w wielu liniach jednocześnie.

## Python bez wchodzenia do konsoli: opcje -c, -m oraz -i

Interpreter przyjmuje opcje wiersza poleceń, dzięki którym krótkie zadania wykonamy bez otwierania konsoli interaktywnej.

Opcja **`-c`** wykonuje przekazany kod i kończy działanie — „kalkulator” mieści się wtedy w jednym poleceniu terminala:

```powershell title="Terminal"
python -c "print(2 ** 10)"
```

Kilka instrukcji rozdzielamy średnikami:

```powershell title="Terminal"
python -c "import math; print(math.pi * 2)"
```

Tę formę stosowaliśmy już w podrozdziałach [Instalacja Pythona](../01-instalacja/instalacja.md) oraz [Ścieżki i utrzymanie interpreterów](../01-instalacja/sciezki-i-utrzymanie.md), odczytując `sys.executable` czy `sys.path`. Uwaga na cudzysłowy: całość kodu najbezpieczniej ująć w cudzysłowy podwójne, a łańcuchy wewnątrz kodu zapisywać w pojedynczych, np. `python -c "print('hello')"`.

Opcja **`-m`** uruchamia wskazany moduł jako program — spotkaliśmy ją już przy `python -m pip` czy `python -m venv`. Moduły standardowej biblioteki potrafią zaskoczyć, np.:

```powershell title="Terminal"
python -m calendar 2026
```

wypisze w terminalu kalendarz na cały rok.

Opcja **`-i`** wykonuje wskazany plik, a następnie — zamiast zakończyć działanie — pozostawia nas w konsoli interaktywnej z dostępem do wszystkich utworzonych w nim zmiennych i funkcji:

```powershell title="Terminal"
python -i hello.py
```

Jest to bardzo wygodny sposób eksperymentowania z własnym kodem. Pełny wykaz opcji wypisze `python --help`, a ich omówienie zawiera dokumentacja: [docs.python.org/3/using/cmdline.html](https://docs.python.org/3/using/cmdline.html).
