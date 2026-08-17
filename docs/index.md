# 1. Instalacja i środowisko pracy

Istnieją różne implementacje języka Python; w niniejszych notatkach używamy implementacji klasycznej — **CPython**, napisanej w języku C. Kod źródłowy jest najpierw przetwarzany na drzewo składniowe AST (ang. *Abstract Syntax Tree*, [docs.python.org/3/library/ast.html](https://docs.python.org/3/library/ast.html)), a następnie kompilowany do kodu bajtowego, zapisywanego w tymczasowych plikach `*.pyc` — można go podejrzeć za pomocą modułu [dis](https://docs.python.org/3/library/dis.html). Kolejne fragmenty kodu bajtowego są tworzone lub odczytywane z plików i przekazywane do wykonania maszynie wirtualnej Pythona (PVM, ang. *Python Virtual Machine*), która dokonuje ostatecznej konwersji na kod maszynowy i uruchamia go na konkretnym sprzęcie. Maszyna wirtualna stanowi ostatni etap interpretera Pythona.

Interpreter Pythona może zostać zainstalowany również przy okazji innych produktów, np. środowiska PyCharm czy popularnego pakietu Anaconda, a na jednym komputerze może współistnieć wiele wersji języka. Do ich instalowania i zarządzania nimi służy obecnie oficjalne narzędzie **Python Install Manager** wraz z poleceniem `py` (opis w podrozdziale [Instalacja klasyczna](instalacja-klasyczna.md)); zastąpiło ono dawny program uruchomieniowy *py launcher*, instalowany wraz z klasycznym instalatorem. W projekcie można ponadto skonfigurować izolowane wirtualne środowisko pracy z wybraną wersją interpretera (opis w podrozdziale [Wirtualne środowisko venv](venv.md)) — różne środowiska IDE tworzą właśnie takie środowiska (venv), zawierające konkretny plik binarny interpretera Pythona.

---

## W tym rozdziale

1. [Instalacja klasyczna](instalacja-klasyczna.md) — Python Install Manager, instalacja interpreterów, PATH i sys.path
2. [Pip — zarządzanie pakietami](pip.md) — instalowanie bibliotek, PyPI, plik requirements.txt
3. [Wirtualne środowisko venv](venv.md) — izolowane środowiska projektów
4. [Konfigurowanie narzędzi](konfiguracja.md) — przygotowanie edytora i środowiska pracy
5. [Notebook](notebook.md) — Jupyter Notebook, edycja kodu w przeglądarce
6. [Google Colab](colab.md) — notebooki w chmurze, dostęp do GPU/TPU, praca zespołowa
7. [Python w przeglądarce](przegladarka.md) — serwisy umożliwiające naukę bez instalacji
8. [Narzędzia AI](ai-tools.md) — GitHub Copilot i asystenci AI w nauce programowania
