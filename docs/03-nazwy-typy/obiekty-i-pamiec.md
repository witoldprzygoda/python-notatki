# Obiekty i pamięć

## Rozmiar obiektów i zarządzanie pamięcią

Utworzone obiekty zajmują pewien obszar pamięci. Nie wchodząc w szczegóły na ten moment, wielkość obiektu prostego dla typu wbudowanego można zbadać za pomocą funkcji `getsizeof()` z modułu `sys`. Najpierw zatem importujemy ten moduł, a potem używamy funkcji za pomocą zapisu `sys.jakas_funkcja()`:

```{ .python .no-copy }
>>> import sys
>>> sys.getsizeof(0)       # 28
>>> sys.getsizeof('')      # 41
>>> sys.getsizeof('abc')   # 44
>>> sys.getsizeof([])      # 56
```

Podane wartości (w bajtach) dotyczą CPythona 3.14 w wersji 64-bitowej — w innych wersjach interpretera mogą się nieznacznie różnić. Widać, że nawet „puste” obiekty niosą narzut: obiekt w Pythonie przechowuje m.in. informację o typie i licznik referencji.

Alokacja i zwalnianie pamięci w Pythonie są automatyczne. Python używa dwóch strategii: **zliczanie referencji** (ang. *reference counting*) i **odśmiecacz** (ang. *garbage collector*). Odśmiecanie to proces, w którym interpreter zwalnia pamięć, gdy nie jest używana, aby udostępnić ją innym obiektom. Jeśli żadne odwołanie nie wskazuje na obiekt w pamięci (tj. nie jest on używany), garbage collector automatycznie usuwa ten obiekt z pamięci. Zliczanie odwołań polega na ustaleniu, ile razy do obiektu odwołują się inne obiekty w systemie. Po usunięciu odwołań zmniejsza się licznik odwołań do obiektu. Gdy licznik odwołań osiągnie zero, obiekt jest zwalniany. W Pythonie wywołania metod i referencje są przechowywane w pamięci stosu, a wszystkie obiekty wartości są przechowywane na prywatnej stercie.

## Niemodyfikowalność i identyfikacja obiektów

Obiekty prostych typów są **niemodyfikowalne**. Typy modyfikowalne — listę, słownik i zbiór — oraz konsekwencje ich semantyki referencji omawia rozdział [5. Typy złożone](../05-typy-zlozone/index.md). Możemy być tym zaskoczeni, ponieważ w wielu językach programowania obiekt określonego typu powstaje i zajmuje określone miejsce (adres) w pamięci, niezależnie od tego, jaką ma zawartość. W Pythonie wszystko jest obiektem; unikatową sygnaturę obiektu można zbadać za pomocą funkcji `id()`. Zwróćmy uwagę, że po kolejnym przypisaniu innych wartości zmienia się adres — czyli powstaje nowy obiekt pod innym adresem, a nie modyfikacja zawartości obiektu, który wcześniej powstał.

Konkretne nazwy (a, b, c…) wskazują na adres w pamięci, w którym znajduje się ich wartość (też traktowana jako obiekt). Przestudiujmy taki fragment:

```{ .python .no-copy }
>>> a = "xyz"   # nazwa a wskazuje na obiekt "xyz"
>>> id(a)       # adres obiektu wskazywanego przez a
1549681491504
>>> b = a       # b wskazuje na TEN SAM obiekt
>>> id(b)       # adres b — taki sam jak a
1549681491504
>>> a = "aaa"   # a wskazuje odtąd na NOWY obiekt
>>> id(a)       # adres się zmienił
1549681490864
>>> id(b)       # b nadal wskazuje na "xyz"
1549681491504
>>> b = a       # teraz i b wskazuje na "aaa"
>>> id(b)
1549681490864
```

Przypisanie `a = "aaa"` nie zmieniło obiektu `"xyz"` — utworzyło nowy obiekt i przepięło na niego referencję `a`; `b` do ostatniego kroku wskazywało obiekt poprzedni. Gdy jakaś wartość nie ma już żadnego dowiązania, jest przez Pythona automatycznie usuwana z pamięci (mechanizmy opisane wyżej). Adresy (prezentowane dziesiętnie) można zrzutować na zapis szesnastkowy poprzez `hex()`.

!!! warning "id() na literałach nie demonstruje zwalniania pamięci"
    Kuszące byłoby „przyłapanie” interpretera na zwalnianiu obiektu przez porównanie
    `id("xyz")` przed przepięciem nazw i po nim. Taki eksperyment jest jednak
    niemiarodajny: CPython **utrwala** (ang. *interning*) krótkie literały łańcuchowe
    wyglądające jak identyfikatory oraz małe liczby całkowite, więc obiekt `"xyz"`
    wcale nie znika — a dla łańcuchów nieutrwalanych wynik zależy od ponownego użycia
    zwolnionej pamięci, czyli jest przypadkowy. O utrwalaniu łańcuchów wspomina nota
    o `sys.intern` w podrozdziale [Operatory](operatory.md).

!!! note "Optymalizacja małych int"
    W przypadku niewielkich wartości typu int, z zakresu **[-5, 256]**, Python wykonuje
    pewną optymalizację — tworzy wstępnie obiekty o takiej wartości i potem ich używa.
    Jeśli utworzymy dwa obiekty niezależnie o wartości 257, mają one różne adresy;
    dla wartości 256 — identyczny adres:

    ```{ .python .no-copy }
    >>> a = 256
    >>> b = 256
    >>> a is b     # True — ten sam obiekt z pamięci podręcznej
    True
    >>> a = 257
    >>> b = 257
    >>> a is b     # False — dwa osobne obiekty
    False
    >>> a == b     # wartości są oczywiście równe
    True
    ```

    Jest to szczegół implementacji CPythona, nie część specyfikacji języka — nigdy
    nie należy polegać na `is` przy porównywaniu **wartości** (opis operatora w
    podrozdziale [Operatory](operatory.md)).

Można również odczytać (zrzutować) wskazany adres pamięci jako obiekt Pythona, korzystając z modułu `ctypes` z biblioteki standardowej. Ilustrujący fragment kodu:

```python title="ctypes-adres.py"
import ctypes
a = "abcd"   # spróbuj z innymi typami
print("Wartosc -", a)
addr_a = id(a)
print("Adres pamieci - ", addr_a)
b = ctypes.cast(addr_a, ctypes.py_object).value
print("Wartosc odczytana z pamieci - ", b)
```

## Usuwanie obiektów: del

Choć zarządzanie czasem życia obiektów w Pythonie jest zautomatyzowane, istnieje słowo kluczowe `del` — można w ten sposób usuwać obiekty, elementy złożonych obiektów (np. list czy słowników — rozdział [5. Typy złożone](../05-typy-zlozone/index.md)), czy nawet definicje klas. Składnia jest prosta: `del nazwa_usuwanego_elementu`. Warto pamiętać, że `del` usuwa **nazwę** (referencję), a nie bezpośrednio obiekt — obiekt zniknie z pamięci dopiero wtedy, gdy jego licznik referencji spadnie do zera.
