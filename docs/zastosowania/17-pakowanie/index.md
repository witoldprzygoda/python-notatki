# 17. Pakowanie i dystrybucja

Programy z poprzednich rozdziałów działają na komputerze, na którym powstały: w katalogu projektu, w jego środowisku wirtualnym, z modułami obok siebie. Odbiorca potrzebuje czegoś innego — biblioteki, którą zainstaluje jednym poleceniem `pip`, narzędzia wiersza poleceń dostępnego z każdego katalogu albo aplikacji okienkowej, która uruchamia się bez instalowania Pythona. Rozdział 7 „Python Notatki” wprowadził układ `src`, minimalny `pyproject.toml` i instalację edytowalną; ten rozdział prowadzi dalej: od pełnych metadanych i punktów wejścia, przez zbudowanie **pakietu dystrybucyjnego** (ang. *distribution package*) i jego publikację, po plik wykonywalny dla użytkownika końcowego.

Przykładem jest menedżer kontaktów z rozdziału 16: jego logika trafia do pakietu `kontakty` z poleceniem `kontakty-csv` do sprawdzania i przeszukiwania plików oraz oknem `kontakty` z listą kontaktów. Kolejne strony budują pakiet i instalują go edytowalnie, tworzą z niego archiwum źródłowe i koło (ang. *wheel*), omawiają publikację i instalację u odbiorcy, porządkują zależności i wersje, a na koniec pakują okno w plik `.exe` i narzędzie w archiwum `.pyz`.

Wersje w chwili pisania: build 1.6.1, Hatchling 1.32.4, Twine 7.0.0, pipx 1.17.5, PyInstaller 6.22.3, packaging 26.3; Python 3.14.7. Żaden z tych pakietów nie jest zależnością budowanego projektu w czasie działania — to narzędzia pracy, instalowane w środowisku programisty; Hatchling pojawia się w `pyproject.toml` tylko jako backend budowania, a pytest jako zależność opcjonalna grupy `test`. Rozdział buduje na rozdziałach 1 (pip, środowiska wirtualne, plik wymagań), 7 (struktura projektu), 9 (pliki) i 16 (pytest, `pyproject.toml` narzędzi) części „Python Notatki” oraz na rozdziale 16 tej części. Plik wymagań narzędzi rozdziału:

```text title="requirements.txt"
pytest==9.1.1
build==1.6.1
hatchling==1.32.4
twine==7.0.0
pipx==1.17.5
pyinstaller==6.22.3
packaging==26.3
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Pakiet do instalacji](pakiet.md) — od projektu do pakietu, kod pakietu, instalacja edytowalna i polecenia, testy pakietu, metadane z wnętrza
2. [Budowanie i publikacja](budowanie.md) — budowanie, zawartość koła, instalacja z pliku, kontrola i publikacja, narzędzia z pipx
3. [Zależności i wersje](zaleznosci.md) — specyfikatory wersji, zależności pakietu a plik wymagań, zależności opcjonalne, wersja w jednym miejscu
4. [Aplikacja dla użytkownika](aplikacja-dla-uzytkownika.md) — skrypt uruchamiający, PyInstaller, archiwum zipapp, co dostarczamy komu, lista kontrolna
