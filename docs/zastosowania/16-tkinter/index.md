# 16. Interfejs graficzny tkinter

Programy z poprzednich rozdziałów obsługuje się z terminala albo przez sieć. Użytkownik, który nie pisze programów, oczekuje okna: pól do wypełnienia, przycisków, listy z wynikami. **tkinter** to moduł interfejsu graficznego z biblioteki standardowej — nakładka na Tcl/Tk, zestaw narzędzi okienkowych działający na Windows, macOS i Linuksie — więc okno można zbudować bez instalowania czegokolwiek. Programowanie okienkowe różni się od skryptów jednym: program nie wykonuje instrukcji od góry do dołu, tylko po zbudowaniu okna oddaje sterowanie **pętli zdarzeń** (ang. *event loop*), która czeka na kliknięcia i klawisze i wywołuje przypisane im funkcje. Rozdział wprowadza tkinter od pierwszego okna po kompletną aplikację, a przedostatnia strona pokazuje bibliotekę **CustomTkinter**, która nadaje tym samym oknom współczesny wygląd.

Kolejne strony omawiają widżety, menedżery układu, zdarzenia i zmienne kontrolne, aplikację jako klasę z menu i dialogami, widżety ttk, płótno Canvas, CustomTkinter i mini-projekt menedżera kontaktów z logiką oddzieloną od okna i testami. Skrypty rozdziału wypisują to, co da się sprawdzić bez klikania, a wygląd okien pokazują zrzuty wykonane z tych właśnie skryptów.

Wersje w chwili pisania: Python 3.14.7 z Tcl/Tk **9.0.4** — tkinter zgłasza wersję główną `9.0`; instalator z Python Install Managera zawiera Tk 9 od wydania 3.14.7, wcześniejsze instalacje mają Tk 8.6, które różni się kilkoma szczegółami omówionymi w tekście. Sprawdzenie:

```powershell title="Terminal"
python -c "import tkinter; print(tkinter.TkVersion, tkinter.Tk().tk.call('info', 'patchlevel'))"
```

CustomTkinter **6.0.0** i Pillow 12.3.0 (obrazy dla płótna i CustomTkinter) to jedyne nowe pakiety spoza biblioteki standardowej; pytest służy testom projektu. Plików do pobrania nie ma — obrazy przykładowe tworzą skrypty. Rozdział buduje na rozdziałach 6 (funkcje jako obiekty, lambda, domknięcia), 8 (wyjątki), 9 (CSV), 10 (klasy), 12 (klasy danych, wzorzec obserwatora), 15 (wątki, kolejka) i 16 (pytest) części „Python Notatki”. Plik wymagań rozdziału potrzebuje trzech wierszy — pytest jest w nim od poprzednich rozdziałów, dopisujemy dwa ostatnie:

```text title="requirements.txt"
pytest==9.1.1
customtkinter==6.0.0
pillow==12.3.0
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Okno i widżety](okno-i-widzety.md) — pierwsze okno, etykieta i przycisk, pola tekstowe, widżety wyboru, tk a ttk, ostrość na ekranach o dużej skali
2. [Menedżery układu](uklad.md) — pack, grid, place, ramki i zagnieżdżanie, pułapka mieszania menedżerów, porównanie
3. [Zdarzenia i zmienne kontrolne](zdarzenia-i-zmienne.md) — zmienne kontrolne i obserwatorzy, `command` a `bind`, pułapka lambda w pętli, zegar i zamykanie okna, dymek podpowiedzi
4. [Aplikacja obiektowa, menu i dialogi](aplikacja-i-menu.md) — klasa aplikacji i menu, dialogi, okna potomne, zamykanie aplikacji
5. [Widżety ttk — zakładki, tabela i style](widzety-ttk.md) — zakładki, tabela Treeview, style i motywy, pasek postępu
6. [Canvas — rysowanie i animacja](canvas.md) — figury i tekst, obrazy, rysowanie i przeciąganie myszą, animacja, szachownica
7. [CustomTkinter — nowoczesny wygląd](customtkinter.md) — instalacja i pierwsze okno, tryby wyglądu i motywy, widżety, zakładki i przewijanie, aplikacja z panelem bocznym, współpraca z tkinter
8. [Mini-projekt: menedżer kontaktów](projekt-kontakty.md) — logika poza oknem z testami, okno aplikacji, praca w tle, dobre praktyki i pułapki
