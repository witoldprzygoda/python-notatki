# Modele danych — Pydantic

Treść żądania POST to JSON, którego kształtu nie znamy, dopóki go nie sprawdzimy. FastAPI opisuje ten kształt klasami biblioteki **Pydantic**: klasa z adnotowanymi polami — jak klasa danych z rozdziału 12 „Python Notatki” — sprawdza dane przy tworzeniu obiektu, zamienia typy, zgłasza wszystkie błędy naraz i opisuje sama siebie w dokumentacji. Ten podrozdział pokazuje Pydantic najpierw bez sieci, potem w trasach.

## Model i walidacja

```python title="model.py"
import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class Produkt(BaseModel):
    id: int
    nazwa: str = Field(min_length=1)
    kategoria: str
    cena: float = Field(gt=0)
    stan: int = Field(ge=0, default=0)

    @field_validator("nazwa")
    @classmethod
    def pojedyncze_spacje(cls, wartosc):
        return " ".join(wartosc.split())


class ProduktScisly(Produkt):
    model_config = ConfigDict(extra="forbid")


produkt = Produkt(id=1, nazwa="  Python.   Wprowadzenie ", kategoria="książki", cena="59")
print(produkt)
print(produkt.cena, type(produkt.cena).__name__, produkt.model_dump())
print(produkt.model_dump_json(exclude={"stan"}))
print(Produkt.model_validate({"id": 2, "nazwa": "Algorytmy", "kategoria": "książki", "cena": 89, "waga": 0.4}))
print(Produkt.model_validate_json('{"id": 3, "nazwa": "Słuchawki", "kategoria": "elektronika", "cena": 249, "stan": 8}').stan)
try:
    Produkt(id="x", nazwa="", kategoria="książki", cena=-1)
except ValidationError as blad:
    print(blad.error_count(), "błędy:")
    for wpis in blad.errors():
        print(" ", wpis["loc"], wpis["type"], "—", wpis["msg"])
try:
    ProduktScisly(id=2, nazwa="Algorytmy", kategoria="książki", cena=89, waga=0.4)
except ValidationError as blad:
    print(blad.errors()[0]["type"], blad.errors()[0]["loc"])
print(json.dumps(Produkt.model_json_schema()["properties"]["cena"]))
```

```{ .text .no-copy }
id=1 nazwa='Python. Wprowadzenie' kategoria='książki' cena=59.0 stan=0
59.0 float {'id': 1, 'nazwa': 'Python. Wprowadzenie', 'kategoria': 'książki', 'cena': 59.0, 'stan': 0}
{"id":1,"nazwa":"Python. Wprowadzenie","kategoria":"książki","cena":59.0}
id=2 nazwa='Algorytmy' kategoria='książki' cena=89.0 stan=0
8
3 błędy:
  ('id',) int_parsing — Input should be a valid integer, unable to parse string as an integer
  ('nazwa',) string_too_short — String should have at least 1 character
  ('cena',) greater_than — Input should be greater than 0
extra_forbidden ('waga',)
{"exclusiveMinimum": 0, "title": "Cena", "type": "number"}
```

Klasa dziedziczy po `BaseModel`, a pola opisujemy adnotacjami — `int`, `str`, `float` albo typ z wartością domyślną. `Field()` dodaje ograniczenia — minimalną długość, `gt`/`ge` dla liczb — i wartość domyślną. Pydantic działa w trybie łagodnym (ang. *lax mode*): tekst `"59"` przyjmuje jako `59.0`, bo daje się bez straty zamienić na liczbę, ale odrzuca `"x"`. Metoda z dekoratorem `@field_validator` dostaje wartość pola po sprawdzeniu typu i może ją zmienić — tu ujednolica spacje w nazwie. `model_dump()` zwraca słownik, `model_dump_json()` — tekst JSON; `model_validate()` i `model_validate_json()` idą w drugą stronę. Pola, których model nie zna, są domyślnie pomijane, a konfiguracja `extra="forbid"` czyni je błędem. `ValidationError` zbiera wszystkie błędy naraz: każdy z położeniem, rodzajem i komunikatem — to ten sam kształt, który FastAPI odsyła z kodem `422`. Ostatni wiersz pokazuje, że ograniczenia pola trafiają do **schematu** (ang. *schema*) w standardzie JSON Schema, z którego korzysta dokumentacja OpenAPI.

## Treść żądania i model odpowiedzi

