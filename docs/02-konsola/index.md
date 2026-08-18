# 2. Konsola

Działania w interpreterze Pythona można prowadzić w dowolnym terminalu, zależnie od systemu operacyjnego. Przede wszystkim program interpretera powinien być dostępny z poziomu terminala — sposoby weryfikacji (odczyt `sys.executable`, polecenia `where.exe python`, `Get-Command python`) opisują podrozdziały [Instalacja Pythona](../01-instalacja/instalacja.md) oraz [Ścieżki i utrzymanie interpreterów](../01-instalacja/sciezki-i-utrzymanie.md).

Python można uruchomić w oknie **cmd** Windows (niewygodne), w **PowerShell** — najlepiej w aplikacji **Windows Terminal**, będącej obecnie domyślnym hostem terminala w Windows 11 — albo np. w programie **IDLE**, dołączonym do standardowej biblioteki (uruchomienie poleceniem `py -m idlelib`).

!!! tip "Skróty klawiszowe w IDLE"
    IDLE ma niekoniecznie intuicyjny zestaw skrótów klawiszowych, który można
    przedefiniować lub się ich nauczyć. Przykładowo, poprzednia (kolejna)
    wykonana instrukcja to ++alt+p++ (++alt+n++).

## Wejście do konsoli i wyjście z niej

Do konsoli wchodzimy poleceniem `python` (lub `py`) — pojawi się znak zachęty `>>>`. Każda wprowadzona linia jest natychmiast wykonywana, a wynik wypisywany na ekran. Konsolę opuszczamy poleceniem `exit` (bez nawiasów; w starszych wersjach `exit()`) albo skrótem ++ctrl+z++ i ++enter++. Warto wykonać kilka poleceń, aby zapoznać się z tym trybem pracy — praktyczne eksperymenty zawiera podrozdział [Konsola w praktyce](konsola-w-praktyce.md).

## Nowa konsola interaktywna

Konsola interaktywna (**REPL**, ang. *read-eval-print loop* — pętla „czytaj, wykonaj, wypisz”) została w ostatnich wydaniach Pythona gruntownie unowocześniona. Od wersji 3.13 domyślna powłoka opiera się na kodzie projektu PyPy i oferuje:

- **edycję wieloliniową** — bloki kodu (np. funkcje, pętle) można poprawiać w całości, poruszając się strzałkami, zamiast wpisywać je od nowa,
- **kolorowe znaki zachęty i komunikaty błędów**,
- polecenia `help`, `exit` oraz `quit` działające **bez nawiasów**,
- przeglądanie pomocy klawiszem ++f1++, historii poleceń klawiszem ++f2++ oraz **tryb wklejania** większych fragmentów kodu pod klawiszem ++f3++ (ponowne ++f3++ wraca do zwykłego trybu).

Python 3.14 dodał do tego **kolorowanie składni na żywo** — słowa kluczowe, łańcuchy znaków, liczby i komentarze otrzymują własne kolory już podczas pisania — oraz **autouzupełnianie nazw modułów** klawiszem ++tab++ w instrukcjach `import`.

<!-- TODO: screenshot — nowy REPL z kolorowaniem składni (kolorów nie odda blok tekstowy) -->

!!! note "Powrót do klasycznej powłoki"
    Nową powłokę można wyłączyć, ustawiając zmienną środowiskową
    `PYTHON_BASIC_REPL`. Samo kolorowanie wyłączają zmienne `PYTHON_COLORS=0`
    lub `NO_COLOR=1`.

---

## W tym rozdziale

1. [Konsola w praktyce](konsola-w-praktyce.md) — kalkulator, funkcje print oraz input, moduł math, pomoc wbudowana
2. [Pierwszy skrypt](pierwszy-skrypt.md) — uruchamianie kodu z pliku, wcięcia, komentarze, opcje wiersza poleceń
