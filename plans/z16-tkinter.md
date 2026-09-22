# Projekt rozdziału 16 części „Python Zastosowania” — Interfejs graficzny tkinter

Czwarty rozdział ścieżki Aplikacje. Branch: `content/zastosowania-16` (z `dev` po `fe9d2a5`). Realizacja autonomiczna na polecenie autora z 22 IX 2026; na życzenie autora rozdział zawiera także samouczek biblioteki **CustomTkinter** (nowocześniejszy wygląd), stąd 8 stron zamiast planowanych 7. Punkt wyjścia: projekt rozdziału 18 w `PLAN_ROZWOJU.md` (sekcja 18) oraz źródła: PDF Dodatki TKINTER (s. 127–150) i Wyklad_11.

## Decyzje redakcyjne (22 IX 2026)

1. **Zakres:** okno i widżety (Tk, `title`/`geometry`/`resizable`/`minsize`, `mainloop`; Label/Button z `command` i `invoke()`, `configure`; Entry (`insert`/`get`/`delete`, `show`, `focus`, `state`), Text z paskiem przewijania, tagi, `"1.0"`/`"end-1c"`, ScrolledText; Checkbutton/Radiobutton ze zmiennymi, Combobox (`current`, `readonly`, `<<ComboboxSelected>>`), Spinbox ttk, Scale (argument tekstowy `command`), Listbox; tk a ttk; ostrość na ekranach o skali >100% — `SetProcessDpiAwareness` i `tk scaling`); menedżery układu (pack, grid z `sticky`/`weight`/`columnspan`, place, ramki i zagnieżdżanie, `winfo_children` + `grid_configure`, pułapka pack+grid — `TclError` w Tk 9 i 8.6, zawieszenie tylko w dawnych wersjach; porównanie); zdarzenia i zmienne (StringVar/IntVar/DoubleVar/BooleanVar, `textvariable`, `trace_add`/`trace_info`/`trace_remove`, `trace("w")` → `TclError` i `DeprecationWarning`; `command` a `bind` z obiektem zdarzenia, `event_generate`, tabela zdarzeń, skróty klawiszowe; pułapka lambda w pętli; `after`/`after_cancel`, zegar, `protocol`; dla dociekliwych: dymek podpowiedzi); aplikacja obiektowa, menu i dialogi (klasa po `tk.Tk`, podział na metody `_buduj_*`, stan w atrybutach; Menu z kaskadą, separatorem, akceleratorami, `tearoff` domyślnie 0 w Tk 9; messagebox z wartościami zwracanymi, filedialog, simpledialog; Toplevel z `transient`/`grab_set`/`wait_window`; zamykanie `destroy` a `quit`); widżety ttk (Notebook, Treeview z nagłówkami, sortowaniem i paskiem przewijania, Style — motywy i własny styl, Progressbar sterowany `after`); Canvas (figury, tekst, tagi, `itemconfig`/`coords`/`move`/`delete`, obraz PhotoImage z referencją, rysowanie myszą, przeciąganie `find_closest`, animacja `after`, szachownica); CustomTkinter 6.0.0 (instalacja, `CTk`, tryby jasny/ciemny i motywy kolorów, widżety CTk*, `CTkFont`, `CTkTabview`, `CTkScrollableFrame`, `CTkImage`, aplikacja z panelem bocznym jako klasa po `CTk`, współpraca z tkinter — Menu, Treeview, Canvas — oraz ograniczenia, skalowanie); mini-projekt menedżera kontaktów (klasa danych, logika poza GUI z testami pytest, formularz z walidacją, wyszukiwanie na żywo, Treeview i pasek stanu, eksport CSV; praca w tle — wątek, kolejka i `after` (zapowiedź z rozdziału 15 „Python Notatki”); dobre praktyki i pułapki). Poza zakresem: obrazy JPEG w PhotoImage (tylko przez Pillow — wzmianka), drukowanie, przeciąganie plików, `tkinter.dnd`, style Windows innych niż domyślne, biblioteki PyQt/wxPython/Kivy (jedno zdanie), Tk 8.6.
2. **Biblioteki i wersje (sonda 22 IX 2026):** Python 3.14.7 z Tcl/Tk **9.0.4** (`tkinter.TkVersion` 9.0, `root.tk.call("info", "patchlevel")`), **CustomTkinter 6.0.0** (zależności darkdetect, packaging), **Pillow 12.3.0** (obrazy dla Canvas/CTkImage i zrzuty). Plik wymagań: `customtkinter==6.0.0`, `pillow==12.3.0` (+ pytest dla testów projektu).
3. **Dane:** brak plików do pobrania; obrazy dla przykładów tworzone w skryptach przez Pillow; kontakty przykładowe wpisane w skrypt projektu. Zrzuty okien generowane automatycznie: harness `sitecustomize.py` (scratchpad `helper16/`, ładowany przez `PYTHONPATH`) podmienia `mainloop()` — okno działa ~0,9 s (zegary i `after` zdążą zadziałać), jest podnoszone na wierzch, zrzut każdego okna składany na neutralnym tle (bez pulpitu) do `docs/zastosowania/16-tkinter/img/<skrypt>.png`; proces z `SetProcessDpiAwareness(2)`, więc obraz jest ostry (Tk 9 skaluje czcionki: `tk scaling` 2.0 przy 150 %). Skrypty książki są nietknięte i uruchamiane przez harness w całości (`refresh_outputs.py`/`verify_page.py` z `PYTHONPATH=helper16`); wydruki przed `mainloop()` weryfikowane, dialogi modalne tylko po kliknięciu.
4. **Fakty sprawdzone 22 IX 2026 (Tk 9.0.4, Windows 11):** pack i grid w jednym kontenerze → `TclError: cannot use geometry manager "grid" inside ".!frame": pack is already managing its content windows` (Tk 8.6.18 również zgłasza `TclError`, z innym brzmieniem — zawieszenie dotyczy dawnych wersji); `Menu` ma `tearoff` domyślnie 0; `Variable.trace("w", …)` → `DeprecationWarning: trace_variable() is deprecated and not supported with Tcl 9; use trace_add() instead` + `TclError: bad option "variable": must be add, info, or remove`; `trace_add` zwraca nazwę, `trace_info()` listę krotek; `after()` zwraca tekst `after#…`; domyślny motyw ttk `vista`, motywy `('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')`; `TkDefaultFont` Segoe UI 9; `Text.get("1.0", "end")` kończy się `\n`, `"end-1c"` nie; `messagebox.askyesno`/`askokcancel`/`askretrycancel` zwracają `bool`, `askquestion` tekst `"yes"`/`"no"`, `askyesnocancel` `True`/`False`/`None`; `Scale` `command` dostaje tekst; `Combobox` `values` jako krotka tekstów; `IntVar.set("7")` → `7`; `event_generate` wywołuje procedury `bind`; `Button.invoke()` wywołuje `command`; `find_closest` zwraca krotkę; `winfo_children` w kolejności utworzenia; `tk scaling` 1,334 bez świadomości DPI, 2,0 z nią (ekran 150 %); CustomTkinter 6.0.0 działa z Tk 9, sam włącza świadomość DPI, `CTk.mainloop` wykonuje własne przygotowania i woła `tkinter.Tk.mainloop`; `CTkTabview.add()/tab()`, `CTkProgressBar.set()`, `CTkSlider(command=)` dostaje `float`, `CTkOptionMenu(command=)` tekst, motywy `blue`, `dark-blue`, `green`, `gold`.
5. **Terminy:** „widżet” (ang. *widget*), „pętla zdarzeń” (ang. *event loop*), „funkcja zwrotna” (ang. *callback*), „menedżer układu” (ang. *geometry manager*), „zmienna kontrolna” (ang. *control variable*), „obserwator” (ang. *observer*), „wiązanie zdarzenia” (ang. *event binding*), „akcelerator” (ang. *accelerator*), „okno modalne” (ang. *modal window*), „płótno” (Canvas), „tryb wyglądu” (ang. *appearance mode*), „motyw” (ang. *theme*), „skalowanie DPI”.
6. Odsyłacze wstecz: „Python Notatki” 6 (funkcje jako obiekty, lambda, domknięcia, późne wiązanie), 8 (wyjątki, `with`), 9 (csv, `pathlib`), 10 (klasy, dziedziczenie), 12 (klasy danych, wzorzec obserwatora), 15 (wątki, kolejka, `after`), 16 (pytest); „Python Zastosowania” 3 (Matplotlib — Canvas a wykresy: wzmianka), 13–15 (sklep: okno dla użytkownika — zapowiedź projektu 18). Zapowiedzi: 17 (pakowanie), 18 (projekt aplikacji) — `TODO`.
7. Domknięcia: markery „tkinter” w „Python Notatki” 06/funkcje-jako-obiekty, 12/wzorce-projektowe, 15/synchronizacja oraz w „Python Zastosowania” 15/testy-i-uruchomienie → strony rozdziału 16; markery „projekt aplikacji”, „pakowanie i dystrybucja” zostają.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „16. Interfejs graficzny tkinter” | cel; pętla zdarzeń; biblioteki i wersje; plik wymagań; ---; ## W tym rozdziale (8) |
| `okno-i-widzety.md` | Okno i widżety | Pierwsze okno (`pierwsze-okno.py`); Etykieta i przycisk (`etykieta-przycisk.py`); Pola tekstowe (`pola.py`); Widżety wyboru (`wybor.py`); tk a ttk; Ostrość na ekranach o dużej skali (`dpi.py`) |
| `uklad.md` | Menedżery układu | pack (`pack.py`); grid (`grid.py`); place (`place.py`); Ramki i zagnieżdżanie (`ramki.py`); Pułapka: pack i grid w jednym kontenerze (`mieszanie.py`); Porównanie |
| `zdarzenia-i-zmienne.md` | Zdarzenia i zmienne kontrolne | Zmienne kontrolne i obserwatorzy (`zmienne.py`); `command` a `bind` (`zdarzenia.py`); Pułapka lambda w pętli (`petla.py`); Zegar, `after` i zamykanie okna (`zegar.py`); Dla dociekliwych: dymek podpowiedzi (`dymek.py`) |
| `aplikacja-i-menu.md` | Aplikacja obiektowa, menu i dialogi | Klasa aplikacji i menu (`aplikacja.py`); Dialogi (`dialogi.py`); Okna potomne (`potomne.py`); Zamykanie aplikacji |
| `widzety-ttk.md` | Widżety ttk — zakładki, tabela i style | Zakładki (`zakladki.py`); Tabela Treeview (`tabela.py`); Style i motywy (`style.py`); Pasek postępu (`postep.py`) |
| `canvas.md` | Canvas — rysowanie i animacja | Figury i tekst (`figury.py`); Obrazy (`obrazy.py`); Rysowanie i przeciąganie myszą (`rysowanie.py`, `przeciaganie.py`); Animacja (`animacja.py`); Szachownica (`szachownica.py`) |
| `customtkinter.md` | CustomTkinter — nowoczesny wygląd | Instalacja i pierwsze okno (`ctk-pierwsze.py`); Tryby wyglądu i motywy (`ctk-tryby.py`); Widżety (`ctk-widzety.py`); Zakładki i przewijanie (`ctk-uklad.py`); Aplikacja z panelem bocznym (`ctk-aplikacja.py`); Współpraca z tkinter i ograniczenia (`ctk-tabela.py`) |
| `projekt-kontakty.md` | Mini-projekt: menedżer kontaktów | Założenia; Logika poza oknem (`kontakty_logika.py`, `tests/test_kontakty.py`, pytest); Okno aplikacji (`kontakty.py`); Praca w tle: wątek, kolejka i `after` (`praca-w-tle.py`); Dobre praktyki i pułapki; Dalej (TODO 17, 18) |

