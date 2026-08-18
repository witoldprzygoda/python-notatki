# Operatory

Zestaw operatorów w języku Python jest bardzo podobny do tych spotykanych w innych językach programowania:

```{ .text .no-copy }
(arytmetyczne)              +  -  *  /  %  **  //
(przypisanie)               =  +=  -=  *=  /=  %=  //=  **=  &=  |=  ^=  >>=  <<=
(porównanie)                ==  !=  >  <  >=  <=
(logiczne)                  and  or  not
(bitowe)                    &  |  ^  ~  >>  <<
(identyczności)             is  is not
(przynależności)            in  not in
(przypisanie w wyrażeniu)   :=
```

Warto przypomnieć, że operator dzielenia `/` wykonuje dzielenie rzeczywiste (zmiennoprzecinkowe), a dzielenie z odcięciem części ułamkowej wykonuje się operatorem `//`. Iloraz całkowity i resztę jednocześnie zwraca funkcja wbudowana `divmod()` — `divmod(7, 2)` daje krotkę `(3, 1)`. W Pythonie mamy również operator potęgowania `**`, nieobecny w językach C/C++.

Nie ma za to operatorów inkrementacji `++` i dekrementacji `--`. Zapis `++x` jest mimo to poprawny — nie wynika to jednak z obecności „preinkrementacji”, lecz z wielokrotnego zastosowania jednoargumentowych operatorów `+` (nic nie zmienia) i `-` (zmienia znak na przeciwny), które można w dowolnej liczbie umieszczać przed obiektem. Ten sam zapis umieszczony **za** obiektem (`x++`) zostanie zgłoszony jako błąd składniowy.

## Operatory logiczne

Operatory `and`, `or` i `not` działają według strategii skróconego wartościowania i zwracają jeden z operandów, nie wartość logiczną — mechanizm ten opisuje szczegółowo sekcja o typie bool w podrozdziale [Typy proste](typy-proste.md). Hierarchia priorytetów: `not` wiąże najsilniej, potem `and`, na końcu `or`.

## Operatory bitowe

Operatory bitowe działają na binarnej reprezentacji liczb całkowitych:

```{ .python .no-copy }
>>> 0b1010 & 0b1100    # AND bitowy → 0b1000
8
>>> 0b1010 | 0b1100    # OR bitowy → 0b1110
14
>>> 0b1010 ^ 0b1100    # XOR bitowy → 0b0110
6
>>> ~0b1010            # NOT bitowy (inwersja: -(x+1))
-11
>>> 1 << 3             # przesunięcie w lewo (= 1 * 2**3)
8
>>> 16 >> 2            # przesunięcie w prawo (= 16 // 4)
4
```

Znajdują zastosowanie m.in. w kryptografii, programowaniu sieciowym i systemach wbudowanych; na tym etapie wystarczy wiedzieć, że istnieją.

## Porównania łańcuchowe i priorytety

W Pythonie składanie operatorów porównania (takich jak `<`, `>`, `<=`, `>=`) jest bardziej intuicyjne niż w wielu innych językach programowania, ponieważ działa jak w matematyce. Wyrażenie `s < d < f` jest oceniane w sposób „łańcuchowy” — Python rozumie je jako jedno logiczne porównanie, równoważne `s < d and d < f`. Ważną cechą tego zapisu jest to, że wartość `d` nie jest ewaluowana dwukrotnie, tylko raz — co ma znaczenie, jeśli jej obliczenie jest kosztowne lub wywołuje efekty uboczne:

```python title="porownania-lancuchowe.py"
def kosztowna_operacja():
    print("Obliczam d...")
    return 5

s = 2
f = 10
print(s < kosztowna_operacja() < f)   # Obliczam d... (tylko raz), True
```

Funkcja `kosztowna_operacja()` zostanie wywołana tylko raz, mimo że jej wynik bierze udział w dwóch porównaniach.

Warto zwrócić szczególną uwagę na priorytety operatorów, ponieważ wpływają one na kolejność obliczeń i ostateczny wynik wyrażenia. Rozważmy przykład:

```{ .python .no-copy }
>>> b, c, e, f, g = 2, 4, 5, 5, -1
>>> b + c <= e or f + g >= e == f == 5
False
```

Najpierw wykonywane jest `b + c`, a następnie porównanie `<= e` — tu `6 <= 5` daje `False`, więc leniwie oceniany operator `or` przechodzi do prawej strony. Ta zawiera porównanie łańcuchowe, które Python traktuje jako `(f + g >= e) and (e == f) and (f == 5)` — wszystkie trzy warunki musiałyby być spełnione; przy `g = -1` pierwszy z nich (`4 >= 5`) jest fałszywy. Wystarczy jednak podstawić `g = 0`, aby całe wyrażenie zwróciło `True`.

## Operator przypisania w wyrażeniu :=

