# Logowanie zamiast print

Gdy program przestaje być kilkuwierszowym skryptem, pojawia się potrzeba wiedzy o tym, co robił: które dane przetworzył, gdzie napotkał problem, ile czasu zajął dany etap. Pierwszym rozwiązaniem jest zwykle `print()` — i do wypisywania wyników dla użytkownika `print()` pozostaje właściwym narzędziem. Do rejestrowania **zdarzeń** (ang. *event*) w trakcie działania programu lepiej nadaje się moduł `logging` z biblioteki standardowej, który prowadzi **dziennik** (ang. *log*): każdy wpis ma poziom ważności, źródło i czas, a o tym, które wpisy pokazać i dokąd je kierować, decyduje jedna konfiguracja, a nie kod rozsiany po programie. W tym podrozdziale uczymy się prowadzić dziennik w konsoli, dobierać poziomy, rejestrować wyjątki ze śladem i formatować komunikaty; dziennik w pliku zapowiadamy na rozdział o wejściu i wyjściu.

## Zadania `print()` i dziennika

Dokumentacja modułu `logging` zestawia narzędzia według zadania; w skrócie:

| Zadanie | Narzędzie |
|---|---|
| wypisanie wyniku programu dla użytkownika | `print()` |
| odnotowanie zdarzenia w normalnej pracy programu (postęp, decyzje, statystyki) | dziennik: `info()` albo `debug()` |
| odnotowanie sytuacji nieoczekiwanej, z którą program sobie poradził | dziennik: `warning()` |
| ostrzeżenie dla programisty korzystającego z naszego kodu, że powinien zmienić własny kod (w bibliotekach) | `warnings.warn()` — poza zakresem książki |
| zgłoszenie błędu, którego nie da się obsłużyć w tym miejscu | `raise` |
| odnotowanie błędu, który obsłużono i po którym program pracuje dalej | dziennik: `error()` albo `exception()` |

Wywołania `print()` rozsiane po kodzie diagnostycznym trzeba usuwać przed oddaniem programu albo zostawić kosztem czytelności wyjścia; nie da się ich wyłączyć jednym ustawieniem, nie mają znacznika czasu ani informacji o źródle, a w programie z kilku modułów nie wiadomo, który z nich wypisał dany wiersz. Dziennik rozwiązuje wszystkie te problemy naraz.

## Pierwszy dziennik

Funkcje modułu `logging` — `logging.info()`, `logging.warning()` i pokrewne — działają bez żadnej konfiguracji, z ustawieniami domyślnymi: przy pierwszym użyciu same konfigurują dziennik główny o nazwie `root`, który rejestruje wyłącznie komunikaty o poziomie `WARNING` i wyższym i wypisuje je na strumień błędów w formacie `POZIOM:nazwa:komunikat`:

```python title="bez-konfiguracji.py"
import logging

logging.info("program uruchomiony")
logging.warning("brak pliku z ustawieniami, przyjmuję domyślne")
```

```{ .text .no-copy }
WARNING:root:brak pliku z ustawieniami, przyjmuję domyślne
```

Komunikat `info()` został odrzucony jako zbyt mało ważny. W programach nie wywołujemy funkcji modułu bezpośrednio, lecz tworzymy własny dziennik funkcją `getLogger()`, podając jako nazwę `__name__` — nazwę modułu z rozdziału 7; w programie uruchomionym bezpośrednio jest to `__main__`, a w module importowanym nazwa modułu, dzięki czemu każdy wpis mówi, skąd pochodzi. Konfigurację ustala funkcja `basicConfig()`, wywoływana **raz**, na początku programu, przed pierwszym komunikatem: argument `level=` ustala próg ważności, a `format=` układ wpisu, w którym pola w nawiasach — `%(levelname)s`, `%(name)s`, `%(message)s` — zostają zastąpione wartościami:

```python title="pierwszy-dziennik.py"
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

log.debug("szczegóły techniczne")
log.info("program uruchomiony")
log.warning("brak pliku z ustawieniami, przyjmuję domyślne")
log.error("nie udało się zapisać wyniku")
```

```{ .text .no-copy }
INFO __main__: program uruchomiony
WARNING __main__: brak pliku z ustawieniami, przyjmuję domyślne
ERROR __main__: nie udało się zapisać wyniku
```

