# 1. Instalacja i środowisko pracy

## Krótka historia i cechy języka

Twórcą języka Python jest **Guido van Rossum**, który rozpoczął nad nim pracę w 1989 roku w holenderskim centrum badawczym Centrum Wiskunde & Informatica; pierwsza publiczna wersja (0.9.0) ukazała się w 1991 roku. Nazwa języka pochodzi od brytyjskiej grupy komediowej Monty Python, nie od węża. Do najważniejszych dat w historii języka należą: wydanie Pythona 2.0 (2000), niekompatybilne z poprzednią linią wydanie Pythona 3.0 (2008) oraz zakończenie wsparcia dla linii 2.x (1 stycznia 2020). Współcześnie rozwijana jest wyłącznie linia 3.x — stanem odniesienia niniejszych notatek jest **Python 3.14**.

O popularności języka decyduje kilka cech:

- **czytelność** — składnia bliska pseudokodowi, bloki kodu wyznaczane wcięciami,
- **dynamiczne typowanie** oraz automatyczne zarządzanie pamięcią (szerzej w rozdziale [3. Nazwy i typy](../03-nazwy-typy/index.md)),
- **wieloparadygmatowość** — styl proceduralny, obiektowy i funkcyjny w jednym języku,
- **bogata biblioteka standardowa** („baterie w zestawie”) oraz ekosystem kilkuset tysięcy pakietów zewnętrznych w repozytorium PyPI (opis w podrozdziale [Pip — zarządzanie pakietami](pip.md)),
- **otwarta licencja** Python Software Foundation, dopuszczająca także zastosowania komercyjne.

## Interpreter i implementacje

Python należy do języków **interpretowanych**. W językach kompilowanych (np. C, C++) cały kod źródłowy jest przed uruchomieniem tłumaczony na kod maszynowy, a wynikiem jest samodzielny plik wykonywalny; błędy składniowe ujawniają się już na etapie kompilacji. W języku interpretowanym program uruchamia osobny program — **interpreter** — który tłumaczy i wykonuje kod dopiero w trakcie działania; nie powstaje plik wykonywalny, a część błędów ujawnia się dopiero podczas wykonania. Python jest przypadkiem pośrednim: kod jest najpierw kompilowany do pośredniego kodu bajtowego, a następnie wykonywany przez maszynę wirtualną.

Istnieją różne implementacje języka Python; w niniejszych notatkach używamy implementacji referencyjnej — **CPython**, napisanej w języku C. Warte odnotowania są również: **PyPy** — implementacja z kompilatorem JIT, w wielu zastosowaniach znacząco szybsza (z jej kodu wywodzi się nowa konsola interaktywna opisana w rozdziale [2. Konsola](../02-konsola/index.md)), **MicroPython** — wariant zoptymalizowany dla mikrokontrolerów, a także **Jython** (maszyna wirtualna Javy) i **IronPython** (platforma .NET).

!!! note "Dla dociekliwych — jak CPython wykonuje kod"
    Kod źródłowy jest najpierw przetwarzany na drzewo składniowe AST (ang. *Abstract
    Syntax Tree*, [docs.python.org/3/library/ast.html](https://docs.python.org/3/library/ast.html)),
    a następnie kompilowany do kodu bajtowego, zapisywanego w tymczasowych plikach
    `*.pyc` — można go podejrzeć za pomocą modułu [dis](https://docs.python.org/3/library/dis.html).
    Kolejne fragmenty kodu bajtowego są tworzone lub odczytywane z plików i przekazywane
    do wykonania maszynie wirtualnej Pythona (PVM, ang. *Python Virtual Machine*), która
    dokonuje ostatecznej konwersji na kod maszynowy i uruchamia go na konkretnym
    sprzęcie. Maszyna wirtualna stanowi ostatni etap interpretera Pythona.

Interpreter Pythona może zostać zainstalowany również przy okazji innych produktów, np. środowiska PyCharm czy popularnego pakietu Anaconda, a na jednym komputerze może współistnieć wiele wersji języka. Do ich instalowania i zarządzania nimi służy obecnie oficjalne narzędzie **Python Install Manager** wraz z poleceniem `py` (opis w podrozdziale [Instalacja Pythona](instalacja.md)); zastąpiło ono dawny program uruchomieniowy *py launcher*, instalowany wraz z klasycznym instalatorem. W projekcie można ponadto skonfigurować izolowane wirtualne środowisko pracy z wybraną wersją interpretera (opis w podrozdziale [Wirtualne środowisko venv](venv.md)) — różne środowiska IDE tworzą właśnie takie środowiska (venv), zawierające konkretny plik binarny interpretera Pythona.

Instrukcje instalacyjne w tym rozdziale dotyczą systemu **Windows**; przy poleceniach, których składnia różni się między systemami (np. aktywacja środowiska wirtualnego), podane są również warianty dla systemów Linux i macOS.

---

## W tym rozdziale

1. [Instalacja Pythona](instalacja.md) — Python Install Manager, instalacja interpreterów
2. [Ścieżki i utrzymanie interpreterów](sciezki-i-utrzymanie.md) — PATH i sys.path, aktualizacja i usuwanie
3. [Pip — zarządzanie pakietami](pip.md) — instalowanie bibliotek, PyPI, plik requirements.txt
4. [Wirtualne środowisko venv](venv.md) — izolowane środowiska projektów
5. [Konfigurowanie narzędzi](konfiguracja.md) — przygotowanie edytora i środowiska pracy
6. [Notebook](notebook.md) — Jupyter Notebook, edycja kodu w przeglądarce
7. [Google Colab](colab.md) — notebooki w chmurze, dostęp do GPU/TPU, praca zespołowa
8. [Python w przeglądarce](przegladarka.md) — serwisy umożliwiające naukę bez instalacji
9. [Narzędzia AI](ai-tools.md) — GitHub Copilot i asystenci AI w nauce programowania
