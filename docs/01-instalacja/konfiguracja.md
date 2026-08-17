# Konfigurowanie narzędzi do pracy

Zasadniczo można pisać program w Pythonie w prostym, interaktywnym środowisku programowania, w powłoce (konsoli), czyli realizując **REPL** (ang. *read-eval-print loop*) — użytkownik może wprowadzać polecenia, które zostaną wykonane, a ich wynik wypisany na ekran. Nie jest to wydajny sposób pracy. Do pisania kodu potrzebny jest edytor, lub lepiej — środowisko pracy wspomagające proces tworzenia kodu (**IDE**, *integrated development environment*).

## Wybór edytora / IDE

Można wybrać według własnych preferencji (niektórzy, znając i używając wcześniej, trwają przy edytorach **vim** lub **emacs**). Niektórzy używają załączonego w pythonowym pakiecie instalacyjnym **IDLE**.

Bardzo dużo możliwości dają lekkie edytory:

- [Sublime Text](https://www.sublimetext.com/)
- [Zed](https://zed.dev/)

Z drugiej strony, w pełni wyposażony pakiet IDE dedykowany dla Pythona to [**PyCharm**](https://www.jetbrains.com/pycharm/) (bezpłatny do użytku niekomercyjnego; istnieje także licencja akademicka). Całkowicie darmowym produktem jest [**Spyder**](https://www.spyder-ide.org/), używany w analizie danych, naukach przyrodniczych oraz inżynierii, głównie ze względu na swoją integrację z popularnymi bibliotekami Pythona, takimi jak NumPy, SciPy czy Matplotlib.

## Rekomendacja: Visual Studio Code

Bardzo wiele osób używa obecnie **Visual Studio Code** (firmy Microsoft — ale jest to produkt wieloplatformowy), ze względu na wydajne działanie, dużą elastyczność, konfigurowalność oraz ciągłe wsparcie i aktualizacje. Za pomocą wybranych dodatków można szybko skonfigurować VSC do wydajnej pracy z Pythonem. Oto jak to zrobić.

### Instalacja i rozszerzenia

1. Instalujemy VSC: [code.visualstudio.com/download](https://code.visualstudio.com/download)
2. Uruchamiamy i dodajemy rozszerzenia **Extensions** (++ctrl+shift+x++): **Python** (IntelliSense od Microsoft)
3. W ten sam sposób instalujemy linter: w **Extensions** wyszukujemy **Pylint** (wydawca Microsoft) i instalujemy

**Linter** to moduł sprawdzający i podpowiadający składnię. Dawniej wybierało się go poleceniem palety *Python: Select Linter* — polecenie to zostało wycofane, a lintery są obecnie osobnymi rozszerzeniami VSC. Po zainstalowaniu rozszerzenia Pylint linter jest od razu aktywny, bez dodatkowej konfiguracji.

!!! note "Wersja pylinta"
    Rozszerzenie zawiera wbudowaną kopię pylinta. Jeżeli jednak w wybranym
    interpreterze (środowisku) jest zainstalowana własna wersja — poleceniem
    `python -m pip install pylint` — to zostanie użyta właśnie ona, co daje
    kontrolę nad wersją lintera w projekcie.

### Test lintera

Utwórzmy plik `main.py` (w jakimś podkatalogu, który też można utworzyć) i wpiszmy celowo błędną składnię (z punktu widzenia Python3), na przykład:

```python title="main.py"
print "hello wrong"
```

Powinien się pojawić problem oraz podpowiedź.

<!-- TODO: screenshot — podkreślenie błędu przez pylint -->

Albo (++ctrl+shift+m++) zakładka **Problems**:

<!-- TODO: screenshot — zakładka Problems -->

### Usuwanie Pylance

Może być tak, że zobaczymy dwie „porady” — druga pochodzi od **Pylance**, który nie jest linterem, lecz serwerem językowym zapewniającym IntelliSense; jego diagnostyka może się dublować z pylintem. Powiedzmy, że chcemy go wyłączyć. Prostą operację (udać się do rozszerzeń, odszukać Pylance — i można np. dezaktywować, albo odinstalować) trzeba jednak uzupełnić wpisem w pliku konfiguracyjnym VSC.

W tym celu idziemy do Command Palette (++ctrl+shift+p++) i szukamy **Preferences: Open User Settings (JSON)** (nie *Default*).

<!-- TODO: screenshot — otwieranie settings.json -->

Otwieramy plik `settings.json` do edycji i np. na końcu dopisujemy (jeśli nie ma):

```json title="settings.json"
"python.languageServer": "None"
```

Po przeładowaniu powinniśmy widzieć podpowiedź tylko z Pylint.

## PEP 8 i formatowanie kodu

W języku Python szereg opisów jak ma działać oraz propozycji usprawnień zawarta jest w tak zwanych **PEPs** (Python Enhancement Proposals): [peps.python.org](https://peps.python.org/). Jeden z najbardziej znanych to [**PEP 8 — Style Guide for Python Code**](https://peps.python.org/pep-0008/), czyli jak powinien być formatowany kod Pythona.

Formatery — podobnie jak lintery — są obecnie osobnymi rozszerzeniami VSC. W **Extensions** wyszukujemy **autopep8** (wydawca Microsoft) i instalujemy. W naszym pliku napiszmy teraz np.:

```python title="main.py"
x=0
```

a następnie w Command Palette (++ctrl+shift+p++) **Format Document With** i wybierzmy **autopep8** (opcja *Configure Default Formatter* pozwala ustawić go jako domyślny formater dla plików Pythona).

Teraz możemy wykonać formatowanie — albo idąc do *Format Document* jak wyżej, albo lepiej, korzystając ze skrótu klawiszowego ++shift+alt+f++. W tym przypadku zobaczymy:

```{ .python .no-copy }
x = 0
```

ponieważ w PEP8 jest rekomendacja, aby przed i za operatorem były spacje.

!!! warning "Formatowanie ≠ poprawianie błędów"
    Nie należy formatowania mylić z poprawianiem błędów — do tego celu służy
    linter (wcześniej opisany pylint).

Jeśli chcemy, aby formatowanie nastąpiło automatycznie podczas zapisu pliku, można w **File → Preferences → Settings** (albo skrót ++ctrl+comma++) wyszukać `formatOnSave` i zaznaczyć opcję **Editor: Format On Save**.

## Wyciszanie ostrzeżeń pylint

Załóżmy, że mamy z powrotem w pliku prostą instrukcję:

```python title="main.py"
print("pierwszy program")
```

Pylint, w zależności od ustawień, ostrzeże nas: *Missing module docstring* (czyli że nie ma w naszym pliku–module żadnego opisu komentarza). Jeśli ostrzeżenia nas irytują, można je wyłączyć. W tym celu idziemy do pliku `settings.json` (jak poprzednio) i dodajmy linię:

```json title="settings.json"
"pylint.args": ["--errors-only"]
```

Dawne ustawienie `python.linting.pylintArgs` zostało wycofane wraz z wbudowanym lintowaniem — konfigurację przekazuje się obecnie przez ustawienia rozszerzenia Pylint (`pylint.args`).

!!! note "Odczytanie znaczenia komunikatu"
    Można odczytać konkretny kod komunikatu, żeby się zorientować, o co linterowi
    chodzi — w terminalu piszemy:

    ```bash title="Terminal"
    pylint --help-msg=missing-module-docstring
    ```

## Uruchamianie kodu — Code Runner

Mamy zatem plik z instrukcją `print` i chcemy go uruchomić z VSC. W tym celu dodamy jeszcze jedno rozszerzenie: idziemy do **Extensions** i szukamy `code runner`, wybieramy ten z pomarańczową ikonką **.run** i instalujemy.

Od tej pory uruchomienie kodu to ++ctrl+alt+n++ (a zatrzymanie ++ctrl+alt+m++).

<!-- TODO: screenshot — wynik działania Code Runner w terminalu VSC -->

!!! tip "Terminal w VSC"
    Jeśli ta sekcja na dole nam się przypadkiem zamknie, to:
    **Terminal → New Terminal** (lub skrót klawiszowy ++ctrl+grave++).

W ten sposób mamy przygotowane środowisko pracy w VSC.
