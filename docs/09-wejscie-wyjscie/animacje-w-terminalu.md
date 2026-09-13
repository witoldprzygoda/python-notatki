# Animacje w terminalu

Ten podrozdział ma charakter uzupełniający: nie wprowadza pojęć potrzebnych dalej, a jego przykłady są ćwiczeniem z tego, co wiemy o `print()`, znakach sterujących i buforowaniu. Pokazujemy, jak w terminalu nadpisywać bieżący wiersz — wskaźnik postępu, „maszyna do pisania”, odbijająca się piłeczka — oraz jak przerysowywać wiele wierszy za pomocą sekwencji sterujących ANSI. Wyników tych programów nie da się oddać w książce w pełni, bo zmieniają się w czasie; każdy z nich warto uruchomić samodzielnie w Windows Terminal.

## Zasada: nadpisywanie wiersza

Wszystkie animacje w jednym wierszu opierają się na trzech elementach z poprzedniego podrozdziału: znak `\r` cofa kursor na początek wiersza, `end=""` powstrzymuje `print()` przed przejściem do nowego wiersza, a `flush=True` wymusza natychmiastowe przekazanie tekstu na ekran — bez tego strumień, buforowany wierszowo, przekazałby wszystkie klatki naraz na końcu. Czwartym elementem jest `time.sleep()`, które ustala tempo:

```python title="odliczanie.py"
import time

OPOZNIENIE = 0.2

for sekundy in range(5, 0, -1):
    print(f"\rstart za {sekundy} s", end="", flush=True)
    time.sleep(OPOZNIENIE)
print("\rstart!        ")
```

Program wypisuje w tym samym miejscu ekranu kolejno `start za 5 s`, `start za 4 s` i tak dalej, a na końcu `start!` — dopełnione spacjami, bo nowy napis jest krótszy od poprzedniego i bez dopełnienia końcówka `za 1 s` zostałaby widoczna. Stała `OPOZNIENIE` jest w przykładach celowo mała; w prawdziwym odliczaniu wynosiłaby `1`.

## Wskaźnik postępu i „maszyna do pisania”

**Wskaźnik obrotowy** (ang. *spinner*) to cztery znaki `|`, `/`, `-` i `\` wyświetlane po kolei w tym samym miejscu — wrażenie obrotu. Łańcuch `"|/-\\"` zawiera odwrotny ukośnik zapisany sekwencją ucieczki `\\`, a powielenie łańcucha ustala liczbę obrotów:

```python title="spinner.py"
import time

OPOZNIENIE = 0.1

for znak in "|/-\\" * 5:
    print(f"\r {znak} pracuję…", end="", flush=True)
    time.sleep(OPOZNIENIE)
print("\r gotowe.    ")
```

Wskaźnik informuje, że program działa, ale nie informuje, jaka część pracy pozostała. **Pasek postępu** (ang. *progress bar*) mówi to wprost; jego szerokość i procent obliczamy z numeru kroku, a formatowanie `{krok:3d}` z pierwszego podrozdziału utrzymuje liczbę w stałej szerokości, by napis nie zmieniał długości między klatkami:

```python title="pasek-postepu.py"
import time

SZEROKOSC = 30
OPOZNIENIE = 0.02

for krok in range(101):
    wypelnione = SZEROKOSC * krok // 100
    pasek = "#" * wypelnione + "-" * (SZEROKOSC - wypelnione)
    print(f"\r[{pasek}] {krok:3d}%", end="", flush=True)
    time.sleep(OPOZNIENIE)
