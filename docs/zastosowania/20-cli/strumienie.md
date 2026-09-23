# Strumienie, kody wyjścia i dziennik

Narzędzia terminala współpracują przez trzy strumienie z rozdziału 9 „Python Notatki”: czytają `stdin`, piszą wynik na `stdout`, a komunikaty na `stderr`, i kończą się kodem, który następne polecenie może sprawdzić. Filtr, który tego przestrzega, działa w **potoku** (ang. *pipe*) z dowolnym innym narzędziem.

## Filtr tekstu

```python title="licznik.py"
"""licznik — liczy wiersze, słowa i dopasowania wzorca w plikach albo na wejściu standardowym."""

import argparse
import errno
import os
import re
import sys
from pathlib import Path


def policz(tekst, wzorzec=None):
    wiersze = tekst.splitlines()
    dopasowania = sum(len(wzorzec.findall(wiersz)) for wiersz in wiersze) if wzorzec else None
    return len(wiersze), sum(len(wiersz.split()) for wiersz in wiersze), dopasowania


def main(argv=None):
    parser = argparse.ArgumentParser(prog="licznik", description="Liczy wiersze, słowa i dopasowania wzorca.")
    parser.add_argument("pliki", nargs="*", help="pliki do policzenia; brak albo - oznacza wejście standardowe")
    parser.add_argument("-e", "--wzorzec", help="wyrażenie regularne do policzenia")
    parser.add_argument("-i", "--ignoruj-wielkosc", action="store_true", help="wzorzec bez rozróżniania wielkości liter")
    argumenty = parser.parse_args(argv)
    try:
        wzorzec = re.compile(argumenty.wzorzec, re.IGNORECASE if argumenty.ignoruj_wielkosc else 0) if argumenty.wzorzec else None
    except re.PatternError as blad:
        parser.error(f"błędny wzorzec: {blad}")
    kod = 0
    try:
        for nazwa in argumenty.pliki or ["-"]:
            if nazwa == "-":
                tekst = sys.stdin.read()
            else:
                try:
                    tekst = Path(nazwa).read_text(encoding="utf-8")
                except OSError as blad:
                    print(f"licznik: {nazwa}: {blad.strerror}", file=sys.stderr)
                    kod = 1
                    continue
            wiersze, slowa, dopasowania = policz(tekst, wzorzec)
            print(f"{wiersze:>6} {slowa:>6}" + (f" {dopasowania:>6}" if wzorzec else "") + f"  {nazwa}")
        sys.stdout.flush()
    except KeyboardInterrupt:
        print("licznik: przerwano", file=sys.stderr)
        return 130
    except OSError as blad:
        if blad.errno not in (errno.EPIPE, errno.EINVAL):
            raise
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    return kod


if __name__ == "__main__":
    sys.exit(main())
```

Filtr przyjmuje listę plików (`nargs="*"` — zero lub więcej), a bez plików albo dla nazwy `-` czyta `sys.stdin` — konwencja narzędzi systemowych, dzięki której `licznik` działa zarówno z plikami, jak i na końcu potoku. Wynik trafia na `stdout` w stałym układzie kolumn, komunikaty o błędach na `stderr` z nazwą programu na początku, a błąd jednego pliku nie przerywa pracy — narzędzie liczy pozostałe i kończy kodem `1`. ++ctrl+c++ w terminalu zgłasza `KeyboardInterrupt`; przechwycony daje krótki komunikat i kod `130` (128 + numer sygnału przerwania, jak w powłokach uniksowych) zamiast śladu wywołań. Gdy odbiorca potoku przestanie czytać (`licznik *.txt | head` przy wyniku dłuższym niż bufor potoku), zapis na `stdout` zgłasza `BrokenPipeError`, a na Windows `OSError` z kodem `EINVAL` — stąd warunek na `errno`; nie jest to błąd filtra, więc kończymy kodem `0`. Jawny `flush()` po pętli zapisuje ostatnią porcję wyniku jeszcze w bloku `try`, a przed powrotem przekierowujemy `stdout` do `os.devnull`, bo interpreter przy zakończeniu programu opróżnia bufor jeszcze raz, jak zaleca dokumentacja modułu `signal` — inaczej proces wypisałby komunikat „Exception ignored while flushing sys.stdout” i zakończył się kodem `120`, a nie `0`. Wzorzec z rozdziału 19 pozwala liczyć trafienia; wzorzec błędny to błąd użycia, więc `PatternError` zamieniamy przez `parser.error()` na komunikat ze sposobem użycia i kod `2` — tak samo `argparse` traktuje nieznaną opcję. Funkcja `policz()` nie zna strumieni, więc testuje się ją bezpośrednio.

## Potoki i kody wyjścia

