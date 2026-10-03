# Dziennik synchronizacji z dev

Każde przyjęcie stanu książki do gałęzi `cwiczenia` dopisuje jeden wiersz: utworzenie gałęzi, synchronizacja (krok 6 procedury synchronizacji w `kurs/README.md`) albo procedura naprawcza. Wiersz zatwierdzamy na gałęzi `sync/…` przed ostatnim uruchomieniem bramki, dlatego kolumna `cwiczenia` podaje commit scalenia, które wprowadziło stan książki, a nie końcowy commit gałęzi `cwiczenia`. Na gałąź `cwiczenia` wiersz trafia dopiero razem z zaakceptowaną synchronizacją.

Kolumny:

- **Data** — dzień synchronizacji (RRRR-MM-DD);
- **`dev`** — przyjęty commit `origin/dev`; od niego liczymy zakres następnej synchronizacji;
- **`cwiczenia`** — commit scalający, który wprowadził ten stan książki do gałęzi ćwiczeń;
- **Rodzaj** — utworzenie gałęzi, synchronizacja albo procedura naprawcza;
- **Bramka** — kod pełnej bramki (`--book origin/dev`) dla stanu przed dopisaniem wiersza;
- **Uwagi** — zmienione wiązania, decyzje przeglądu G4, podniesione wersje aktywności i usterki książki zgłoszone do poprawy.

| Data | `dev` | `cwiczenia` | Rodzaj | Bramka | Uwagi |
|---|---|---|---|---|---|
| 2026-10-03 | `7e79223` | `11bcb3d` | utworzenie gałęzi | 0 | scalenie zaakceptowanej gałęzi podglądu `podglad/cwiczenia` z `origin/dev`: 8 aktywności rozdziału 4 na 2 stronach; wiązań nie zmieniano |
