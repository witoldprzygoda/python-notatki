# Pierwsza aplikacja

Aplikacja FastAPI to obiekt klasy `FastAPI` i funkcje przypisane do adresów dekoratorami z rozdziału 6 „Python Notatki”. Ten podrozdział buduje najmniejszy sklep — trzy trasy do odczytu — i pokazuje, co framework robi sam: rozbiera ścieżkę, sprawdza typy, zamienia wynik funkcji na JSON i dokumentuje interfejs.

## Aplikacja i trasy

```python title="aplikacja.py"
"""Sklep w pamięci: trzy trasy do odczytu."""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Sklep", version="1.0")

PRODUKTY = {
    1: {"id": 1, "nazwa": "Python. Wprowadzenie", "kategoria": "książki", "cena": 59.0, "stan": 12},
    2: {"id": 2, "nazwa": "Algorytmy", "kategoria": "książki", "cena": 89.0, "stan": 5},
    3: {"id": 3, "nazwa": "Słuchawki", "kategoria": "elektronika", "cena": 249.0, "stan": 8},
}


@app.get("/")
def start():
    return {"komunikat": "Sklep działa"}


@app.get("/produkty")
def lista_produktow(kategoria: str | None = None, limit: Annotated[int, Query(ge=1, le=100)] = 10):
    wybrane = [produkt for produkt in PRODUKTY.values() if kategoria is None or produkt["kategoria"] == kategoria]
    return wybrane[:limit]


@app.get("/produkty/{produkt_id}")
def produkt(produkt_id: int):
    if produkt_id not in PRODUKTY:
        raise HTTPException(status_code=404, detail=f"nie ma produktu {produkt_id}")
    return PRODUKTY[produkt_id]
```

Dekorator `@app.get("/produkty")` wiąże funkcję z metodą HTTP i ścieżką — to **trasa** (ang. *route*), a funkcja to **funkcja obsługi** (ang. *path operation function*). Wynik funkcji — słownik, lista, liczba — FastAPI serializuje do JSON-a i wysyła z kodem `200`. Parametr w nawiasach klamrowych w ścieżce trafia do argumentu o tej samej nazwie jako **parametr ścieżki** (ang. *path parameter*); argumenty, których nie ma w ścieżce, framework czyta z zapytania jako **parametry zapytania** (ang. *query parameters*). Adnotacja typu jest umową: `produkt_id: int` oznacza, że framework zamieni tekst ze ścieżki na liczbę, a gdy się nie da — odpowie błędem, zanim funkcja zostanie wywołana. `Annotated` z modułu `typing` dołącza do typu dodatkowe informacje — tu `Query(ge=1, le=100)` z ograniczeniami wartości; wartość domyślna czyni parametr opcjonalnym. `HTTPException` przerywa obsługę i staje się odpowiedzią z podanym kodem.

## Pierwsze żądania

Żądania wysyłamy klientem testowym, omówionym w ostatniej sekcji tej strony:

```python title="pierwsze.py"
from fastapi.testclient import TestClient

from aplikacja import app

klient = TestClient(app)
odpowiedz = klient.get("/")
print(odpowiedz.status_code, odpowiedz.headers["content-type"], odpowiedz.json())
print(klient.get("/produkty", params={"kategoria": "książki"}).json())
print(klient.get("/produkty", params={"limit": 1}).json())
print(klient.get("/produkty/2").json())
for sciezka, parametry in (("/produkty/abc", None), ("/produkty", {"limit": 0}), ("/produkty/9", None), ("/nieznana", None)):
    odpowiedz = klient.get(sciezka, params=parametry)
    print(odpowiedz.status_code, odpowiedz.json())
print(klient.post("/").status_code, klient.post("/").json())
```

```{ .text .no-copy }
200 application/json {'komunikat': 'Sklep działa'}
[{'id': 1, 'nazwa': 'Python. Wprowadzenie', 'kategoria': 'książki', 'cena': 59.0, 'stan': 12}, {'id': 2, 'nazwa': 'Algorytmy', 'kategoria': 'książki', 'cena': 89.0, 'stan': 5}]
[{'id': 1, 'nazwa': 'Python. Wprowadzenie', 'kategoria': 'książki', 'cena': 59.0, 'stan': 12}]
{'id': 2, 'nazwa': 'Algorytmy', 'kategoria': 'książki', 'cena': 89.0, 'stan': 5}
422 {'detail': [{'type': 'int_parsing', 'loc': ['path', 'produkt_id'], 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'abc'}]}
422 {'detail': [{'type': 'greater_than_equal', 'loc': ['query', 'limit'], 'msg': 'Input should be greater than or equal to 1', 'input': '0', 'ctx': {'ge': 1}}]}
404 {'detail': 'nie ma produktu 9'}
404 {'detail': 'Not Found'}
405 {'detail': 'Method Not Allowed'}
```

