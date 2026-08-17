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

Warto przypomnieć, że operator dzielenia `/` wykonuje dzielenie rzeczywiste (zmiennoprzecinkowe), a dzielenie z odcięciem części ułamkowej wykonuje się operatorem `//`. W Pythonie mamy również operator potęgowania `**`, nieobecny w językach C/C++. Nie ma za to operatorów inkrementacji `++` i dekrementacji `--`.

Priorytet operatora `:=` jest niższy od pozostałych operatorów — zatem kod bez nawiasów spowoduje najpierw ewaluację całego wyrażenia.

<!-- TODO: przykłady z PDF (zrzuty): priorytet := z a ** 2 > 6 -->

## Równość a identyczność, przynależność

Przechodząc do operatorów `is`, `is not` oraz `in`, `not in` — warto sprecyzować obszar ich zastosowania. Operator `==` porównuje wartość (równość) dwóch obiektów, natomiast operator `is` sprawdza, czy dwie zmienne wskazują na **ten sam obiekt w pamięci**. Oznacza to, że zazwyczaj używamy operatorów równości `==` i `!=`, chyba że porównujemy z `None`.

!!! note "sys.intern"
    W module sys jest funkcja `intern(string)`, która umieszcza argument — obiekt typu
    str — w tablicy łańcuchów „utrwalonych” w pamięci i zwraca taki właśnie łańcuch.
    Zabieg podobny do „utrwalonych” liczb całkowitych poprawia wydajność niektórych
    operacji, zwłaszcza dla słowników: gdy klucze są „utrwalone”, ich porównywanie
    może być wykonane na poziomie porównań wskaźników.

<!-- TODO: przykłady z PDF (zrzuty): intern() i adresy -->

W większości przypadków odrębnie utworzone obiekty, nawet o tej samej wartości, będą w różnych miejscach pamięci — zatem operator `is` zwróci False. Jeśli obiekty utworzymy poprzez operator przypisania (np. `a = b = "abc"` albo kolejno `a = "abc"`, `b = a`), to a i b będą w tym samym miejscu w pamięci. W takiej sytuacji, w przypadku obiektów **modyfikowalnych**, może nas spotkać niespodzianka: jeśli utworzymy pod dwiema nazwami obiekt listy w tym samym miejscu w pamięci, modyfikacja jednego z nich pociągnie modyfikację drugiego.

Na podsumowanie — przykłady z is (is not) oraz in (not in) dla prostych obiektów listy:

```python
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

Demonstrację działania in (not in) można oczywiście sprawdzić również na łańcuchach znakowych (proszę przetestować!).
