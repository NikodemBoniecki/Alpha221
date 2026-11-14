# Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka

**Grupa:** L2 / L3 | **Zespół:** Z4 | **Repozytorium:** https://github.com/NikodemBoniecki/Alpha221
Sztuczna inteligencja, laboratorium | Collegium Da Vinci | rok akademicki 2026/2027

Mamy już uruchamialny szkielet programu. Na razie działa na danych syntetycznych albo na pliku CSV przygotowanym lokalnie. Nie wybraliśmy jeszcze rynkowego zbioru danych i nie mamy wyników eksperymentów.

## 1. Problem *(rubryka A)*

Chcemy pomóc inwestorom indywidualnym zdecydować, jak podzielić kapitał między wybrane akcje, uwzględniając oczekiwany zwrot i ryzyko. Program przyjmie historyczne ceny dzienne spółek oraz limit ryzyka podany przez użytkownika. Następnie zaproponuje wagi spółek w portfelu i oszacuje jego zwrot oraz ryzyko. Na początek skupimy się na firmach z obszarów AI, gamedev i półprzewodników.

## 2. Dlaczego SI i dlaczego ta technika *(B · 7 pkt)*

Podstawowy problem portfelowy można rozwiązać klasyczną optymalizacją średnia-wariancja, więc nie zakładamy, że zwykły algorytm będzie za wolny. Wybraliśmy algorytm genetyczny, bo jest tematem z laboratorium i pozwoli nam porównać przeszukiwanie heurystyczne z rozwiązaniem Markowitza. Sieć neuronowa nie pasuje do naszego celu, bo nie prognozujemy etykiet ani cen. System ekspertowy wymagałby reguł, których nie mamy.

## 3. Dane *(B · 8 pkt)*

Wybraliśmy [Huge Stock Market Dataset, wersję 3](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs). Kaggle podaje, że zbiór zawiera dzienne pliki CSV dla akcji i ETF-ów z USA, ma licencję CC0 i zajmuje około 809 MB. Opis zbioru podaje, że ceny są skorygowane o splity i dywidendy. Nie pobraliśmy jeszcze archiwum.

Do pierwszej ewaluacji planujemy wykorzystać NVDA, AMD, MSFT, EA i TTWO w okresie od 2012-01-03 do 2017-01-03. Po pobraniu sprawdzimy, czy każdy ticker ma wspólny zakres dat. Z plików wybierzemy datę i cenę zamknięcia, ułożymy serie w jeden szeroki CSV i sprawdzimy braki przed obliczeniem dziennych stóp zwrotu, średnich zwrotów i macierzy kowariancji. Dokładną liczbę wierszy wpiszemy po przygotowaniu pliku. Do ewaluacji użyjemy tych samych danych i ograniczeń dla GA, Markowitza oraz 1/N.

Tiingo nie jest naszym wybranym źródłem. Sprawdziliśmy jego warunki i zapisaliśmy je w [notatce o Tiingo](tiingo-data-notes.md). Nie pobierzemy stamtąd danych bez licencji pozwalającej na ich przechowywanie i ewaluację algorytmu.

## 4. Rozwiązanie *(A · 10 pkt, B · 5 pkt)*

### Jak będzie działał program

1. Wczytamy ceny z lokalnego pliku CSV. Domyślnie program tworzy przykładowe dane syntetyczne.
2. Sprawdzimy dane, uporządkujemy daty i obliczymy dzienne stopy zwrotu.
3. Wyliczymy średnie zwroty i macierz kowariancji.
4. Utworzymy populację portfeli. Każdy portfel będzie miał nieujemne wagi o sumie równej 1.
5. Ocenimy zwrot i ryzyko każdego portfela. Wybierzemy kandydatów, wykonamy krzyżowanie i mutację, a nowe wagi ponownie przeskalujemy do sumy 1.
6. Będziemy powtarzać te kroki do osiągnięcia limitu pokoleń albo kryterium zatrzymania.
7. Zwrócimy portfel o najwyższym oczekiwanym zwrocie spośród tych, które mieszczą się w limicie ryzyka. Jeśli takiego nie znajdziemy, program wyświetli informację o braku rozwiązania.
8. Te same miary policzymy dla portfela 1/N i modelu Markowitza.

### Model matematyczny

Oznaczmy wektor wag aktywów jako `w`, wektor średnich dziennych stóp zwrotu jako `μ`, a macierz kowariancji dziennych stóp zwrotu jako `Σ`. Dla portfela bez krótkiej sprzedaży wymagamy `wᵢ ≥ 0` oraz `Σᵢ wᵢ = 1`. Dzienny oczekiwany zwrot portfela wynosi `μₚ = μᵀw`, a dzienna wariancja `σₚ² = wᵀΣw`. Roczny zwrot oszacujemy jako średni zwrot dzienny pomnożony przez 252. Roczna zmienność wyniesie `σₚ,roczna = √(252 · wᵀΣw)`. To nasze założenia modelowe, które sprawdzimy podczas implementacji.