Dwa pierwsze żądania z błędami nie dotarły do funkcji: tekst `abc` nie jest liczbą, a `limit=0` łamie ograniczenie, więc FastAPI odpowiedział kodem `422` i listą błędów — każdy z rodzajem (`type`), położeniem (`loc`: w ścieżce czy w zapytaniu, jaki parametr), komunikatem i odrzuconą wartością. Ten kształt jest jednakowy dla wszystkich tras. Brak produktu to nasz `HTTPException` z polem `detail`; nieznana ścieżka i metoda bez trasy dają `404` i `405` bez naszego udziału.

## Uruchomienie serwera

Aplikacja nie ma własnej pętli obsługi połączeń — uruchamia ją **serwer ASGI** (ang. *Asynchronous Server Gateway Interface*, standard łączący aplikacje Pythona z serwerami HTTP), którym jest uvicorn:

```powershell title="Terminal"
python -m uvicorn aplikacja:app --reload
```

```{ .text .no-copy }
INFO:     Will watch for changes in these directories: ['C:\\Users\\jan\\sklep']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [53292] using StatReload
INFO:     Started server process [20972]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:49324 - "GET /produkty/2 HTTP/1.1" 200 OK
```

Argument `aplikacja:app` to nazwa modułu i nazwa obiektu aplikacji w nim. Serwer nasłuchuje na porcie `8000` tylko dla tej maszyny; każde obsłużone żądanie zapisuje w dzienniku z adresem klienta, linią żądania i kodem. Opcja `--reload` ponownie ładuje aplikację po każdej zmianie pliku (dodatek `uvicorn[standard]` daje szybszą obserwację plików) — wygodna przy pisaniu, zbędna u odbiorcy. ++ctrl+c++ zatrzymuje serwer. Dodatek `fastapi[standard]` instaluje też polecenie `fastapi dev`, które robi to samo; `python -m uvicorn` nie wymaga niczego poza serwerem.

## Dokumentacja interfejsu

Przy uruchomionym serwerze adres `http://127.0.0.1:8000/docs` otwiera dokumentację interfejsu wygenerowaną z kodu: każdą trasę z parametrami, ich typami i ograniczeniami, przykładowe odpowiedzi i przycisk, który wysyła żądanie z przeglądarki.

<!-- TODO: screenshot — strona /docs (Swagger UI) aplikacji z trzema trasami i rozwiniętą trasą /produkty/{produkt_id} -->

Źródłem dokumentacji jest opis interfejsu w standardzie **OpenAPI** — dokument JSON pod adresem `/openapi.json`, z którego korzystają też generatory klientów i narzędzia do testów:

```python title="dokumentacja.py"
from fastapi.testclient import TestClient

from aplikacja import app

opis = TestClient(app).get("/openapi.json").json()
print(opis["info"], list(opis["paths"]))
for parametr in opis["paths"]["/produkty"]["get"]["parameters"]:
    print(parametr["name"], parametr["required"], parametr["schema"])
```

```{ .text .no-copy }
{'title': 'Sklep', 'version': '1.0'} ['/', '/produkty', '/produkty/{produkt_id}']
kategoria False {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'title': 'Kategoria'}
limit False {'type': 'integer', 'maximum': 100, 'minimum': 1, 'default': 10, 'title': 'Limit'}
```

Tytuł i wersja pochodzą z argumentów `FastAPI()`, nazwy parametrów, typy i ograniczenia — z adnotacji funkcji: `Query(ge=1, le=100)` stał się `minimum` i `maximum` w schemacie. Dokumentacja jest więc zawsze zgodna z kodem, bo nie istnieje osobno. Alternatywny widok tej samej treści jest pod adresem `/redoc`.

## Klient testowy

Skrypty tego rozdziału (poza jednym na trzeciej stronie) nie uruchamiają serwera: `TestClient(app)` z modułu `fastapi.testclient` wywołuje aplikację w tym samym procesie, a z zewnątrz wygląda jak `httpx.Client` z rozdziału 14 — te same metody `get()` i `post()`, argumenty `params`, `json`, `headers` i taki sam obiekt odpowiedzi. Adres bazowy `http://testserver` jest umowny, port nie jest potrzebny. Klient testowy służy testom z ostatniej strony rozdziału, a tutaj — pokazaniu zachowania aplikacji bez okna terminala z serwerem. Funkcje obsługi piszemy jako zwykłe `def`; FastAPI wykonuje je w puli wątków z rozdziału 15 „Python Notatki”, więc kilka żądań może być obsługiwanych równocześnie, a wersja `async def` ma sens dopiero z bibliotekami asynchronicznymi, których nie używamy.
