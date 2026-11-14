# Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka

**Grupa:** L2 / L3 | **Zespół:** Z4 | **Repozytorium:** https://github.com/NikodemBoniecki/Alpha221
Sztuczna inteligencja, laboratorium | Collegium Da Vinci | rok akademicki 2026/2027

Projekt jest na etapie planowania. Nie napisaliśmy jeszcze kodu, nie pobraliśmy danych i nie mamy wyników. Parametry i próg opisane niżej są naszymi założeniami na początek pracy.

## 1. Problem *(rubryka A)*

Chcemy pomóc inwestorom indywidualnym zdecydować, jak podzielić kapitał między wybrane akcje, uwzględniając oczekiwany zwrot i ryzyko. Program przyjmie historyczne ceny dzienne spółek oraz limit ryzyka podany przez użytkownika. Następnie zaproponuje wagi spółek w portfelu i oszacuje jego zwrot oraz ryzyko. Na początek skupimy się na firmach z obszarów AI, gamedev i półprzewodników.

## 2. Dlaczego SI i dlaczego ta technika *(B · 7 pkt)*

Podstawowy problem portfelowy można rozwiązać klasyczną optymalizacją średnia-wariancja, więc nie zakładamy, że zwykły algorytm będzie za wolny. Wybraliśmy algorytm genetyczny, bo jest tematem z laboratorium i pozwoli nam porównać przeszukiwanie heurystyczne z rozwiązaniem Markowitza. Sieć neuronowa nie pasuje do naszego celu, bo nie prognozujemy etykiet ani cen. System ekspertowy wymagałby reguł, których nie mamy.

## 3. Dane *(B · 8 pkt)*

