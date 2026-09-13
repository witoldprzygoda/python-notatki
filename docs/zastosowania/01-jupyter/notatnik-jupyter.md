# Notatnik Jupyter w VSC

Notatnik Jupyter poznaliśmy w tomie I jako program uruchamiany w przeglądarce (rozdział [1. Instalacja i środowisko pracy](../../01-instalacja/notebook.md)) i jako usługę Google Colab. W pracy z danymi wygodniejszy jest notatnik otwarty w Visual Studio Code: ten sam edytor, to samo środowisko wirtualne i te same narzędzia, co przy skryptach. Ten podrozdział wprowadza pojęcia — komórka, jądro, stan — i nawyki, które odróżniają uporządkowaną pracę w notatniku od przypadkowej.

## Notatnik a skrypt

Skrypt wykonuje się od początku do końca w nowym interpreterze. Notatnik to plik `.ipynb` — dokument w formacie JSON z rozdziału 9 — złożony z **komórek** (ang. *cells*) kodu i tekstu, wykonywanych pojedynczo, w dowolnej kolejności, w jednym działającym interpreterze zwanym **jądrem** (ang. *kernel*). Wynik każdej komórki — wydruk, wartość wyrażenia, wykres — zostaje zapisany pod nią, razem z kodem. Notatnik jest więc zarazem laboratorium i raportem: pozwala próbować, poprawiać jedną komórkę bez powtarzania reszty i pokazać czytelnikowi drogę do wyniku. Ceną jest stan przechowywany między komórkami; wracamy do tego niżej.

## Instalacja i pierwszy notatnik

W środowisku wirtualnym projektu instalujemy **ipykernel** — pakiet, który udostępnia interpreter jako jądro — oraz JupyterLab — nowszy interfejs przeglądarkowy projektu Jupyter, następca klasycznego Jupyter Notebook z tomu I — jeśli chcemy pracować także w przeglądarce; razem z nim instaluje się narzędzie nbconvert, potrzebne w ostatniej sekcji:

```powershell title="Terminal"
python -m pip install ipykernel jupyterlab
```

W VSC potrzebne jest rozszerzenie **Jupyter** (`ms-toolsai.jupyter`) z galerii rozszerzeń, obok rozszerzenia Python z rozdziału 1. Nowy notatnik tworzy polecenie **Create: New Jupyter Notebook** z palety poleceń (++ctrl+shift+p++) albo utworzenie pliku z rozszerzeniem `.ipynb`; przycisk **Select Kernel** w prawym górnym rogu wybiera jądro — wskazujemy interpreter ze środowiska wirtualnego projektu, tak jak przy skryptach w rozdziale 1. Komórkę wykonujemy skrótem ++shift+enter++ (wykonaj i przejdź dalej) albo ++ctrl+enter++ (wykonaj i zostań).

<!-- TODO: screenshot — nowy notatnik w VSC: pusta komórka kodu, przycisk Select Kernel w prawym górnym rogu; kadr: górna część edytora -->

<!-- TODO: screenshot — lista wyboru jądra z interpreterem .venv projektu; kadr: sama lista -->

## Komórki kodu i wartość ostatniego wyrażenia

Komórka kodu zachowuje się jak konsola z rozdziału 2: wartość ostatniego wyrażenia jest wypisywana bez `print()`, a przypisanie nic nie wypisuje. W książce komórki notatnika zapisujemy jako bloki z numerem komórki, a pod nimi to, co pojawia się pod komórką w notatniku:

```python title="pierwszy.ipynb — komórka 1"
x = 5
x * 2
```

```{ .text .no-copy }
10
```

```python title="pierwszy.ipynb — komórka 2"
print("wydruk")
x + 1
```

```{ .text .no-copy }
wydruk
6
```

```python title="pierwszy.ipynb — komórka 3"
lista = [1, 2, 3]
lista.append(4)
lista
```

```{ .text .no-copy }
[1, 2, 3, 4]
```

```python title="pierwszy.ipynb — komórka 4"
_ * 2
```

```{ .text .no-copy }
[1, 2, 3, 4, 1, 2, 3, 4]
```

Wydruki z `print()` pojawiają się w kolejności wykonania, a wartość ostatniego wyrażenia — na końcu, w postaci `repr()` z rozdziału 7; dlatego w komórce 3 lista jest wypisana z przecinkami i nawiasami. Nazwa `_` przechowuje wartość ostatniego wyrażenia, jak w konsoli. Metoda `append()` zwraca `None`, którego notatnik nie wypisuje — stąd `lista` w osobnym wierszu na końcu komórki.

## Komórki Markdown

Drugi rodzaj komórki zawiera tekst w składni Markdown — tej samej, w której napisano tę książkę: nagłówki `#`, listy `-`, wyróżnienia `**`, kod w odwrotnych apostrofach, wzory między znakami dolara. Komórkę tekstową dodajemy przyciskiem **+ Markdown** na pasku notatnika (ten sam przycisk pojawia się między komórkami), a istniejącą komórkę kodu zamieniamy skrótem ++m++ w trybie poleceń (++esc++ wychodzi z edycji komórki, ++y++ zamienia z powrotem na kod). Dobry notatnik przeplata kod krótkimi komórkami tekstu: pytanie przed analizą, wniosek po wykresie. Komórka tekstowa w książce wygląda tak:

```markdown title="pierwszy.ipynb — komórka Markdown"
## Średnia temperatura

Rok 2024 był cieplejszy od 2025 o **0,15 °C**; różnica mieści się w zmienności rocznej.
```

## Stan jądra i kolejność wykonania

