# Projekt rozdziału 19 części „Python Zastosowania” — Wyrażenia regularne

Pierwszy rozdział ścieżki Automatyzacja. Branch: `content/zastosowania-19` (z `dev` po `0cf592d`). Realizacja autonomiczna w ramach zbiorczego polecenia autora z 23 IX 2026 (rozdziały 19–23 bez przerwy).

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** składnia wzorców (`search`/`match`/`fullmatch`, obiekt `Match`, surowe łańcuchy; metaznaki, klasy znaków, kwantyfikatory zachłanne i leniwe, kotwice, alternatywa, ucieczki; grupy zwykłe, nazwane, nieprzechwytujące i odwołania wsteczne; flagi `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII` i różnica `\w` dla polskich liter); wyszukiwanie, dzielenie i zamiana (`findall`/`finditer`, `split` z grupą, `sub`/`subn` z odwołaniami i funkcją, `compile` i metody wzorca, pamięć podręczna, `escape`, `PatternError` z pozycją); wzorce w praktyce (dziennik uvicorn z rozdziału 15 → wzorzec `VERBOSE` z grupami nazwanymi i `Counter`; wyciąganie dat, telefonów i adresów z tekstu z normalizacją; zmiana nazw plików `pathlib` + `sub`; dokument Markdown — nagłówki i odsyłacze z `MULTILINE`); pułapki, wydajność i testy (nawroty katastrofalne `(a+)+b` z pomiarem, kwantyfikatory dzierżawcze `a++` i grupy atomowe `(?>…)` z Pythona 3.11; walidacja przez `fullmatch` — kod pocztowy, NIP z sumą kontrolną w Pythonie, e-mail praktyczny; testy wzorców pytest z `parametrize`; kiedy nie używać wyrażeń — metody `str`, parsery `csv`/`json`/HTML; moduł `regex` jako wzmianka; lista kontrolna). Cztery strony + index. Poza zakresem: lookahead/lookbehind poza jednym przykładem, `re.Scanner`, składnia Perla, `regex` w praktyce, `re.DEBUG`.
2. **Biblioteki:** tylko biblioteka standardowa (`re` w Pythonie 3.14.7; `re.PatternError` od 3.13 jako nazwa `re.error`; kwantyfikatory dzierżawcze i grupy atomowe od 3.11); pytest 9.1.1 do testów wzorców. Plik wymagań: `pytest==9.1.1`.
3. **Dane:** blok pliku `dziennik.log` (wiersze w formacie dziennika uvicorn z rozdziału 15, z wierszami nieżądań), teksty w skryptach; pliki do zmiany nazw tworzone przez skrypt w katalogu roboczym. Harness: `verify_page.py` z `--data=` na staging (plik dziennika z bloku), maska czasu `\d+\.\d{3} s` dla pomiarów nawrotów.
4. **Fakty sprawdzone 23 IX 2026 (Python 3.14.7):** `\w` obejmuje polskie litery (Unicode domyślnie), `re.ASCII` ogranicza do ASCII (`zażółć` → `za`); `re.PatternError` istnieje i jest tą samą klasą co `re.error`, ma atrybut `pos`; `(a+)+b` na 22/24/26 znakach `a`: 0,11 / 0,46 / 1,83 s, `(a++)+b` — 0,0001 s; `(?>a+)b` działa; `re.split` z grupą przechwytującą zwraca separatory; `finditer(r"a*", "baa")` daje także dopasowania puste `(0,0)`, `(3,3)`; `re.sub(r"a*", "-", "baa")` → `-b--`; `re.escape("cena: 3.50 zł (brutto)?")` ucieka spacje, kropkę, nawiasy i pytajnik; `re.compile` zwraca obiekt z `pattern`, `flags` (32 = UNICODE), `groups`, `groupindex`; `re.M`/`re.S`/`re.X` skróty flag; `(?i)` w treści wzorca.
5. **Terminy:** „wyrażenie regularne” (ang. *regular expression*, regex), „wzorzec” (ang. *pattern*), „dopasowanie” (ang. *match*), „metaznak”, „klasa znaków” (ang. *character class*), „kwantyfikator” (ang. *quantifier*) zachłanny/leniwy (ang. *greedy*/*lazy*), „kotwica” (ang. *anchor*), „grupa przechwytująca” (ang. *capturing group*), „odwołanie wsteczne” (ang. *backreference*), „nawroty” (ang. *backtracking*), „kwantyfikator dzierżawczy” (ang. *possessive quantifier*), „grupa atomowa” (ang. *atomic group*), „surowy łańcuch” (ang. *raw string*).
6. Odsyłacze wstecz: „Python Notatki” 3 (łańcuchy, surowe łańcuchy), 4 (metody `str`), 7 (tabela biblioteki standardowej — wiersz `re` do zaktualizowania), 9 (pliki, `pathlib`, `csv`), 16 (pytest, `parametrize`); „Python Zastosowania” 4 (pandas `str.extract` — wzmianka), 15 (dziennik uvicorn). Zapowiedzi: 20 (CLI), 21 (HTML — parser zamiast wyrażeń) — `TODO`.
7. Domknięcia: marker „wyrażeniach regularnych” w 18/dostawa → `19-re/index.md`; „Python Notatki” 7/biblioteka-standardowa: wiersz tabeli `re` „poza zakresem książki” → odsyłacz do rozdziału 19, admonition „książka jej nie omawia” → omawia ją rozdział 19 „Python Zastosowania”.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „19. Wyrażenia regularne” | cel; biblioteka; plik wymagań; ---; ## W tym rozdziale (4) |
| `skladnia.md` | Składnia wzorców | Pierwsze dopasowanie (`pierwsze.py`); Metaznaki, klasy i kwantyfikatory (`metaznaki.py`, tabela); Zachłanność (`zachlannosc.py`); Grupy (`grupy.py`); Flagi (`flagi.py`) |
| `operacje.md` | Wyszukiwanie, dzielenie i zamiana | Wszystkie dopasowania (`wszystkie.py`); Dzielenie (`dzielenie.py`); Zamiana (`zamiana.py`); Wzorce skompilowane i błędy (`kompilacja.py`) |
| `praktyka.md` | Wzorce w praktyce | Dziennik serwera (`dziennik.log`, `dziennik.py`); Dane z tekstu (`z-tekstu.py`); Nazwy plików (`pliki.py`); Dokument wielowierszowy (`markdown.py`) |
| `pulapki.md` | Pułapki, wydajność i testy | Nawroty (`nawroty.py`); Walidacja (`walidacja.py`); Testy wzorców (`test_wzorce.py`, pytest); Kiedy nie wyrażenia; Lista kontrolna; Dalej (TODO 20, 21) |

Szacunek: 650–800 linii; bez wykresów i zrzutów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 18)

```yaml
      - 19. Wyrażenia regularne:
          - Wprowadzenie: zastosowania/19-re/index.md
          - Składnia wzorców: zastosowania/19-re/skladnia.md
          - Wyszukiwanie, dzielenie i zamiana: zastosowania/19-re/operacje.md
          - Wzorce w praktyce: zastosowania/19-re/praktyka.md
          - Pułapki, wydajność i testy: zastosowania/19-re/pulapki.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `pulapki.md` | narzędzia wiersza poleceń; pobieranie i parsowanie stron | rozdziały 20, 21 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/18-projekt-aplikacja/dostawa.md` (marker) | `19-re/index.md` |
| `07-moduly/biblioteka-standardowa.md` (tabela i admonition) | `zastosowania/19-re/index.md` |

## CONTENT HANDOFF

Brak wykładu źródłowego (PLAN_ROZWOJU: `re` wykluczone z części „Python Notatki”, „pełna strona do rozważenia w następnym wydaniu”) — rozdział napisany od podstaw według dokumentacji `re` i *Regular Expression HOWTO*.

## Listy kontrolne

- Przed commitem: staging z bloków; `refresh_outputs.py --mask`; `verify_page.py` dwa przebiegi z maską czasu; pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w 18/dostawa i 07/biblioteka-standardowa, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport zbiorczy po całej ścieżce.
