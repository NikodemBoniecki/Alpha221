# Dokumentacja projektu Alpha221

**Projekt:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
**Kurs:** Sztuczna inteligencja, laboratorium | Collegium Da Vinci | 2026/2027
**Stan tej dokumentacji:** 2026-11-21

## 1. Cel i zakres

Alpha221 jest konsolowym prototypem do porównywania algorytmu genetycznego (GA), optymalizacji Markowitza i portfela równoważonego 1/N. Dla danych tygodniowych GA maksymalizuje szacowane prawdopodobieństwo dodatniego skumulowanego zwrotu portfela w horyzoncie 6 miesięcy przy podanym przez użytkownika limicie rocznej zmienności.

Koszyk ma pulę 15 spółek oraz dwa ETF-y: SPY na S&P 500 i ETFBW20TR.WA na WIG20TR. GA wybiera dokładnie 10 spółek. Na spółki przypada 80% portfela, na ETF-y 20%. Waga każdej wybranej spółki wynosi co najmniej 1% i najwyżej 20% całego portfela; każdy ETF otrzymuje co najmniej 1%. Markowitz stosuje te same budżety, limit 20% na spółkę i minima ETF-ów, ale może użyć dowolnej liczby spółek z puli. Portfel 1/N dzieli 80% równo między wszystkie 15 spółek oraz 20% po równo między dwa ETF-y. Ograniczenia te są zaimplementowane w optymalizatorach dla docelowego koszyka.

Projekt jest pracą edukacyjną i nie służy do podejmowania decyzji inwestycyjnych.

## 2. Koszyk aktywów

| Ticker | Aktywo | Waluta notowania |
|---|---|---|
| AAPL | Apple | USD |
| MSFT | Microsoft | USD |
| NVDA | NVIDIA | USD |
| JPM | JPMorgan Chase | USD |
| KO | Coca-Cola | USD |
| CDR.WA | CD Projekt | PLN |
| TTWO | Take-Two Interactive | USD |
| UBI.PA | Ubisoft | EUR |
| AMD | Advanced Micro Devices | USD |
| ASML | ASML | USD |
| XTB.WA | XTB | PLN |
| PKN.WA | ORLEN | PLN |
| ASB.WA | ASBISc Enterprises | PLN |
| CBF.WA | cyber_Folks | PLN |
| TSLA | Tesla | USD |
| SPY | SPDR S&P 500 ETF | USD |
| ETFBW20TR.WA | BETA ETF WIG20TR | PLN |

Koszyk uwzględnia sześć instrumentów w PLN, jeden w EUR i dziesięć w USD. Kurs USDPLN=X jest podany jako PLN za 1 USD; EURUSD=X jako USD za 1 EUR.

## 3. Źródło i zasady użycia danych