Rozważamy [Tiingo EOD Daily Prices API](https://www.tiingo.com/documentation/end-of-day), które udostępnia dzienne ceny pod adresem `/tiingo/daily/{ticker}/prices`. Nie wybraliśmy jeszcze konkretnego zbioru, tickerów ani zakresu dat. Na początek zakładamy od 50 do 100 spółek i do pięciu lat danych dziennych. API zwraca JSON domyślnie, obsługuje też CSV. Szczegóły dotyczące wyboru symboli, tokenu i limitów zapisaliśmy w [notatce o Tiingo](tiingo-data-notes.md).

Przed użyciem wybierzemy listę tickerów i dokładne daty, a potem sprawdzimy dostępność każdego symbolu przez endpoint metadanych. Do wyliczania zwrotów planujemy użyć pola `adjClose`, które zawiera korekty splitów i dywidend. Uporządkujemy ceny według dat, sprawdzimy braki i wyrównamy szeregi do wspólnego okresu. Następnie obliczymy dzienne stopy zwrotu, średnie zwroty i macierz kowariancji. Do ewaluacji podzielimy okres chronologicznie. Parametry dobierzemy na wcześniejszych danych, a wynik zmierzymy na późniejszych danych, których nie używaliśmy do strojenia.

Przed pobraniem musimy rozwiązać kwestię licencji. Aktualne warunki Tiingo nie pozwalają planom Starter i Trial na trwałe przechowywanie danych ani wyników pochodnych. Do testowania lub porównywania systemu AI/ML na danych Tiingo wymagana jest licencja Enterprise. Sam plan Power nie wystarczy do takiego benchmarku. Dlatego nie pobierzemy danych z Tiingo, dopóki nie uzyskamy wymaganej licencji. Jeśli jej nie dostaniemy, wybierzemy zbiór z licencją zezwalającą na zapis danych i ewaluację. Szczegóły i źródła są w [notatce o Tiingo](tiingo-data-notes.md), a pełne warunki opisuje [regulamin Tiingo](https://www.tiingo.com/tos/).

## 4. Rozwiązanie *(A · 10 pkt, B · 5 pkt)*

### Jak będzie działał program

1. Wczytamy ceny z lokalnego pliku albo, jeśli licencja na to pozwoli, pobierzemy je z Tiingo.
2. Sprawdzimy dane, uporządkujemy daty i obliczymy dzienne stopy zwrotu.
3. Wyliczymy średnie zwroty i macierz kowariancji.
4. Utworzymy populację portfeli. Każdy portfel będzie miał nieujemne wagi o sumie równej 1.
5. Ocenimy zwrot i ryzyko każdego portfela. Wybierzemy kandydatów, wykonamy krzyżowanie i mutację, a nowe wagi ponownie przeskalujemy do sumy 1.
6. Będziemy powtarzać te kroki do osiągnięcia limitu pokoleń albo kryterium zatrzymania.
7. Zwrócimy portfel o najwyższym oczekiwanym zwrocie spośród tych, które mieszczą się w limicie ryzyka. Jeśli takiego nie znajdziemy, program wyświetli informację o braku rozwiązania.
8. Te same miary policzymy dla portfela 1/N i modelu Markowitza.

### Model matematyczny

Oznaczmy wektor wag aktywów jako `w`, wektor średnich dziennych stóp zwrotu jako `μ`, a macierz kowariancji dziennych stóp zwrotu jako `Σ`. Dla portfela bez krótkiej sprzedaży wymagamy `wᵢ ≥ 0` oraz `Σᵢ wᵢ = 1`. Dzienny oczekiwany zwrot portfela wynosi `μₚ = μᵀw`, a dzienna wariancja `σₚ² = wᵀΣw`. Roczny zwrot oszacujemy jako średni zwrot dzienny pomnożony przez 252. Roczna zmienność wyniesie `σₚ,roczna = √(252 · wᵀΣw)`. To nasze założenia modelowe, które sprawdzimy podczas implementacji.

Chcemy maksymalizować oczekiwany zwrot `μᵀw` przy warunku `σₚ,roczna ≤ σmax`, gdzie `σmax` oznacza limit użytkownika. W funkcji oceny możemy zastosować karę `F(w) = μᵀw - λ · max(0, σₚ,roczna - σmax)²`, gdzie `λ` jest siłą kary. Sama kara nie gwarantuje spełnienia limitu, dlatego przed zwróceniem wyniku odrzucimy portfele, które go przekraczają.

Każdy osobnik będzie wektorem wag. Wylosujemy początkową populację i przeskalujemy wagi tak, aby sumowały się do 1. Planujemy selekcję turniejową, krzyżowanie ważone i mutację wag, po której ponownie je znormalizujemy. Wyniki porównamy z modelem Markowitza oraz portfelem równoważonym 1/N.

### Parametry na początek

Do pierwszych prób przyjmiemy populację 100 osobników, maksymalnie 200 pokoleń, turniej o rozmiarze 3, prawdopodobieństwo krzyżowania 0,8, prawdopodobieństwo mutacji 0,1 i ziarno losowości 42. Po pierwszych pomiarach zdecydujemy, czy je zmienić. Program będzie działał na CPU.

## 5. Ewaluacja *(B · 8 pkt)*

Nie mamy jeszcze wyników, bo nie zaczęliśmy implementacji i nie wybraliśmy danych. Nasz cel to zwracać tylko portfele spełniające limit ryzyka oraz osiągnąć medianę zwrotu równą co najmniej 95% wyniku Markowitza w pięciu przypadkach testowych. Porównamy też wyniki z portfelem 1/N. Wszystkie metody sprawdzimy na tych samych danych i przy tych samych ograniczeniach.

| Przypadek | Punkt odniesienia | Nasze rozwiązanie |
|---|---|---|
| 1 do 5, do ustalenia po wyborze danych | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |

Po eksperymentach wpiszemy tu wyniki i krótki wniosek. Na razie nie wiemy, czy algorytm genetyczny zbliży się do Markowitza ani czy pobije portfel 1/N.

## 6. Wymagania niefunkcjonalne *(A · 5 pkt)*

Program ma działać na CPU. Chcemy, żeby jeden test dla koszyka od 50 do 100 spółek trwał krócej niż 60 sekund, ale nie zmierzyliśmy jeszcze czasu. Przy tych samych danych, ustawieniach i ziarnie losowości program powinien zwracać ten sam wynik. Sprawdzimy, czy wejście zawiera wymagane kolumny, poprawne daty i skończone wartości. Brak danych lub tokenu ma powodować czytelny komunikat zamiast awarii.

## 7. Ograniczenia *(E · 4 pkt)*

Wynik zależy od wybranego okresu historycznego i nie przewiduje przyszłych cen. Nie uwzględniamy na razie kosztów transakcji, podatków, płynności ani ograniczeń sektorowych. Algorytm genetyczny może nie znaleźć najlepszego możliwego portfela, a przy bardzo niskim limicie może nie znaleźć żadnego dopuszczalnego portfela. Wyniku nie należy traktować jako porady inwestycyjnej. W dalszej pracy możemy dodać koszty transakcji, testy na kolejnych okresach i dodatkowe ograniczenia.

## 8. Zastosowania w praktyce *(E · 4 pkt)*

Optymalizację portfela wykorzystuje się przy podziale aktywów w narzędziach dla inwestorów, w zarządzaniu portfelami funduszy oraz przy analizie ryzyka i rebalansowaniu portfeli instytucjonalnych. W praktyce takie systemy biorą pod uwagę również koszty i inne ograniczenia. Nasz program będzie prostym prototypem na potrzeby zajęć, a nie narzędziem do podejmowania decyzji inwestycyjnych.

## 9. Zespół *(D · 8 pkt)*

Podzieliliśmy wstępnie odpowiedzialność za projekt. Możemy zmienić ten podział w trakcie pracy. Poniższa tabela pokazuje plan ról, a nie listę ukończonych zadań.

| Osoba | Zakres odpowiedzialności |
|---|---|
| Kacper Nowaczyk (31838) | Projekt algorytmu genetycznego i jego operatory |
| Adam Remfeld (31799) | Wybór licencjonowanego źródła, pozyskanie i przygotowanie danych |
| Nikodem Boniecki (31865) | Punkty odniesienia, ewaluacja, integracja i dokumentacja |

## 10. Uruchomienie *(C · 4 pkt)*

Nie dodaliśmy jeszcze kodu ani pliku `requirements.txt`, więc na razie nie da się uruchomić programu. W następnym etapie dodamy wersję Pythona, wymagane pakiety, instrukcję konfiguracji źródła danych, polecenie uruchomienia i miejsce zapisu wyników.

## 11. Narzędzia AI

Przy przygotowaniu dokumentów i sprawdzaniu informacji o Tiingo korzystaliśmy z ChatGPT. Nie używaliśmy go do pisania kodu ani tworzenia wyników eksperymentów, bo jeszcze ich nie mamy. Przed oddaniem sprawdzimy treść dokumentów i warunki licencji.
