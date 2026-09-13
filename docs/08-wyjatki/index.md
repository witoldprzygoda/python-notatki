# 8. Wyjątki i zarządzanie zasobami

Błędy towarzyszą nam od pierwszych eksperymentów w konsoli: `ValueError` przy `int(input())`, `KeyError` i `IndexError` przy kontenerach, `RecursionError` przy rekurencji, `ModuleNotFoundError` i `AssertionError` przy modułach i testach. Dotąd każdy z nich czytaliśmy wyłącznie ze śladu wywołań, a program kończył się kodem wyjścia `1`. W tym rozdziale błąd staje się **obiektem**: wyjątkiem, który jedna część programu zgłasza, a inna przechwytuje i obsługuje. Poznajemy instrukcję `try` z klauzulami `except`, `else` i `finally`, instrukcję `raise` z łańcuchami wyjątków, hierarchię typów wyjątków oraz zasady stylu: kiedy sprawdzać warunek przed operacją, a kiedy próbować i obsługiwać błąd, czego unikać i jak testować, że funkcja odrzuca błędne dane.

Drugi wątek rozdziału to zasoby — pliki, blokady, pomiary czasu — które trzeba zwolnić niezależnie od tego, czy wystąpił błąd. Służy do tego instrukcja `with` i menedżery kontekstu, które nauczymy się pisać bez klas, dekoratorem z modułu `contextlib`. Trzeci wątek to warsztat diagnostyczny: systematyczne czytanie śladu wywołań, moduł `traceback`, debugger Visual Studio Code zapowiedziany w rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/konfiguracja.md) wraz z terminalowym pdb oraz moduł `logging`, który zastępuje `print()` w roli dziennika zdarzeń programu.

Rozdział domyka zapowiedzi z rozdziałów [6. Funkcje](../06-funkcje/index.md) — zwracanie `None` jako sygnału błędu było rozwiązaniem tymczasowym, a wartość z `return` w funkcji generatorowej trafia do wyjątku `StopIteration` — i [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/index.md): instrukcja `assert` i opcja `-O`, mechanizm `sys.exit()`, testy pytest rozszerzone o `pytest.raises()`. Narzędzia z tego rozdziału będą obecne w każdym dalszym, poczynając od rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/index.md), w którym program zaczyna czytać i zapisywać pliki.

---

## W tym rozdziale

1. [Obsługa wyjątków](obsluga-wyjatkow.md) — wyjątek jako obiekt, anatomia śladu wywołań w Pythonie 3.14, najczęstsze wyjątki, `try`/`except` z obiektem wyjątku, `else` i `finally`, walidacja danych wejściowych
2. [Zgłaszanie wyjątków](zglaszanie-wyjatkow.md) — `raise` i propagacja, hierarchia wyjątków, ponowne zgłoszenie, łańcuchy `from` i `from None`, notatki `add_note()`, `assert` a opcja `-O`
3. [Styl obsługi błędów i testy wyjątków](styl-i-testowanie.md) — LBYL a EAFP, zasięg bloku `try`, antywzorce, `pytest.raises()` z `match=`, grupy wyjątków i `except*` dla dociekliwych
4. [Instrukcja with i menedżery kontekstu](with-i-contextlib.md) — od `try`/`finally` do `with`, protokół menedżera kontekstu, `contextlib.contextmanager`; dla dociekliwych `suppress`, `nullcontext` i `ExitStack`
5. [Diagnostyka — ślad wywołań (traceback) i debugger](diagnostyka.md) — czytanie śladu, moduł `traceback`, debugger VSC z pułapkami i wykonaniem krokowym, `breakpoint()` i pdb
6. [Logowanie zamiast print](logging.md) — dziennik zdarzeń, `basicConfig()` i `getLogger(__name__)`, poziomy komunikatów, `exception()`, leniwe formatowanie