```python title="uzycie-licznik.py"
import os
import subprocess
import sys
from pathlib import Path

Path("wiersz.txt").write_text("Litwo! Ojczyzno moja! ty jesteś jak zdrowie;\nIle cię trzeba cenić, ten tylko się dowie,\nKto cię stracił.\n", encoding="utf-8")
Path("lista.txt").write_text("jabłka\ngruszki\nśliwki\n", encoding="utf-8")
srodowisko = {**os.environ, "PYTHONUTF8": "1"}


def uruchom(*argumenty, wejscie=None):
    proces = subprocess.run([sys.executable, "licznik.py", *argumenty], input=wejscie, capture_output=True, text=True, encoding="utf-8", env=srodowisko)
    print(f"[kod {proces.returncode}] stdout: {proces.stdout!r}" + (f" stderr: {proces.stderr.strip()!r}" if proces.stderr else ""))


uruchom("wiersz.txt", "lista.txt")
uruchom("-e", r"ci[ęe]", "-i", "wiersz.txt")
uruchom(wejscie="pierwszy wiersz\ndrugi wiersz\n")
uruchom("-", "lista.txt", wejscie="a b c\n")
uruchom("brak.txt", "lista.txt")
uruchom("--wzorzec", "(", "lista.txt")
```

```{ .text .no-copy }
[kod 0] stdout: '     3     18  wiersz.txt\n     3      3  lista.txt\n'
[kod 0] stdout: '     3     18      2  wiersz.txt\n'
[kod 0] stdout: '     2      4  -\n'
[kod 0] stdout: '     1      3  -\n     3      3  lista.txt\n'
[kod 1] stdout: '     3      3  lista.txt\n' stderr: 'licznik: brak.txt: No such file or directory'
[kod 2] stdout: '' stderr: 'usage: licznik [-h] [-e WZORZEC] [-i] [pliki ...]\nlicznik: error: błędny wzorzec: missing ), unterminated subpattern at position 0'
```

Skrypt kontrolny uruchamia filtr jako proces potomny — jak zrobi to powłoka — z tekstem podanym na `stdin` przez `input=` albo z plikami, i pokazuje kod wyjścia oraz oba strumienie wyjściowe osobno. Brakujący plik daje komunikat na `stderr`, wynik dla pozostałych plików na `stdout` i kod `1`, więc skrypt powłoki może zareagować, a potok dostał wszystko, co dało się policzyć. Błędny wzorzec daje sposób użycia, komunikat i kod `2`, bez śladu wywołań. W terminalu ten sam filtr uruchamia się w potoku:

```powershell title="Terminal"
Get-Content wiersz.txt | python -X utf8 licznik.py -e "ci[ęe]"
python licznik.py *.txt; echo "kod: $LASTEXITCODE"
```

Kod wyjścia poprzedniego polecenia jest w PowerShell w `$LASTEXITCODE`, w powłokach uniksowych w `$?`. Drugie polecenie kończy się w PowerShell komunikatem `licznik: *.txt: Invalid argument` i kodem `1`: gwiazdkę w nazwach plików rozwija powłoka uniksowa, ale nie PowerShell ani `cmd` — narzędzie dla Windows, które ma przyjmować `*.txt`, rozwija wzorzec samo przez `Path().glob()`.

## Dziennik na `stderr`

Wynik i komunikaty muszą trafiać do osobnych strumieni: gdy wynik jest w potoku albo przekierowany do pliku, komunikat wpisany przez `print()` zniekształciłby dane. `logging.basicConfig(stream=sys.stderr, level=…)` z narzędzia `porzadek` daje komunikaty o przebiegu, które użytkownik widzi w terminalu, a potok nie — z poziomem ustawianym opcjami: `-q` tylko błędy, domyślnie ostrzeżenia, `-v` informacje, `-vv` diagnostyka. Format komunikatu w narzędziu jest krótki (`poziom: treść`), bez daty, bo dziennik czyta człowiek przy terminalu; przy zapisie do pliku `-vv` z pełnym formatem z rozdziału 8 „Python Notatki” daje materiał do diagnozy. Pasek postępu i inne animacje z rozdziału 9 też należą do `stderr` — i tylko wtedy, gdy `sys.stderr.isatty()` mówi, że po drugiej stronie jest terminal, nie plik.

## Kodowanie na Windows

Terminal Windows wyświetla polskie znaki poprawnie, ale gdy wyjście programu jest przechwycone — przez potok, przekierowanie do pliku, `subprocess` — Python 3.14 użyje strony kodowej systemu (`cp1252` na tym komputerze; dopiero wersja 3.15 ma domyślnie włączać tryb UTF-8 według PEP 686): `print("zażółć")` zgłosi `UnicodeEncodeError`, a tekst z `sys.stdin` — na przykład z `Get-Content` w potoku wyżej, który PowerShell 7 przekazuje w UTF-8 — zostanie odczytany z przekłamanymi znakami, więc wzorzec `ci[ęe]` nie znajdzie żadnego dopasowania. Trzy rozwiązania: zmienna `PYTHONUTF8=1` w środowisku (przechodzi na procesy potomne; skrypt kontrolny wyżej ustawia ją dla nich jawnie), opcja `python -X utf8` — jak w potoku wyżej, ale tylko dla tego jednego procesu — albo w samym narzędziu `reconfigure(encoding="utf-8")` na `sys.stdin`, `sys.stdout` i `sys.stderr` na początku `main()`, przed pierwszym odczytem; `stderr` bez tego nie zgłasza błędu, lecz wypisuje polskie litery jako sekwencje `\u0142`. Pliki czytamy zawsze z jawnym `encoding="utf-8"`, jak w rozdziale 9 „Python Notatki”; pliki od użytkowników Excela mogą wymagać `utf-8-sig`.