Dane są pobierane z Yahoo Finance przez bibliotekę yfinance. yfinance jest nieoficjalnym narzędziem społecznościowym, nie jest powiązane z Yahoo i opisuje swoje zastosowanie jako badawcze i edukacyjne. Dokumentacja biblioteki wskazuje też, że Yahoo Finance API jest przeznaczone do użytku osobistego. Yahoo oznacza udostępniane informacje jako informacyjne i zabrania ich redystrybucji. Przed innym niż zamknięty pokazem edukacyjnym należy ponownie sprawdzić warunki źródła. [Dokumentacja yfinance](https://github.com/ranaroussi/yfinance/blob/main/README.md) · [Warunki Yahoo](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) · [Źródła i opóźnienia notowań](https://help.yahoo.com/kb/finance/article-exchanges-data-delays-sln2310.html)

Projekt nie używa tokenu API. Pobranie danych nie ma gwarantowanego SLA ani opublikowanego w tym projekcie limitu zapytań. Dostępność i opóźnienie zależą od rynku oraz dostawcy danych.

Zrzuty cen są ignorowane przez Git i nie powinny być commitowane ani redystrybuowane. Do odtworzenia należy uruchomić pobieracz lokalnie.

## 4. Pobieranie i przygotowanie cen

Pobieracz znajduje się w `alpha221/market_data.py`. Polecenie `python -m alpha221.market_data` domyślnie pobiera względny okres `2y` dla wszystkich 17 instrumentów, USDPLN=X i EURUSD=X. Do odtworzenia konkretnego zbioru należy użyć stałych dat `--start` i `--end`; data końcowa jest wyłączna.

1. Ceny skorygowane o działania korporacyjne są pobierane jako `Adj Close`, przy `auto_adjust=False` i `repair=False`. Dla najnowszego kursu jednostkowego pobierane jest `Close`. Pola dywidend i splitów są pobierane i raportowane osobno.
2. Ceny w PLN są dzielone przez USDPLN=X. Ceny w EUR są mnożone przez EURUSD=X. USD pozostaje bez zmiany.
3. Kurs FX jest dopasowywany do sesji instrumentu. Przy braku kursu z dokładnej daty wolno użyć ostatniego kursu z wcześniejszej daty. Ceny akcji i ETF-ów nie są uzupełniane.
4. Zbiór dzienny zawiera tylko daty, na które każdy instrument ma rzeczywiste notowanie. Brak kolumny, pusta seria, niepoprawne ceny lub zbyt mała liczba wspólnych dat zatrzymują pobieranie z błędem; ticker nie jest po cichu usuwany.
5. Zbiór tygodniowy wybiera ostatnią kompletną wspólną sesję w każdym tygodniu kończącym się w piątek. Etykietą wiersza jest piątek kończący tydzień, a osobny raport zachowuje faktyczną datę źródłową i opóźnienie względem piątku.
6. Metadane Yahoo są porównywane z oczekiwanym symbolem, walutą, typem instrumentu i strefą giełdy. Niezgodność zatrzymuje audyt.
7. Dla stałego okna pobieracz dodaje jednodniowy bufor zapytania po obu stronach, a następnie jawnie przycina wynik do żądanych dat. Zapobiega to pomijaniu końcowej sesji europejskich rynków w zbiorczym zapytaniu yfinance.
8. Manifest zapisuje parametry, wersje Pythona i bibliotek, schematy, liczbę wierszy, SHA-256 kodu pobieracza i każdego pliku wynikowego.

Domyślne polecenie dwuletnie zweryfikowane 2026-11-21 utworzyło 485 wspólnych sesji dziennych od 2024-11-21 do 2026-11-20 oraz 105 cen tygodniowych, czyli 104 okresy zwrotu.

Audyt z 2026-11-21 objął okres 2019-11-21-2026-11-20. Zbiór ma 1703 wspólne sesje dzienne i 366 cen tygodniowych, czyli 365 wektorów zwrotu dla 17 instrumentów. Nie ma pustych, niedodatnich ani zduplikowanych cen, a kolejne daty tygodniowe dzieli zawsze 7 dni. Każdy potrzebny kurs FX pochodził z tego samego dnia. Spośród 366 tygodni 343 korzystały z ceny piątkowej, 20 z czwartkowej, 2 ze środowej i 1 z wtorkowej. Test potrzebuje 364 okresów, więc jeden pozostaje w zapasie.

Dane pozostają ignorowane przez Git. Dokładny zbiór można odtworzyć poleceniem:

~~~bash
python -m alpha221.market_data --start 2019-11-21 --end 2026-11-21 --minimum-common-rows 1600 --prices-output data/raw/prices_7y_usd.csv --weekly-output data/raw/prices_weekly_7y_usd.csv --latest-output data/raw/latest_prices_7y_usd.csv --audit-output results/market_data_audit_7y.csv --calendar-audit-output results/market_data_calendar_audit_7y.csv --manifest-output data/raw/market_data_manifest_7y.json
~~~

## 5. Pliki danych

Pobieracz tworzy lokalnie:

| Plik | Zawartość |
|---|---|
| data/prices.csv | Dzienny Adj Close w USD, tylko kompletne wspólne sesje |
| data/prices_weekly_usd.csv | Tygodniowe ceny w USD, etykiety piątków kończących tygodnie |
| data/raw/prices_7y_usd.csv | Siedmioletni dzienny zbiór do testu kroczącego |
| data/raw/prices_weekly_7y_usd.csv | Siedmioletni tygodniowy zbiór do testu kroczącego |
| data/latest_prices_usd.csv | Ostatnie Close w USD dla każdego instrumentu, do wyceny jednostkowej |
| results/market_data_audit.csv | Metadane instrumentu, zakres i kompletność, zdarzenia korporacyjne, korekty cen oraz statystyki FX |
| results/market_data_calendar_audit.csv | Etykieta tygodnia, rzeczywista data źródłowa i liczba dni do piątku |
| data/market_data_manifest.json | Parametry, wersje środowiska, źródło, schematy, liczby wierszy i sumy SHA-256 |

Katalogi data z wygenerowanymi cenami oraz results są ignorowane przez Git. Liczby z tego zrzutu są kontrolą kompletności, a nie wynikami optymalizacji.

## 6. Częstotliwość i annualizacja

Do głównego porównania przyjęta jest częstotliwość tygodniowa. Wyrównywanie dziennych notowań rynków z różnymi kalendarzami przez wypełnianie cen może wprowadzać sztuczne zerowe zwroty. Tygodniowa próbka używa wspólnej sesji z każdego tygodnia i nie wstawia takich cen. Różne godziny zamknięcia giełd nadal oznaczają, że ceny z tej samej daty nie są wyceną z tej samej chwili; tygodniowa próbka ogranicza problem świąt, ale go całkowicie nie usuwa. [Badanie synchronizacji zwrotów międzynarodowych rynków](https://www.sciencedirect.com/science/article/pii/S037842660000159X)

Wyniki tygodniowe są annualizowane przez 52 okresy: średni zwrot tygodniowy mnożony jest przez 52, a wariancja przez 52. Zmienność roczna to pierwiastek z annualizowanej wariancji. Dla częstotliwości dziennej stosowane jest 252. CLI przyjmuje jawny parametr --frequency daily albo --frequency weekly i sprawdza odstępy dat. Nie wolno używać weekly cen z annualizacją daily.

## 7. Obliczenia

Dla ceny skorygowanej w USD P(i,t) prosty zwrot instrumentu i w okresie t wynosi:

~~~text
r(i,t) = P(i,t) / P(i,t-1) - 1
~~~

Z tych zwrotów liczone są średnie zwroty μ oraz macierz kowariancji Σ. Dla wag portfela w i liczby okresów w roku A roczny zwrot szacowany jest jako A · μᵀw, a roczna zmienność jako √(A · wᵀΣw). W tej wersji A wynosi 52 dla tygodni i 252 dla sesji dziennych. Zwrot jest estymacją średniej historycznej, nie prognozą.

## 8. Obecne modele

### Uzgodniony model docelowy

GA wybiera dokładnie 10 z 15 spółek. Każda ma wagę 1-20%, a ich suma wynosi 80%. Dwa ETF-y zajmują pozostałe 20%, po co najmniej 1% każdy. Portfel nie może przekroczyć podanego limitu rocznej zmienności. GA maksymalizuje oszacowane prawdopodobieństwo dodatniego zwrotu w USD po 26 tygodniach.

Markowitz używa tych samych budżetów 80/20, limitu 20% na spółkę oraz minimum 1% na każdy ETF, ale nie ma obowiązku trzymać dokładnie 10 spółek. Jako klasyczny punkt odniesienia maksymalizuje oczekiwany zwrot przy limicie zmienności. 1/N jest stałym punktem odniesienia: 80%/15 na każdą spółkę i 10% na każdy ETF. To porównuje trzy strategie z tymi samymi danymi i budżetami, ale nie izoluje wyłącznie jakości algorytmów, ponieważ cel GA (prawdopodobieństwo 6-miesięcznego zysku) różni się od celu Markowitza (oczekiwany zwrot). Wszystkie metody są oceniane wspólnymi miarami poza próbą. Dodatkowo zaimplementowano pełne przejście po 3003 podzbiorach 10 spółek jako kontrolę GA.

### Wybór wag i test poza próbą

Wagi są szacowane na kroczącym oknie 2 lat tygodniowych danych. Test poza próbą obejmuje 5 lat historii; co 26 tygodni modele wyznaczają wagi wyłącznie na danych dostępnych do tej daty, po czym portfel jest oceniany na następnych 26 tygodniach. Oznacza to 10 kolejnych okresów testowych. Końcowa kontrola z 2026-11-21 potwierdziła 366 tygodniowych cen (365 okresów zwrotu), co wystarcza do protokołu.

Wynik testu obejmuje skumulowany zwrot w USD, udział dodatnich okresów 6-miesięcznych, zrealizowaną zmienność oraz zgodność z limitem ryzyka dla GA, Markowitza i 1/N. Zbioru testowego nie wykorzystuje się do doboru wag ani ustawień algorytmu.

Estymator prawdopodobieństwa używa ruchomego bootstrapu blokowego ze wspólnych wektorów tygodniowych zwrotów. Dla każdego scenariusza losowane są kolejne bloki, z których składana jest ścieżka 26 tygodni; wynik portfela jest kapitalizowany tydzień po tygodniu. Długość 4 tygodni jest głównym ustawieniem, a bloki 2 i 8 tygodni służą do analizy wrażliwości. GA używa 1000 scenariuszy podczas optymalizacji, a raport porównawczy 10 000. Wynik jest estymacją historyczną, nie gwarancją.

### Pełne przeszukanie podzbiorów

Opcja `--exhaustive-subsets` sprawdza wszystkie 3003 zestawy 10 spółek. Dla każdego zestawu SLSQP wyznacza wagi Markowitza przy tych samych budżetach 80/20, limicie 1-20% na wybraną spółkę i minimum 1% na ETF. Potem program liczy dla każdego wykonalnego portfela to samo bootstrapowe prawdopodobieństwo co dla GA.

To pełne przeszukanie **składu**, ale nie globalne maksimum bootstrapowego prawdopodobieństwa po wszystkich możliwych wagach w każdym zestawie: wagi wewnątrz zestawu wyznacza Markowitz. Traktujemy wynik jako punkt kontrolny dla selekcji, nie jako matematyczną granicę celu GA. Opcja działa na pojedynczym tygodniowym oknie treningowym, nie w pięcioletnim teście kroczącym.

### Algorytm genetyczny

Chromosom zawiera po jednej wadze dla każdego z 17 aktywów. Populacja początkowa losowana jest z rozkładu Dirichleta. Wagi są nieujemne i normalizowane do sumy 1. Algorytm używa selekcji turniejowej, krzyżowania ważonego i mutacji.

Na wejściu tygodniowym GA maksymalizuje estymowane prawdopodobieństwo dodatniego skumulowanego zwrotu w 26 tygodniach. Fitness używa bootstrapu blokowego ze wspólnych tygodniowych wektorów zwrotu, z głównym blokiem długości 4 tygodni i 1000 scenariuszy podczas optymalizacji. Roczny limit zmienności jest twardym ograniczeniem; najlepszy znaleziony portfel musi go spełnić. Dla raportu prawdopodobieństwa każdej metody CLI używa 10 000 scenariuszy i podaje analizę wrażliwości dla bloków 2 i 8 tygodni. Dzienny tryb demonstracyjny nadal maksymalizuje estymowany zwrot, ponieważ cel 26-tygodniowy jest zdefiniowany dla tygodniowych zwrotów.

Chromosom ma 17 genów. Naprawa chromosomu wybiera 10 spółek z najwyższymi genami i projektuje ich wagi na ograniczony simpleks: suma 80%, minimum 1% i maksimum 20% na spółkę. Dwa ETF-y sumują się do 20%, każdy ma minimum 1%. Mechanizm jest zaimplementowany dla docelowego wejścia 17 aktywów.

Parametry domyślne: populacja 100, 200 pokoleń, rozmiar turnieju 3, prawdopodobieństwo krzyżowania 0,8, mutacji 0,1, skala mutacji 0,05, ziarno 42.

### Markowitz

Rozwiązanie SLSQP maksymalizuje estymowany zwrot przy ograniczeniu zmienności, budżetach 80/20, limicie 20% na spółkę i minimum 1% na każdy ETF. Nie wymusza dokładnie 10 aktywnych spółek.

### 1/N

Docelowy baseline dzieli 80% równo między 15 spółek i 20% równo między dwa ETF-y. Ta wersja jest zaimplementowana dla koszyka 17 aktywów. Dla syntetycznych danych demonstracyjnych bez koszyka projektu CLI zachowuje ogólne 1/N.

## 9. Uruchamianie

Zainstaluj zależności:

~~~bash
python -m pip install -r requirements.txt
~~~

Wymagany jest Python 3.10 lub nowszy. Pełną instrukcję zweryfikowano na Pythonie 3.12.10, NumPy 2.5.5, SciPy 1.18.1, pandas 3.1.1 i yfinance 1.8.0. Opcjonalnie przed instalacją można utworzyć środowisko poleceniem `python -m venv .venv`.

Pobierz dane i wygeneruj CSV:

~~~bash
python -m alpha221.market_data
~~~

Uruchom prototyp na danych tygodniowych:

~~~bash
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22
~~~

Pełne przeszukanie wszystkich zestawów spółek na dwuletnim oknie treningowym:

~~~bash
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22 --exhaustive-subsets
~~~

Uruchom pięcioletni test kroczący na siedmioletnim zbiorze:

~~~bash
python -m alpha221 --input data/raw/prices_weekly_7y_usd.csv --frequency weekly --walk-forward --risk-limit 0.22 --fold-output results/walk_forward_folds_7y.csv --summary-output results/walk_forward_summary_7y.csv
~~~

Test dopasowuje wagi na poprzednich 104 tygodniowych zwrotach i mierzy następne 26 tygodni. Powtarza to 10 razy. Powyższe polecenie zapisuje szczegóły do `results/walk_forward_folds_7y.csv`, a podsumowanie do `results/walk_forward_summary_7y.csv`.

Przy wejściu tygodniowym program wypisuje wagi, estymowany roczny zwrot, zmienność, szansę dodatniego zwrotu za 6 miesięcy oraz wrażliwość na długość bloku 2 i 8 tygodni. Główna estymacja używa bloku 4 tygodni. Wyniki zapisuje domyślnie do results/comparison.csv. Dzienny tryb demonstracyjny nie wylicza prawdopodobieństwa 6-miesięcznego. Użycie bez argumentu input uruchamia syntetyczne dane demonstracyjne, które nie są wynikiem projektu.

CLI obsługuje też risk-limit, seed, population, generations, yearly, output, probability-simulations i optimization-simulations. Domyślnie raport używa 10 000 ścieżek, a GA 1000 ścieżek na ocenę. Tryb yearly oblicza osobne statystyki dla każdego roku kalendarzowego. Nie jest to test poza próbą, ponieważ estymacja i ocena wykorzystują dane z tego samego roku.

## 10. Aktualny status ewaluacji

Dane rynkowe pobrano ponownie po rozszerzonym audycie i naprawie granicy daty w yfinance. Końcowy pełny przebieg poza próbą używał limitu ryzyka 22%, 104 tygodni treningu, 26 tygodni utrzymywania wag, domyślnej populacji GA 100, 200 pokoleń, 1000 ścieżek w optymalizacji i 10 000 w raporcie. Wyniki obejmują 10 okresów testowych od 2021-11-19 do 2026-11-13:

| Metoda | Łączny zwrot 5-letni | Dodatnie okresy 6-miesięczne | Średnia szacowana szansa zysku | Roczna zmienność z testu | Okresy w limicie 22% |
|---|---:|---:|---:|---:|---:|
| GA | 199.71% | 9/10 (90%) | 87.81% | 19.35% | 7/10 |
| Markowitz | 319.40% | 9/10 (90%) | 88.01% | 21.44% | 7/10 |
| 1/N | 177.29% | 9/10 (90%) | 75.86% | 19.94% | 8/10 |

To wynik historyczny, a nie dowód przewagi ani prognoza. GA i Markowitz spełniały szacowany limit 22% we wszystkich oknach treningowych, ale zrealizowana zmienność przekroczyła go w 3 z 10 okresów dla każdej z tych metod. Stały portfel 1/N przekroczył limit oszacowany na treningu w 2 oknach i limit zrealizowany w 2 okresach. Raporty CSV pozostają lokalne i są ignorowane przez Git.

Osobno wykonano pełne przeszukanie 3003 zestawów na dwuletnim oknie treningowym przy tym samym limicie 22%. Wagi każdego zestawu wyznaczył Markowitz, a wyniki rozpatrzonych portfeli oceniono bootstrapem:

| Metoda na oknie treningowym | Szacowany zwrot roczny | Zmienność roczna | Szacowane P(dodatni zwrot za 6 mies.) |
|---|---:|---:|---:|
| GA | 48.59% | 17.78% | 98.93% |
| Markowitz bez limitu liczby spółek | 61.34% | 22.00% | 98.02% |
| 1/N | 29.24% | 19.53% | 90.11% |
| Najlepszy z 3003 zestawów, wagi Markowitza | 53.69% | 18.34% | 98.96% |

Wszystkie 3003 zestawy dały wykonalny wynik Markowitza przy limicie 22%. GA i najlepszy zestaw z przeszukania osiągnęły niemal identyczne szacowane prawdopodobieństwo. To porównanie jest in-sample, a wewnątrz każdego zestawu wagi maksymalizują oczekiwany zwrot, nie bootstrapowe prawdopodobieństwo; nie stanowi więc dowodu globalnej optymalności GA ani pełnego testu poza próbą.

## 11. Ograniczenia i dalsza praca

- Pełne ograniczenia GA/Markowitza i pięcioletni test kroczący są zaimplementowane. Nie ma jeszcze alokacji kwoty kapitału na liczbę jednostek.
- Prawdopodobieństwo z bootstrapu jest estymacją na podstawie historii treningowej; pięcioletni test zawiera tylko 10 niezależnych okresów półrocznych.
- Zwroty i kowariancje są estymowane z krótkiego, dwuletniego okna; wyniki są wrażliwe na ten okres.
- Brakuje kosztów transakcji, podatków i modelu płynności; test nie uwzględnia kosztów rebalansowania.
- Tygodniowe ceny ograniczają niedopasowanie kalendarzy giełd, ale nie synchronizują godzin zamknięcia rynków.
- Dane mogą być opóźnione, zmienione lub czasowo niedostępne.
- Projekt nie jest poradą inwestycyjną.

Rola GA względem Markowitza wymaga uczciwej interpretacji: klasyczny Markowitz optymalizuje ciągłe wagi, ale można rozszerzyć go o wybór dyskretny. Wykonane przeszukanie obejmuje wszystkie 3003 składy, lecz jego wagi wewnątrz składu optymalizują oczekiwany zwrot. GA jest badaną heurystyką i nie gwarantuje globalnego optimum ani odporności na błędy estymacji. 1/N usuwa etap estymacji wag, ale nadal jest narażony na ryzyko rynku i nie jest odporny na każdy błąd danych. Limit 20% ogranicza ekspozycję na pojedynczą spółkę, ale nie eliminuje ryzyka wspólnego spadku rynku ani strat.

Estymator bootstrapowy i ograniczenia wag są zaimplementowane, ale wynik pozostaje wrażliwy na krótkie dwuletnie okno i niepewność historyczną. GA i Markowitz optymalizują różne funkcje celu; wspólny test porównuje ich wyniki poza próbą, ale nie izoluje samego wpływu algorytmu optymalizacji.
