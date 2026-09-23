# Projekt rozdziału 23 części „Python Zastosowania” — Projekt: narzędzie automatyzujące

Ostatni rozdział ścieżki Automatyzacja i całej części. Branch: `content/zastosowania-23` (z `dev` po rozdziale 22). Realizacja autonomiczna w ramach zbiorczego polecenia autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Projekt:** narzędzie `monitor-cen` — pobiera ceny produktów ze sklepu (strona testowa i lokalny serwer z rozdziału 21), zapisuje pomiary w bazie SQLite, porównuje kolejne pomiary (zmiany cen, produkty nowe i brakujące) i tworzy raport: arkusz Excel z historią, zmianami i wykresem oraz dokument Word z podsumowaniem (rozdział 22). Uruchamiane z wiersza poleceń z podpoleceniami `pobierz`, `raport` i `historia` (rozdziały 17 i 20), instalowane jako polecenie (`[project.scripts]`, pipx) i uruchamiane z harmonogramu zadań. Zmianę cen między pomiarami symuluje skrypt, który podmienia ceny w plikach HTML sklepu wzorcem z rozdziału 19.
2. **Zakres stron (3 + index):** założenia i architektura (wymagania, przepływ danych, układ pakietu, pliki pożyczone z rozdziału 21, `pyproject.toml`); moduły narzędzia (`historia.py` — SQLite, `analiza.py` — porównanie pomiarów, `raport.py` — Excel i Word, `cli.py` z podpoleceniami, `__main__.py`; przebieg: dwa pomiary z symulowaną zmianą i raport); testy i wdrożenie (pytest z fixture serwera i bazą w `tmp_path`, instalacja przez pipx, harmonogram zadań Windows `schtasks` i cron jako blok terminalowy bez uruchamiania, dziennik do pliku, lista kontrolna, zakończenie ścieżki i części). Poza zakresem: powiadomienia e-mail, interfejs okienkowy, baza inna niż SQLite.
3. **Biblioteki:** httpx 0.28.1, beautifulsoup4 4.15.0, lxml 6.1.3, openpyxl 3.1.5, python-docx 1.2.0, Pillow 12.3.0, pytest 9.1.1; `sqlite3` z biblioteki standardowej. Środowisko `venv-ch23` (suma 21 i 22).
4. **Dane:** strona testowa z rozdziału 21 (`zbuduj_sklep.py`, `sklep_serwer.py` — pożyczone, pokazane jako pliki do skopiowania), moduły `pobieranie.py` i `rekordy.py` z rozdziału 21 pożyczone do pakietu. Harness: pakiet `monitor/` w stagingu (bloki z `title="monitor/…"`), moduły w `--skip`, skrypty kontrolne uruchamiają narzędzie jako proces z połączonymi strumieniami; dziennik podaje ścieżki, nie porty.
5. **Domknięcia:** markery „projekcie narzędzia automatyzującego” w 20/narzedzie, 21/narzedzie, 22/raport → `23-projekt-automatyzacja/index.md`; status ścieżki Automatyzacja i całej części w `PLAN_ZASTOSOWANIA.md`, `docs/index.md`, `docs/zastosowania/index.md` („wszystkie cztery ścieżki ukończone”).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 |
|---|---|---|
| `index.md` | Wprowadzenie / „23. Projekt: narzędzie automatyzujące” | cel; wymagania; plik wymagań; ---; ## W tym rozdziale (3) |
| `architektura.md` | Założenia i architektura | Wymagania; Przepływ danych; Układ pakietu; Pliki z rozdziału 21; Konfiguracja pakietu (`pyproject.toml`) |
| `moduly.md` | Moduły narzędzia | Historia pomiarów (`monitor/historia.py`); Analiza zmian (`monitor/analiza.py`); Raport (`monitor/raport.py`); Wiersz poleceń (`monitor/cli.py`, `monitor/__main__.py`); Przebieg (`symuluj_zmiane.py`, `uzycie-monitor.py`) |
| `testy-i-wdrozenie.md` | Testy i wdrożenie | Testy (`tests/test_monitor.py`, pytest); Instalacja polecenia; Harmonogram zadań; Dziennik w pliku; Lista kontrolna; Zakończenie części |

## Blok nawigacji (`mkdocs.yml`, po rozdziale 22)

```yaml
      - 23. Projekt — narzędzie automatyzujące:
          - Wprowadzenie: zastosowania/23-projekt-automatyzacja/index.md
          - Założenia i architektura: zastosowania/23-projekt-automatyzacja/architektura.md
          - Moduły narzędzia: zastosowania/23-projekt-automatyzacja/moduly.md
          - Testy i wdrożenie: zastosowania/23-projekt-automatyzacja/testy-i-wdrozenie.md
```

## Listy kontrolne

- Przed commitem: staging z bloków + pliki pożyczone z rozdziału 21; `refresh_outputs.py`; `verify_page.py` dwa przebiegi; pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje.
- Po commicie: domknięcia w 20, 21, 22; status ścieżki i części; integracja do `dev`; pamięć.