Chcemy maksymalizować oczekiwany zwrot `μᵀw` przy warunku `σₚ,roczna ≤ σmax`, gdzie `σmax` oznacza limit użytkownika. W obecnej implementacji dopuszczalne portfele są oceniane ich rocznym zwrotem. Portfele przekraczające limit otrzymują karę `-1000 - 1000 · (σₚ,roczna - σmax)`. Algorytm zapamiętuje i zwraca wyłącznie rozwiązanie spełniające limit.

Każdy osobnik jest wektorem wag. Program losuje początkową populację i normalizuje wagi tak, aby sumowały się do 1. Używa selekcji turniejowej, krzyżowania ważonego i mutacji wag, po której ponownie je normalizuje. Wyniki porównuje z modelem Markowitza oraz portfelem równoważonym 1/N.

### Parametry na początek

Do pierwszych prób przyjmiemy populację 100 osobników, maksymalnie 200 pokoleń, turniej o rozmiarze 3, prawdopodobieństwo krzyżowania 0,8, prawdopodobieństwo mutacji 0,1 i ziarno losowości 42. Po pierwszych pomiarach zdecydujemy, czy je zmienić. Program będzie działał na CPU.

## 5. Ewaluacja *(B · 8 pkt)*

Nie mamy jeszcze wyników na danych rynkowych. Program można uruchomić na danych syntetycznych, ale służą one tylko do sprawdzenia działania i nie będą traktowane jako wynik projektu. Nasz cel to zwracać wyłącznie portfele GA spełniające limit ryzyka oraz osiągnąć medianę rocznego zwrotu równą co najmniej 95% wyniku Markowitza w pięciu przypadkach. Każdy przypadek będzie obejmował jeden rok od 2012 do 2016. Porównamy też wyniki z portfelem 1/N. Wszystkie metody sprawdzimy na tych samych danych i przy tych samych ograniczeniach.

| Przypadek | Punkt odniesienia | Nasze rozwiązanie |
|---|---|---|
| 2012 | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |
| 2013 | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |
| 2014 | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |
| 2015 | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |
| 2016 | Markowitz i 1/N, brak wyników | Algorytm genetyczny, brak wyników |

Po eksperymentach wpiszemy tu wyniki i krótki wniosek. Na razie nie wiemy, czy algorytm genetyczny zbliży się do Markowitza ani czy pobije portfel 1/N.

## 6. Wymagania niefunkcjonalne *(A · 5 pkt)*

Program działa na CPU. Zakładamy, że jeden test dla wybranego koszyka pięciu spółek potrwa krócej niż 60 sekund, ale nie zmierzyliśmy jeszcze czasu na danych rynkowych. Przy tych samych danych, ustawieniach i ziarnie losowości algorytm genetyczny zwraca ten sam wynik. Program sprawdza wymagane kolumny, poprawne daty i wartości cen. Brak pliku albo niepoprawne dane powodują czytelny komunikat.

## 7. Ograniczenia *(E · 4 pkt)*

Wynik zależy od wybranego okresu historycznego i nie przewiduje przyszłych cen. Zbiór kończy się w 2017 roku, więc nie opisuje obecnego rynku i może zawierać błąd przeżywalności. Nie uwzględniamy na razie kosztów transakcji, podatków, płynności ani ograniczeń sektorowych. Algorytm genetyczny może nie znaleźć najlepszego możliwego portfela, a przy bardzo niskim limicie może nie znaleźć żadnego dopuszczalnego portfela. Wyniku nie należy traktować jako porady inwestycyjnej.

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

Wymagany jest Python 3.10 lub nowszy. Zależności instalujemy poleceniem `python -m pip install -r requirements.txt`. Program uruchamiamy z głównego katalogu repozytorium:

```bash
python -m alpha221
```

To polecenie używa przykładowych danych syntetycznych. Porównanie algorytmu genetycznego, Markowitza i portfela 1/N zapisuje do `results/comparison.csv`. Własne ceny można podać w pliku CSV, w którym pierwsza kolumna to `date`, a kolejne kolumny zawierają skorygowane ceny zamknięcia dla tickerów:

```bash
python -m alpha221 --input data/prices.csv --risk-limit 0.25
```

Program nie pobiera danych z internetu i nie wymaga tokenu. Wybrany zbiór pobierzemy osobno z Kaggle i przygotujemy jako CSV opisany wyżej.

## 11. Narzędzia AI

Przy przygotowaniu dokumentów, sprawdzaniu informacji o Tiingo, wyborze danych i początkowego szkieletu programu korzystaliśmy z ChatGPT. Nie używaliśmy go do tworzenia wyników eksperymentów. Przed oddaniem sprawdzimy kod, dokumenty i dane.