Szacunek: 1300–1500 linii; ok. 30 skryptów, ok. 25 zrzutów okien generowanych automatycznie.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 15)

```yaml
      - 16. Interfejs graficzny tkinter:
          - Wprowadzenie: zastosowania/16-tkinter/index.md
          - Okno i widżety: zastosowania/16-tkinter/okno-i-widzety.md
          - Menedżery układu: zastosowania/16-tkinter/uklad.md
          - Zdarzenia i zmienne kontrolne: zastosowania/16-tkinter/zdarzenia-i-zmienne.md
          - Aplikacja obiektowa, menu i dialogi: zastosowania/16-tkinter/aplikacja-i-menu.md
          - Widżety ttk — zakładki, tabela i style: zastosowania/16-tkinter/widzety-ttk.md
          - Canvas — rysowanie i animacja: zastosowania/16-tkinter/canvas.md
          - CustomTkinter — nowoczesny wygląd: zastosowania/16-tkinter/customtkinter.md
          - Mini-projekt: menedżer kontaktów: zastosowania/16-tkinter/projekt-kontakty.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `projekt-kontakty.md` | pakowanie; projekt aplikacji | rozdziały 17, 18 |

## Domknięcia

| Plik | Cel |
|---|---|
| `06-funkcje/funkcje-jako-obiekty.md` (marker tkinter) | `zastosowania/16-tkinter/okno-i-widzety.md` |
| `12-oop-zaawansowane/wzorce-projektowe.md` (marker tkinter) | `zastosowania/16-tkinter/zdarzenia-i-zmienne.md` |
| `15-wspolbieznosc/synchronizacja.md` (marker tkinter) | `zastosowania/16-tkinter/projekt-kontakty.md` |
| `zastosowania/15-fastapi/testy-i-uruchomienie.md` (marker tkinter) | `zastosowania/16-tkinter/index.md` |

## CONTENT HANDOFF

Źródła: PDF Dodatki TKINTER (s. 127–150) — przykłady przepisane (`textvar` → `textvariable`, `trace("w")` → `trace_add`, `tk.Spinbox` z `bd` → `ttk.Spinbox`, `exit()` → `destroy()`, `iconbitmap` → `iconphoto`, `grid_configure` to `grid`, `foreground` = kolor tekstu, `askyesno` → `bool`, teksty bez polskich znaków → z polskimi); Wyklad_11 — pułapka pack/grid opisana jako zawieszenie: w Tk 9 to `TclError`; `bind("<Escape>", quit)` → `lambda e: root.destroy()`; `get("1.0", END)` → `"end-1c"`. Bez odwołań do materiałów z zajęć.

## Listy kontrolne

- Przed commitem: staging skryptów z bloków (`extract_project.py`); `PYTHONPATH=helper16 ZRZUTY_KATALOG=docs/zastosowania/16-tkinter/img refresh_outputs.py` (wydruki + zrzuty); `PYTHONPATH=helper16 verify_page.py` dwa przebiegi (bez zrzutów); pytest projektu; obejrzenie każdego zrzutu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w rozdziałach 6, 12, 15 „Python Notatki” i 15 „Python Zastosowania”, status w `PLAN_ZASTOSOWANIA.md` (7 → 8 stron), `ZRZUTY.md` (zrzuty generowane), integracja do `dev`, pamięć, raport.
