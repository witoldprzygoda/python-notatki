# Obiekty i pamięć

## Rozmiar obiektów i zarządzanie pamięcią

Utworzone obiekty zajmują pewien obszar pamięci. Nie wchodząc w szczegóły na ten moment, wielkość obiektu prostego dla typu wbudowanego można zbadać za pomocą funkcji `getsizeof()` z modułu `sys`. Najpierw zatem importujemy ten moduł, a potem używamy funkcji za pomocą zapisu `sys.jakas_funkcja()`.

<!-- TODO: przykład z PDF (zrzut): sys.getsizeof dla różnych typów -->

Alokacja i zwalnianie pamięci w Pythonie są automatyczne. Python używa dwóch strategii: **zliczanie referencji** (reference counting) i **odśmiecacz** (garbage collector). Odśmiecanie to proces, w którym interpreter zwalnia pamięć, gdy nie jest używana, aby udostępnić ją innym obiektom. Jeśli żadne odwołanie nie wskazuje na obiekt w pamięci (tj. nie jest on używany), garbage collector automatycznie usuwa ten obiekt z pamięci. Zliczanie odwołań polega na ustaleniu, ile razy do obiektu odwołują się inne obiekty w systemie. Po usunięciu odwołań zmniejsza się licznik odwołań do obiektu. Gdy licznik odwołań osiągnie zero, obiekt jest zwalniany. W Pythonie wywołania metod i referencje są przechowywane w pamięci stosu, a wszystkie obiekty wartości są przechowywane na prywatnej stercie.

## Niemodyfikowalność i identyfikacja obiektów

Obiekty prostych typów są **niemodyfikowalne**. Możemy być tym zaskoczeni, ponieważ w wielu językach programowania obiekt określonego typu powstaje i zajmuje określone miejsce (adres) w pamięci, niezależnie od tego, jaką ma zawartość. W Pythonie wszystko jest obiektem; unikatową sygnaturę obiektu można zbadać za pomocą funkcji `id()`. Zwróćmy uwagę, że po kolejnym przypisaniu innych wartości zmienia się adres — czyli powstaje kopia obiektu pod innym adresem, a nie modyfikacja zawartości obiektu, który wcześniej powstał.

Jak widać, konkretne nazwy (a, b, c…) wskazują raczej na adres w pamięci, w którym znajduje się ich wartość (też traktowana jako obiekt). Jeśli więc jakaś wartość nie ma dłużej dowiązania, jest przez Python automatycznie z pamięci usuwana. Przestudiujmy taki fragment:

```{ .python .no-copy }
>>> a = "xyz"   # tworzymy obiekt a
>>> id("xyz")   # sprawdzamy adres ciągu "xyz"
1549681491504
>>> id(a)       # adres obiektu a, taki sam jak "xyz"
1549681491504
>>> b = a       # tworzymy obiekt b z wartością a
>>> id(b)       # adres b — taki sam jak a
1549681491504
>>> a = "aaa"   # zmieniamy zawartość a
>>> id(a)       # adres się zmienił: a pokazuje na inny obszar pamięci
1549681490864
>>> b = a       # ponownie przypisujemy wartość a do b
>>> id(b)       # b ma teraz adres taki jak a (czyli łańcuch "aaa")
1549681490864
>>> id("xyz")   # co się stało z łańcuchem "xyz"?
1549681491312   # inny adres!
```

Jak widać, poprzedni łańcuch `"xyz"` został usunięty, gdyż ani obiekt a, ani obiekt b już na niego nie wskazywały — a skoro teraz pytamy, to utworzono w pamięci nowy `"xyz"`, pod nowym adresem. Adresy (prezentowane dziesiętnie) można oczywiście zrzutować poprzez `hex()`.

!!! note "Optymalizacja małych int"
    W przypadku niewielkich wartości typu int, z zakresu **[-5, 256]**, Python wykonuje
    pewną optymalizację — tworzy wstępnie obiekty o takiej wartości i potem ich używa.
    Jeśli utworzymy dwa obiekty niezależnie o wartości 257, mają one różne adresy;
    dla wartości 256 — identyczny adres.

<!-- TODO: przykłady z PDF (zrzuty): id() dla 257 i 256 -->

Można również odczytać (zrzutować) wskazany adres pamięci jako obiekt Pythona, korzystając z zewnętrznego modułu `ctypes`. Ilustrujący fragment kodu:

```python
import ctypes
a = "abcd"   # spróbuj z innymi typami
print("Wartosc -", a)
addr_a = id(a)
print("Adres pamieci - ", addr_a)
b = ctypes.cast(addr_a, ctypes.py_object).value
print("Wartosc odczytana z pamieci - ", b)
```

## Usuwanie obiektów: del

Choć zarządzanie czasem życia obiektów w Pythonie jest zautomatyzowane, istnieje słowo kluczowe `del` — można w ten sposób usuwać obiekty, elementy złożonych obiektów (np. list, słowników), czy nawet definicje klas. Składnia jest prosta: `del nazwa_usuwanego_elementu`.