Operator `:=` (ang. *walrus operator*, od Pythona 3.8) pozwala wykonać przypisanie w miejscu, w którym oczekiwane jest wyrażenie — np. wewnątrz warunku. Zwykłe przypisanie `=` jest w takich miejscach niedozwolone (to ochrona przed klasyczną pomyłką `=`/`==` znaną z języków C/C++), a objęcie operacji nawiasami sprawia, że staje się ona wyrażeniem o wartości.

Kanoniczny przykład — zapamiętanie wyniku obliczenia użytego w warunku:

```{ .python .no-copy }
>>> data = [0] * 12
>>> if (n := len(data)) > 10:
...     print(n)
...
12
```

Operator `:=` ma najniższy priorytet ze wszystkich operatorów, więc w zapisie `(x := wyrażenie)` przypisaniu podlega wartość **całego** wyrażenia; w wielu miejscach — m.in. jako samodzielna instrukcja — zapis bez nawiasów jest niedozwolony składniowo:

```{ .python .no-copy }
>>> a = 3
>>> (x := a ** 2 > 6)    # x przyjmuje wartość całego porównania
True
>>> x
True
>>> (y := a) ** 2 > 6    # nawiasy zmieniają zakres przypisania
True
>>> y
3
```

Przykład nadużycia operatora `:=`, pogarszającego czytelność kodu, pokazuje rozdział [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md).

## Równość a identyczność, przynależność

Przechodząc do operatorów `is`, `is not` oraz `in`, `not in` — warto sprecyzować obszar ich zastosowania. Operator `==` porównuje wartość (równość) dwóch obiektów, natomiast operator `is` sprawdza, czy dwie zmienne wskazują na **ten sam obiekt w pamięci**. Oznacza to, że zazwyczaj używamy operatorów równości `==` i `!=`, chyba że porównujemy z `None`.

!!! tip "Porównania z None: zawsze is"
    Zgodnie z zaleceniem PEP 8 brak wartości sprawdzamy zapisem `x is None`
    (oraz `x is not None`) — nigdy `x == None`. `None` jest jedynym obiektem swojego
    typu, więc test tożsamości jest tu jednoznaczny i szybszy, a ponadto odporny na
    obiekty, które nietypowo definiują własne porównania.

!!! note "sys.intern"
    W module sys jest funkcja `intern(string)`, która umieszcza argument — obiekt typu
    str — w tablicy łańcuchów „utrwalonych” w pamięci i zwraca taki właśnie łańcuch.
    Zabieg podobny do „utrwalonych” liczb całkowitych poprawia wydajność niektórych
    operacji, zwłaszcza dla słowników: gdy klucze są „utrwalone”, ich porównywanie
    może być wykonane na poziomie porównań wskaźników:

    ```{ .python .no-copy }
    >>> import sys
    >>> s1 = sys.intern('ala ma kota i psa')
    >>> s2 = sys.intern('ala ma kota i psa')
    >>> s1 is s2      # ten sam obiekt z tablicy utrwalonych
    True
    ```

W większości przypadków odrębnie utworzone obiekty, nawet o tej samej wartości, będą w różnych miejscach pamięci — zatem operator `is` zwróci False. Jeśli obiekty utworzymy poprzez operator przypisania (np. `a = b = "abc"` albo kolejno `a = "abc"`, `b = a`), to a i b będą w tym samym miejscu w pamięci. W takiej sytuacji, w przypadku obiektów **modyfikowalnych**, może nas spotkać niespodzianka: jeśli utworzymy pod dwiema nazwami obiekt listy w tym samym miejscu w pamięci, modyfikacja jednego z nich pociągnie modyfikację drugiego. Zjawisko to — wraz z kopiowaniem płytkim i głębokim — omawia szczegółowo rozdział 5 ([Referencje i kopiowanie](../05-typy-zlozone/referencje-i-kopiowanie.md)).

Na podsumowanie — przykłady z is (is not) oraz in (not in). Używamy tu **listy**, czyli modyfikowalnego kontenera omawianego w rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md); na razie wystarczy wiedzieć, że `["jablko", "banan"]` to sekwencja dwóch łańcuchów znakowych:

```python title="is-in.py"
x = ["jablko", "banan"]
y = ["jablko", "banan"]
z = x
print(x is z)        # True, gdyż x i z są w tym samym miejscu pamięci
print(x is y)        # False, x i y nie są w tym samym miejscu pamięci
print(x == y)        # True, bo zawartość x i y jest taka sama
print(x is not z)    # False
print(x is not y)    # True
print(x != y)        # False
print("banan" in x)      # True — element "banan" znajduje się w x
print("arbuz" not in x)  # True — elementu "arbuz" nie ma w x
```

Działanie in (not in) warto sprawdzić również na łańcuchach znakowych — operator bada wtedy zawieranie podciągu, np. `"ana" in "banan"` daje `True`.