Próg `INFO` przepuścił trzy komunikaty i odrzucił `debug()`. Wpisy trafiają na strumień błędów, wprowadzony w podrozdziale [Obsługa wyjątków](obsluga-wyjatkow.md#program-bez-obsugi-i-z-obsuga), więc nie mieszają się z wynikami wypisywanymi przez `print()` na standardowe wyjście — po przekierowaniu wyjścia programu do pliku dziennik pozostaje w konsoli. Wywołanie `basicConfig()` musi poprzedzać pierwszy komunikat. Funkcje modułu, jak `logging.warning()`, przy pierwszym użyciu same wywołują `basicConfig()` bez argumentów, jeśli dziennik główny nie ma jeszcze konfiguracji, a kolejne `basicConfig()` nic już nie zmienia:

```python title="konfiguracja-za-pozno.py"
import logging

logging.warning("pierwszy komunikat")
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logging.debug("komunikat diagnostyczny")
logging.warning("drugi komunikat")
```

```{ .text .no-copy }
WARNING:root:pierwszy komunikat
WARNING:root:drugi komunikat
```

Ani próg `DEBUG`, ani nowy format nie zadziałały — pierwszy komunikat już ustalił konfigurację domyślną; jest to najczęstsza przyczyna „niedziałającego” `basicConfig()`. Dziennik nazwany, utworzony przez `getLogger()`, nie konfiguruje niczego sam: bez `basicConfig()` wypisuje na strumień błędów sam komunikat, bez poziomu i nazwy, a późniejsze `basicConfig()` działa normalnie. Niezależnie od odmiany reguła jest jedna: konfigurację ustalamy na początku programu.

## Poziomy komunikatów

Każdy komunikat ma jeden z pięciu poziomów standardowych, a każdy poziom liczbę, dzięki której próg z `basicConfig()` działa jako porównanie: przepuszczane są komunikaty o wartości równej progowi lub wyższej.

| Poziom | Wartość | Kiedy |
|---|---|---|
| `DEBUG` | 10 | szczegóły przydatne tylko przy szukaniu błędu: wartości pośrednie, przebieg pętli |
| `INFO` | 20 | potwierdzenie, że program działa zgodnie z oczekiwaniem: etapy, statystyki |
| `WARNING` | 30 | sytuacja nieoczekiwana, z którą program sobie poradził; domyślny próg |
| `ERROR` | 40 | błąd, przez który program nie wykonał jakiejś operacji |
| `CRITICAL` | 50 | błąd, po którym program może nie być w stanie kontynuować |

Kryterium wyboru jest odbiorca: `DEBUG` czyta programista podczas pracy, `INFO` — osoba nadzorująca działanie programu, `WARNING` i wyżej — każdy, kto musi zareagować. W trakcie pisania programu ustawiamy próg `DEBUG` i widzimy wszystko; przed oddaniem zmieniamy go na `INFO` albo `WARNING`, nie dotykając ani jednego wpisu w kodzie. Metody dziennika noszą nazwy poziomów pisane małymi literami — `log.debug()`, `log.info()`, `log.warning()`, `log.error()`, `log.critical()` — a stałe progu wielkimi: `logging.DEBUG`, `logging.INFO` i tak dalej.

## Rejestrowanie wyjątków

Klauzula `except`, która pozwala programowi pracować dalej, powinna zostawić po błędzie pełną informację. Metoda `exception()` rejestruje komunikat na poziomie `ERROR` i dołącza do niego ślad wywołań bieżącego wyjątku — to samo, co `traceback.print_exc()` z poprzedniego podrozdziału, ale w ramach dziennika, z poziomem, nazwą źródła i konfigurowalnym miejscem docelowym. Wywołujemy ją wyłącznie wewnątrz klauzuli `except`:

```python title="wyjatek-dziennik.py"
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


def przetworz(wpisy):
    """Sumuje poprawne wpisy; błędne rejestruje w dzienniku ze śladem."""
    suma = 0
    for wpis in wpisy:
        try:
            suma += int(wpis)
        except ValueError:
            log.exception("pomijam błędny wpis %r", wpis)
    log.info("przetworzono %d wpisów, suma %d", len(wpisy), suma)
    return suma


przetworz(["1", "x", "3"])
```

```{ .text .no-copy }
ERROR __main__: pomijam błędny wpis 'x'
Traceback (most recent call last):
  File "wyjatek-dziennik.py", line 12, in przetworz
    suma += int(wpis)
            ~~~^^^^^^
ValueError: invalid literal for int() with base 10: 'x'
INFO __main__: przetworzono 3 wpisów, suma 4
```

Ślad znalazł się w dzienniku pod komunikatem, a program dokończył pracę i odnotował podsumowanie. Gdy ślad nie jest potrzebny, wystarczy `log.error()`; gdy potrzebny jest na innym poziomie, każda z metod przyjmuje argument `exc_info=True`. Wzorzec z tego przykładu — `except` na poziomie, który decyduje o kontynuowaniu, z `exception()` zamiast `pass` — jest właściwą odpowiedzią na antywzorzec połykania wyjątków z podrozdziału o stylu.

## Formatowanie komunikatów

W przykładzie wyżej komunikaty nie były f-stringami: zamiast `f"pomijam błędny wpis {wpis!r}"` napisaliśmy `"pomijam błędny wpis %r", wpis`. Moduł `logging` formatuje komunikat sam, wstawiając kolejne argumenty w miejsca **wieloznaczników** (ang. *placeholder*): `%s` wstawia wartość jak `str()`, `%r` jak `repr()`, `%d` liczbę całkowitą. Jest to starszy mechanizm formatowania z operatorem `%`, który w pełni poznamy w rozdziale o wejściu i wyjściu; w dzienniku wystarczą te trzy wieloznaczniki. <!-- TODO: link po powstaniu rozdziału o wejściu i wyjściu --> Powód, dla którego `logging` odstępuje od f-stringów, jest praktyczny: formatowanie następuje dopiero wtedy, gdy komunikat przeszedł próg. Wpis `log.debug("stan: %r", duza_struktura)` przy progu `INFO` kosztuje jedynie sprawdzenie progu, podczas gdy f-string zbudowałby reprezentację struktury za każdym razem, tylko po to, by ją odrzucić. Narzędzia analizujące dzienniki korzystają ponadto z faktu, że szablon komunikatu jest stały, a zmieniają się tylko argumenty.

Format wpisu z `basicConfig()` może zawierać także czas zdarzenia — pole `%(asctime)s`, którego postać ustala argument `datefmt=` w notacji funkcji `time.strftime()`, gdzie `%Y-%m-%d %H:%M:%S` oznacza datę i godzinę z sekundami. Przy progu `DEBUG` w dzienniku pojawia się także komunikat diagnostyczny:

```python title="czas.py"
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

log.debug("wczytano %d wierszy", 3)
log.info("początek przetwarzania")
log.info("koniec przetwarzania")
```

```{ .text .no-copy }
2026-09-13 10:15:42 DEBUG __main__: wczytano 3 wierszy
2026-09-13 10:15:42 INFO __main__: początek przetwarzania
2026-09-13 10:15:42 INFO __main__: koniec przetwarzania
```

Data i godzina zależą od chwili uruchomienia. Inne pola formatu — numer wiersza `%(lineno)d`, nazwa funkcji `%(funcName)s`, nazwa pliku `%(filename)s` — wymienia dokumentacja modułu w sekcji *LogRecord attributes*.

## Dziennik w pliku i dalsze możliwości

Dziennik w konsoli znika wraz z zamknięciem okna. Argument `filename=` funkcji `basicConfig()` kieruje wpisy do pliku, a `encoding="utf-8"` zapewnia poprawny zapis polskich znaków — z tych samych powodów, dla których `open()` w tym rozdziale zawsze otrzymywało kodowanie; domyślnie wpisy są dopisywane na końcu istniejącego pliku. Do plików wracamy w rozdziale o wejściu i wyjściu i tam pokażemy dziennik w pliku w działaniu. <!-- TODO: link po powstaniu rozdziału o wejściu i wyjściu --> Moduł `logging` potrafi znacznie więcej: kierować wpisy jednocześnie do konsoli i do pliku, dzielić pliki dziennika według rozmiaru albo daty, prowadzić osobne dzienniki dla modułów z osobnymi progami i przyjmować wpisy z wielu wątków, o czym wspomnimy w rozdziale o współbieżności. <!-- TODO: link po powstaniu rozdziału o współbieżności --> Wspólną zasadą pozostaje ta z tego podrozdziału: moduły tworzą dzienniki przez `getLogger(__name__)` i tylko rejestrują zdarzenia, a program główny konfiguruje raz, na początku, co i dokąd ma trafiać.

Na tym kończymy rozdział o wyjątkach. Błędy, które od rozdziału 2 czytaliśmy ze śladów wywołań, stały się obiektami: umiemy je przechwytywać, zgłaszać z własnym komunikatem, łączyć w łańcuchy i testować; instrukcja `with` zwalnia zasoby niezależnie od błędów, a debugger i dziennik pokazują, co program robił, zanim błąd wystąpił. Wszystkie te narzędzia będą stale obecne w dalszych rozdziałach — najpierw przy pracy z plikami, w rozdziale o wejściu i wyjściu. <!-- TODO: link po powstaniu rozdziału o wejściu i wyjściu -->