Nazwy zdefiniowane w jednej komórce są widoczne we wszystkich następnych — i we wcześniejszych, jeśli wykonamy je ponownie. Numer w nawiasie obok komórki (`[3]`) mówi, jako która została wykonana, nie gdzie stoi w pliku. Stąd najczęstszy błąd pracy w notatniku:

```python title="stan.ipynb — komórka 1"
licznik = 0
```

```python title="stan.ipynb — komórka 2"
licznik += 1
licznik
```

```{ .text .no-copy }
1
```

```python title="stan.ipynb — komórka 3"
del licznik
licznik
```

```{ .text .no-copy }
NameError: name 'licznik' is not defined
```

Wykonanie komórki 2 dwa razy daje `2`, choć w pliku nic się nie zmieniło; komórka wykonana, a potem usunięta, zostawia w jądrze swoje nazwy; komórka 3 pokazuje, co dzieje się, gdy nazwa zniknie — ten sam `NameError` zobaczymy po restarcie jądra, wykonując komórkę 2 bez komórki 1; w notatniku pod komórką pojawia się pełny ślad wywołań z rozdziału 8, w książce podajemy ostatni wiersz. Środek zaradczy jest jeden i stosujemy go przed każdym oddaniem wyników: **Restart** jądra i **Run All** — notatnik, który wykonuje się od góry do dołu w nowym jądrze, jest poprawny; inny nie. W VSC są to dwa przyciski na pasku notatnika, **Restart** i **Run All**; paleta poleceń ma też jedno polecenie **Restart Kernel and Run All Cells**.

## Polecenia magiczne

Jądro ipykernel opiera się na powłoce IPython z rozdziału 1 — stąd numeracja komórek taka jak znaki zachęty `In [1]:` — i rozszerza składnię o **polecenia magiczne** (ang. *magic commands*) zaczynające się od `%` (jeden wiersz) lub `%%` (cała komórka). Najprzydatniejsze przy danych to pomiary czasu — odpowiednik modułu `timeit` z podrozdziału [Pomiar czasu i profilowanie](../../13-wydajnosc/pomiar-i-profilowanie.md) rozdziału 13 — i przegląd nazw w jądrze:

```python title="polecenia.ipynb — komórka 1"
%timeit sum(range(1000))
```

```{ .text .no-copy }
6.11 μs ± 712 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
```

```python title="polecenia.ipynb — komórka 2"
%%time
suma = sum(range(1_000_000))
suma
```

```{ .text .no-copy }
CPU times: total: 15.6 ms
Wall time: 11.3 ms
499999500000
```

```python title="polecenia.ipynb — komórka 3"
%who_ls
```

```{ .text .no-copy }
['suma']
```

`%timeit` sam dobiera liczbę powtórzeń i podaje średnią z odchyleniem; `%%time` mierzy jedno wykonanie całej komórki; `%who_ls` zwraca listę nazw zdefiniowanych w jądrze — po restarcie jest pusta. Polecenia magiczne nie są składnią Pythona: skrypt z takim wierszem nie uruchomi się, o czym trzeba pamiętać przy przenoszeniu kodu z notatnika do modułu.

## Pomoc w notatniku

Znak zapytania po nazwie wypisuje pod komórką docstring i sygnaturę (w VSC jako zwykły wydruk, w JupyterLab jako osobne wyjście komórki); dwa znaki zapytania pokazują kod źródłowy funkcji napisanej w Pythonie:

```{ .python .no-copy }
import numpy as np

np.linspace?
np.mean??
```

Zwykłe `help(np.linspace)` z rozdziału 6 działa tak samo, wypisując pomoc pod komórką; w VSC ten sam opis pojawia się po najechaniu kursorem na nazwę. Podrozdział o dokumentacji pokazuje, jak takie opisy czytać.

## JupyterLab w przeglądarce i eksport

Ten sam notatnik można otworzyć w przeglądarce — na przykład na komputerze bez VSC albo na zdalnym serwerze:

```powershell title="Terminal"
python -m jupyter lab
```

Polecenie uruchamia serwer i otwiera JupyterLab pod adresem `http://localhost:8888/lab` (pełny adres z tokenem dostępu serwer wypisuje w terminalu); kończy je ++ctrl+c++ w terminalu — serwer prosi o potwierdzenie `y`, a drugie ++ctrl+c++ zamyka go bez pytania. Plik `.ipynb` przechowuje kod razem z wynikami, więc zapisany notatnik jest gotowym raportem; narzędzie **nbconvert** (instalowane z JupyterLab; osobno: `python -m pip install nbconvert`) zamienia go na inne formaty lub wykonuje od nowa bez otwierania:

```powershell title="Terminal"
python -m jupyter nbconvert --to html analiza.ipynb
python -m jupyter nbconvert --to script analiza.ipynb
python -m jupyter nbconvert --execute --to notebook --inplace analiza.ipynb
```

Pierwsze polecenie tworzy `analiza.html` do przekazania odbiorcy, który nie ma Pythona; drugie — `analiza.py` z kodem komórek rozdzielonym komentarzami `# In[N]:`; polecenia magiczne stają się w nim wywołaniami `get_ipython().run_line_magic(...)`, które poza IPythonem kończą się `NameError`, więc przed uruchomieniem skryptu trzeba je usunąć; trzecie wykonuje wszystkie komórki w nowym jądrze i zapisuje wyniki w pliku — to samo, co **Restart** i **Run All**, ale z wiersza poleceń, więc nadaje się do automatyzacji z rozdziału 16. W repozytorium Git notatnik z wynikami daje trudne do czytania różnice między wersjami (obrazy zapisane jako tekst); przed commitem wyniki można usunąć poleceniem `python -m jupyter nbconvert --clear-output --inplace analiza.ipynb`, jeśli notatnik jest kodem, a nie raportem.