```python title="zamowienia.py"
from fastapi import FastAPI, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from aplikacja import PRODUKTY


class NoweZamowienie(BaseModel):
    produkt_id: int
    ilosc: int = Field(ge=1)


class Zamowienie(NoweZamowienie):
    id: int
    wartosc: float


class ProduktKrotko(BaseModel):
    id: int
    nazwa: str
    cena: float


app = FastAPI()
ZAMOWIENIA = []


@app.get("/produkty/{produkt_id}", response_model=ProduktKrotko)
def produkt(produkt_id: int):
    return PRODUKTY[produkt_id]


@app.post("/zamowienia", status_code=status.HTTP_201_CREATED, response_model=Zamowienie)
def zloz_zamowienie(nowe: NoweZamowienie, response: Response):
    produkt = PRODUKTY[nowe.produkt_id]
    zamowienie = Zamowienie(id=len(ZAMOWIENIA) + 1, wartosc=nowe.ilosc * produkt["cena"], **nowe.model_dump())
    ZAMOWIENIA.append(zamowienie)
    response.headers["Location"] = f"/zamowienia/{zamowienie.id}"
    return zamowienie


klient = TestClient(app)
print(klient.get("/produkty/1").json())
odpowiedz = klient.post("/zamowienia", json={"produkt_id": 1, "ilosc": 2})
print(odpowiedz.status_code, odpowiedz.headers["location"], odpowiedz.json())
print(klient.post("/zamowienia", json={"produkt_id": "1", "ilosc": 2.0}).json())
for tresc in ({"produkt_id": 1}, {"produkt_id": 1, "ilosc": 0}, {"produkt_id": "x", "ilosc": "y"}):
    odpowiedz = klient.post("/zamowienia", json=tresc)
    print(odpowiedz.status_code, [(blad["loc"], blad["type"]) for blad in odpowiedz.json()["detail"]])
odpowiedz = klient.post("/zamowienia", content="to nie JSON", headers={"Content-Type": "application/json"})
print(odpowiedz.status_code, odpowiedz.json()["detail"][0]["type"])
```

```{ .text .no-copy }
{'id': 1, 'nazwa': 'Python. Wprowadzenie', 'cena': 59.0}
201 /zamowienia/1 {'produkt_id': 1, 'ilosc': 2, 'id': 1, 'wartosc': 118.0}
{'produkt_id': 1, 'ilosc': 2, 'id': 2, 'wartosc': 118.0}
422 [(['body', 'ilosc'], 'missing')]
422 [(['body', 'ilosc'], 'greater_than_equal')]
422 [(['body', 'produkt_id'], 'int_parsing'), (['body', 'ilosc'], 'int_parsing')]
422 json_invalid
```

Parametr funkcji o typie modelu Pydantic oznacza dla FastAPI treść żądania: framework czyta JSON, buduje obiekt `NoweZamowienie` — w trybie łagodnym, więc `"1"` i `2.0` stają się liczbami całkowitymi — i przekazuje go funkcji, a przy błędzie odpowiada `422` z listą, w której `loc` zaczyna się od `body`. Niepoprawny JSON to także `422`, z rodzajem `json_invalid`. `response_model` opisuje odpowiedź: FastAPI przepuszcza przez model to, co funkcja zwróciła — obiekt Pydantic albo słownik — i odsyła tylko pola modelu, dlatego `ProduktKrotko` ucina kategorię i stan; ten sam skutek daje adnotacja zwracanego typu `-> ProduktKrotko`. Model odpowiedzi dziedziczy po modelu żądania, żeby nie powtarzać pól, a `status_code` w dekoratorze ustala kod dla udanej odpowiedzi. Parametr typu `Response` daje dostęp do nagłówków odpowiedzi — tu `Location` po utworzeniu zasobu, jak w rozdziale 14.

## Modele zagnieżdżone i schematy

```python title="koszyk.py"
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class Pozycja(BaseModel):
    produkt_id: int
    ilosc: int = Field(ge=1)


class Koszyk(BaseModel):
    klient_id: int
    pozycje: list[Pozycja] = Field(min_length=1)
    uwagi: str | None = None


app = FastAPI()


@app.post("/koszyki")
def przyjmij(koszyk: Koszyk):
    return {"pozycji": len(koszyk.pozycje), "sztuk": sum(pozycja.ilosc for pozycja in koszyk.pozycje), "uwagi": koszyk.uwagi}


klient = TestClient(app)
print(klient.post("/koszyki", json={"klient_id": 1, "pozycje": [{"produkt_id": 1, "ilosc": 2}, {"produkt_id": 3, "ilosc": 1}]}).json())
odpowiedz = klient.post("/koszyki", json={"klient_id": 1, "pozycje": [{"produkt_id": 1, "ilosc": 0}]})
print(odpowiedz.status_code, odpowiedz.json()["detail"][0]["loc"])
print(klient.post("/koszyki", json={"klient_id": 1, "pozycje": []}).json()["detail"][0]["msg"])
schematy = klient.get("/openapi.json").json()["components"]["schemas"]
print(list(schematy))
print(schematy["Koszyk"]["required"], schematy["Koszyk"]["properties"]["pozycje"])
```

```{ .text .no-copy }
{'pozycji': 2, 'sztuk': 3, 'uwagi': None}
422 ['body', 'pozycje', 0, 'ilosc']
List should have at least 1 item after validation, not 0
['HTTPValidationError', 'Koszyk', 'Pozycja', 'ValidationError']
['klient_id', 'pozycje'] {'items': {'$ref': '#/components/schemas/Pozycja'}, 'type': 'array', 'minItems': 1, 'title': 'Pozycje'}
```

Pole typu `list[Pozycja]` sprawdza każdy element listy jako model `Pozycja`, a `loc` błędu prowadzi do konkretnego elementu: `body`, `pozycje`, indeks `0`, pole `ilosc`. Pole `str | None` z wartością domyślną jest opcjonalne. W opisie OpenAPI każdy model staje się schematem w `components.schemas`, na który trasy się powołują (dwa pozostałe schematy opisują odpowiedź `422`) — dokumentacja pokazuje więc dokładnie te pola, które kod przyjmuje, z listą wymaganych i ograniczeniami. Modele Pydantic przydają się także poza FastAPI: do sprawdzania pliku konfiguracyjnego, odpowiedzi cudzego API albo wierszy z pliku CSV, zanim program zacznie na nich liczyć.
