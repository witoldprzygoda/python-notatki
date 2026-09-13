# 16. Warsztat programisty i dalsza droga

Program, który działa, to dopiero początek: kod trzeba utrzymywać, zmieniać i przekazywać innym. Ten rozdział zbiera narzędzia, które przy tym pomagają i które w poprzednich rozdziałach pojawiały się pojedynczo — testy, adnotacje typów, styl kodu — a dokłada ich automatyzację: te same sprawdzenia wykonywane przed każdym zapisem zmian i na serwerze po każdym wysłaniu kodu. Kończy go posłowie o tym, dokąd prowadzą dalsze ścieżki.

| Cel | Narzędzie | Podrozdział |
|---|---|---|
| sprawdzić, czy kod robi to, co powinien | pytest — fixture, parametryzacja, pokrycie | [Testowanie z pytest — techniki zaawansowane](testowanie.md) |
| wykryć błędy typów przed uruchomieniem | adnotacje typów i mypy | [Adnotacje typów w praktyce](typy-statyczne.md) |
| ujednolicić wygląd i wychwycić usterki | Ruff — linter i formater | [Styl i formatowanie kodu](styl-kodu.md) |
| uruchamiać sprawdzenia automatycznie | pre-commit i GitHub Actions | [Automatyzacja jakości — pre-commit i CI](automatyzacja-jakosci.md) |
| wybrać kierunek dalszej nauki | asyncio, WWW, dane, Python 3.15 | [Co dalej](co-dalej.md) |

Rozdział zakłada znajomość pytest z rozdziału 7, dekoratorów i generatorów z rozdziału 6, adnotacji z rozdziałów 3 i 6, klas danych i protokołów z rozdziału 12 oraz konfiguracji edytora z rozdziału 1. Podrozdział o automatyzacji zakłada też repozytorium Git, którego używamy w kursie do oddawania zadań; sam Git nie jest tematem książki. Wersje narzędzi podajemy według stanu z września 2026 roku — narzędzia zmieniają się szybciej niż język, więc przed instalacją warto sprawdzić aktualne wydania.

---

## W tym rozdziale

1. [Testowanie z pytest — techniki zaawansowane](testowanie.md) — fixture, parametryzacja, `conftest.py` i markery, wybór testów, pokrycie kodu, atrapy
2. [Adnotacje typów w praktyce](typy-statyczne.md) — typy złożone, aliasy i generyki, `TypedDict`, mypy i inne sprawdzacze typów
3. [Styl i formatowanie kodu](styl-kodu.md) — Zen Pythona i PEP 8 w praktyce, dokumenty PEP, Ruff, alternatywy
4. [Automatyzacja jakości — pre-commit i CI](automatyzacja-jakosci.md) — pre-commit, narzędzia w edytorze, GitHub Actions, typowe błędy
5. [Co dalej](co-dalej.md) — programowanie asynchroniczne, aplikacje WWW, dane i uczenie maszynowe, Python 3.15, ściągawka narzędzi, zasoby, posłowie

!!! note "Zamknięcie części I"
    Rozdział nie ma laboratorium — jego treść przydaje się w każdym projekcie zaliczeniowym. Jest ostatnim rozdziałem części I książki, poświęconej językowi; część II omawia biblioteki.