print()
```

Ostatnia klatka wygląda tak:

```{ .text .no-copy }
[##############################] 100%
```

W programie, który wykonuje długie obliczenie, miejsce `time.sleep()` zajmuje jeden krok obliczenia, a `krok` jest numerem przetworzonego elementu. Odmienny efekt daje „maszyna do pisania”, która działa odwrotnie niż nadpisywanie: dopisuje po jednym znaku, a między znakami pokazuje kursor w postaci bloku `▓` (znak Unicode U+2593, dostępny przez `chr(0x2593)`), który zaraz potem znika pod następną literą dzięki znakowi `\b`:

```python title="maszyna.py"
import time

KURSOR = chr(0x2593)
OPOZNIENIE = 0.05
tekst = "Tekst pisany na maszynie."

for znak in tekst:
    print(znak + KURSOR + "\b", end="", flush=True)
    time.sleep(OPOZNIENIE)
print(" ")
```

Każde `print()` wypisuje literę i blok kursora, po czym `\b` cofa kursor terminala o jedną pozycję, na blok; następna litera go nadpisuje. Końcowe `print(" ")` zasłania blok po ostatniej literze i przechodzi do nowego wiersza.

## Odbijająca się piłeczka

Ruch w poziomie to nadpisywanie wiersza, w którym znak `O` jest poprzedzony rosnącą, a potem malejącą liczbą spacji. Kierunek zmienia się na brzegach, a spacje po znaku zacierają jego poprzednie położenie:

```python title="pileczka.py"
import time

SZEROKOSC = 30
OPOZNIENIE = 0.03

pozycja, kierunek = 0, 1
for _ in range(120):
    print("\r" + " " * pozycja + "O" + " " * (SZEROKOSC - pozycja), end="", flush=True)
    pozycja += kierunek
    if pozycja in (0, SZEROKOSC):
        kierunek = -kierunek
    time.sleep(OPOZNIENIE)
print()
```

Pętla ma ustaloną liczbę klatek; inna wersja kończy się po upływie zadanego czasu, mierzonego funkcją `time.perf_counter()` z rozdziału 8, którą można podstawić w miejsce licznika. Zmiana kierunku przez `kierunek = -kierunek` i sprawdzenie brzegów operatorem `in` na krotce to cała logika ruchu w tej animacji.

## Wiele wierszy — sekwencje sterujące ANSI

Znak `\r` cofa kursor tylko do początku bieżącego wiersza; do poprzednich wierszy nie sięga. Terminale rozumieją jednak **sekwencje sterujące ANSI** (ang. *ANSI escape sequences*) — łańcuchy zaczynające się od znaku o kodzie 27 (ESC; w łańcuchu zapisujemy go sekwencją ucieczki `\033` z kodem ósemkowym, równoważną `\x1b`) i nawiasu `[`, które przesuwają kursor, czyszczą ekran i zmieniają kolory. Windows Terminal i terminale uniksowe obsługują je bez dodatkowych ustawień. Najważniejsze z nich:

| Sekwencja | Działanie |
|---|---|
| `\033[2J` | czyści cały ekran |
| `\033[H` | ustawia kursor w lewym górnym rogu |
| `\033[nA`, `\033[nB` | przesuwa kursor o `n` wierszy w górę, w dół |
| `\033[F` | przesuwa kursor na początek poprzedniego wiersza |
| `\033[?25l`, `\033[?25h` | ukrywa i pokazuje kursor |
| `\033[31m`, `\033[0m` | włącza czerwony kolor tekstu, przywraca domyślny |

Piłeczka odbijająca się w pionie przerysowuje kilkanaście wierszy naraz: czyści ekran, wypisuje `pozycja` pustych wierszy i znak. Kursor jest na czas animacji ukryty, a klauzula `finally` z rozdziału 8 przywraca go nawet wtedy, gdy program przerwiemy klawiszami ++ctrl+c++:

```python title="pion.py"
import time

CZYSC = "\033[2J\033[H"
UKRYJ, POKAZ = "\033[?25l", "\033[?25h"
WYSOKOSC = 10
OPOZNIENIE = 0.05

pozycja, kierunek = 0, 1
print(UKRYJ, end="")
try:
    for _ in range(40):
        print(CZYSC + "\n" * pozycja + "O", end="", flush=True)
        pozycja += kierunek
        if pozycja in (0, WYSOKOSC):
            kierunek = -kierunek
        time.sleep(OPOZNIENIE)
finally:
    print(POKAZ)
```

Ten sam schemat — wyczyść, narysuj, odczekaj — rysuje figury zmieniające rozmiar. Pulsujący kwadrat składa się ze znaków bloków `█` (U+2588), `▀` (U+2580) i `▄` (U+2584):

```python title="kwadrat.py"
import time

PELNY, GORNY, DOLNY = chr(0x2588), chr(0x2580), chr(0x2584)
CZYSC = "\033[2J\033[H"
MAKS = 6
OPOZNIENIE = 0.1

rozmiar, kierunek = 1, 1
for _ in range(30):
    wiersze = [DOLNY * (2 * rozmiar + 2)]
    wiersze += [PELNY + " " * (2 * rozmiar) + PELNY] * rozmiar
    wiersze.append(GORNY * (2 * rozmiar + 2))
    print(CZYSC + "\n".join(wiersze), flush=True)
    rozmiar += kierunek
    if rozmiar in (1, MAKS):
        kierunek = -kierunek
    time.sleep(OPOZNIENIE)
```

Kwadrat rośnie od rozmiaru `1` do `MAKS` i maleje z powrotem; boki są dwukrotnie szersze niż wyższe, bo znaki w terminalu są mniej więcej dwa razy wyższe niż szersze. Zamiast czyścić cały ekran, można cofnąć kursor o tyle wierszy, ile zajmuje rysunek (`"\033[" + str(len(wiersze)) + "A"`) i rysować od nowa w tym samym miejscu, czyszcząc każdy wiersz sekwencją `\033[K` przed ponownym wypisaniem — obraz mniej migocze, a wcześniejsze wyjście programu pozostaje na ekranie. Zamiast sekwencji ANSI spotyka się polecenie powłoki `os.system("cls")` (`clear` poza Windows); sekwencja `\033[2J` robi to samo bez uruchamiania powłoki i bez zależności od systemu.

## Ograniczenia i zastosowania

Animacje działają wyłącznie w terminalu. Okno IDLE, panel OUTPUT w Visual Studio Code i przekierowanie do pliku nie interpretują `\r` ani sekwencji ANSI, lecz zapisują je jako znaki, a w starym oknie konsoli Windows (`conhost`) sekwencje ANSI mogą wymagać jednorazowego włączenia — najprościej przez wywołanie `os.system("")` na początku programu. Tekst wypisany w trakcie animacji przez inną część programu — na przykład ostrzeżenie na `stderr` — miesza się z klatkami, dlatego w programach z paskiem postępu komunikaty odkłada się do dziennika w pliku.

W praktyce z tego podrozdziału najczęściej przydaje się pasek postępu przy długich obliczeniach lub przetwarzaniu wielu plików; gotowe, dopracowane implementacje oferują pakiety zewnętrzne, jak `tqdm` (pasek postępu dla dowolnej pętli) czy `rich` (kolory, tabele, paski w jednym pakiecie). Zasada ich działania jest jednak dokładnie ta, którą tu pokazaliśmy: `\r`, `flush` i sekwencje sterujące. Wracamy teraz do głównego wątku rozdziału — do plików.
