# Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka

**Grupa:** L2 / L3 · **Zespół:** Z4 · **Repozytorium:** https://github.com/NikodemBoniecki/Alpha221  
Sztuczna inteligencja — laboratorium · Collegium Da Vinci · rok akad. 2026/2027

> Status dokumentu: projekt jest na etapie planowania. Kod, pobrane dane, parametry końcowe i wyniki ewaluacji nie są jeszcze dostępne. Wartości opisane jako wstępne są celami do potwierdzenia podczas implementacji.

## 1. Problem *(rubryka A)*

Inwestor indywidualny, który wybiera kilka spółek, musi zdecydować, jak podzielić pomiędzy nie kapitał, aby uzyskać możliwie wysoki oczekiwany zwrot przy ograniczonym ryzyku. System przyjmie szeregi historycznych cen dziennych dla wybranych akcji oraz maksymalny poziom ryzyka użytkownika. Zwróci wagi aktywów w portfelu oraz oszacowane ryzyko i oczekiwany zwrot. Początkowy zakres obejmuje akcje związane z AI, gamedev i półprzewodnikami.

## 2. Dlaczego SI i dlaczego ta technika *(B · 7 pkt)*

Podstawowy problem średnia-wariancja można rozwiązać klasyczną metodą optymalizacji, więc dla planowanej skali nie twierdzimy, że algorytm tradycyjny jest zbyt kosztowny. Algorytm genetyczny wybraliśmy jako technikę SI z zakresu laboratorium, aby zbadać heurystyczne przeszukiwanie przestrzeni wag i porównać je z rozwiązaniem Markowitza. Sieć neuronowa nie jest tu naturalnym wyborem, ponieważ projekt nie przewiduje uczenia modelu do prognozowania etykiet ani cen; system ekspertowy wymagałby ręcznego zapisania reguł, które nie są głównym przedmiotem problemu.

## 3. Dane *(B · 8 pkt)*

Planowanym źródłem danych jest [Tiingo EOD Daily Prices API](https://www.tiingo.com/documentation/end-of-day), endpoint `/tiingo/daily/{ticker}/prices`. Lista tickerów i dokładny zakres dat nie zostały jeszcze ustalone. Zakładamy około 50–100 spółek oraz do pięciu lat cen dziennych w odpowiedziach JSON; dokładny rozmiar danych zależy od wybranych symboli i okresu. Dane nie zostały jeszcze pobrane. Zespół uzyska token API i przechowa go lokalnie jako zmienną środowiskową, a nie w repozytorium.

Przed obliczeniami dane zostaną uporządkowane według dat, sprawdzone pod kątem braków i wyrównane dla wspólnego okresu. Z cen zostaną wyliczone dzienne stopy zwrotu, na których obliczymy średnie zwroty i macierz kowariancji. Podział ewaluacyjny będzie chronologiczny: parametry i wybór rozwiązania będą oparte na wcześniejszym okresie, a wynik sprawdzimy na późniejszym okresie, którego algorytm nie używał do dostrajania. Konkretne daty i reguła obsługi braków zostaną zapisane po pobraniu danych. Ze względu na oznaczenie planu Tiingo jako „Internal Use Only” surowe odpowiedzi API nie będą umieszczane w repozytorium; przed publicznym udostępnieniem wyników zespół sprawdzi warunki użycia z prowadzącym. [Warunki i limity Tiingo](https://www.tiingo.com/pricing) · [Warunki użycia API](https://www.tiingo.com/tos/).

## 4. Rozwiązanie *(A · 10 pkt, B · 5 pkt)*

### Schemat działania

1. Wczytaj ceny z lokalnego pliku lub pobierz je z Tiingo dla wybranych tickerów.
2. Sprawdź wejście, wyrównaj daty i wylicz dzienne stopy zwrotu.
3. Oblicz wektor średnich zwrotów oraz macierz kowariancji.
4. Wygeneruj populację portfeli; każdy osobnik jest wektorem nieujemnych wag, których suma wynosi 1.
5. Oceń zwrot i ryzyko każdego portfela; wybieraj osobniki do reprodukcji, wykonuj krzyżowanie i mutację, a wagi normalizuj ponownie do sumy 1.
6. Powtarzaj ewolucję do osiągnięcia limitu pokoleń lub kryterium zatrzymania.
7. Spośród rozwiązań spełniających limit zwróć portfel o najwyższym oczekiwanym zwrocie. Jeśli nie znaleziono rozwiązania dopuszczalnego, zgłoś ten fakt zamiast zwracać portfel naruszający limit.
8. Oblicz te same metryki dla portfela 1/N i modelu Markowitza oraz zapisz porównanie.

### Model matematyczny i algorytm

Niech `w` oznacza wektor wag aktywów, `μ` wektor średnich dziennych stóp zwrotu, a `Σ` macierz kowariancji dziennych stóp zwrotu. Dla portfela długiego bez dźwigni wymagamy `wᵢ ≥ 0` oraz `Σᵢ wᵢ = 1`. Dzienny oczekiwany zwrot wynosi `μₚ = μᵀw`, a dzienna wariancja wynosi `σₚ² = wᵀΣw`. Wartości roczne będą wyliczane przez pomnożenie średniego zwrotu przez 252 oraz wariancji przez 252; roczna zmienność to `σₚ,roczna = √(252 · wᵀΣw)`. Są to założenia modelowe, które zostaną zweryfikowane przy implementacji.

Głównym celem jest maksymalizacja oczekiwanego zwrotu `μᵀw` przy ograniczeniu `σₚ,roczna ≤ σmax`, gdzie `σmax` jest limitem użytkownika. Funkcja oceny może stosować karę `F(w) = μᵀw − λ · max(0, σₚ,roczna − σmax)²`, gdzie `λ` jest współczynnikiem kary. Sama kara nie gwarantuje spełnienia ograniczenia, dlatego wybór wyniku końcowego będzie dodatkowo filtrował rozwiązania i dopuszczał wyłącznie portfele spełniające limit.

Chromosom jest wektorem rzeczywistych wag. Populacja początkowa będzie losowana i normalizowana do sumy 1. Planowane operatory to selekcja turniejowa, krzyżowanie ważone i mutacja niewielkich zmian wag z ponowną normalizacją. Do porównania użyjemy modelu Markowitza z tym samym celem i ograniczeniami oraz portfela 1/N.

### Wstępne parametry

Punkt startowy do strojenia: populacja 100 osobników, maksymalnie 200 pokoleń, turniej selekcyjny o rozmiarze 3, prawdopodobieństwo krzyżowania 0,8, prawdopodobieństwo mutacji 0,1 i ziarno losowości 42. To wartości planowane, a nie wyniki pomiaru; mogą ulec zmianie po eksperymentach. Implementacja ma działać na CPU.

## 5. Ewaluacja *(B · 8 pkt)*

Wyniki nie są jeszcze dostępne — algorytm nie został zaimplementowany, a dane nie zostały pobrane. Wstępne kryterium z karty to: wszystkie zwrócone portfele spełniają limit ryzyka, a mediana oczekiwanego zwrotu GA osiąga co najmniej 95% zwrotu Markowitza na pięciu przypadkach testowych. Porównamy też portfel 1/N. Metryki będą liczone na tym samym okresie testowym i przy identycznych ograniczeniach wag oraz ryzyka.

| Przypadek | Punkt odniesienia | Nasze rozwiązanie |
|---|---|---|
| 1–5 — do ustalenia po przygotowaniu danych | Markowitz i 1/N — brak wyników | Algorytm genetyczny — brak wyników |

Wniosek zostanie uzupełniony po eksperymentach; obecnie nie można stwierdzić, czy GA przewyższa prostą metodę bazową ani jak blisko jest rozwiązania Markowitza.

## 6. Wymagania niefunkcjonalne *(A · 5 pkt)*

Program ma działać na CPU i dla planowanego koszyka 50–100 spółek celować w czas poniżej 60 sekund na pojedynczy przypadek testowy; jest to cel do pomiaru, nie potwierdzona charakterystyka. Uruchomienie z tym samym ziarnem losowości, danymi i konfiguracją powinno odtworzyć ten sam wynik. System ma walidować m.in. pusty zbiór cen, brak wymaganych kolumn, duplikaty dat, wartości niefinitywne i niewystarczającą liczbę obserwacji. Brak tokenu API lub błąd pobrania danych ma zakończyć się czytelnym komunikatem.

## 7. Ograniczenia *(E · 4 pkt)*

Wynik zależy od historycznego okresu i nie stanowi prognozy ani rekomendacji inwestycyjnej. Model nie uwzględnia obecnie kosztów transakcyjnych, podatków, płynności, ograniczeń sektorowych ani zmian składu indeksów. Średnie zwroty historyczne są niepewne, a algorytm genetyczny może nie znaleźć optimum globalnego; jego wynik zależy od konfiguracji i ziarna. Przy zbyt niskim limicie ryzyka może nie istnieć dopuszczalny portfel. W przyszłości warto uwzględnić koszty transakcji, testy kroczące i dodatkowe ograniczenia inwestycyjne.

## 8. Zastosowania w praktyce *(E · 4 pkt)*

Optymalizacja portfela jest stosowana w narzędziach alokacji aktywów dla inwestorów indywidualnych, w procesach zarządzania portfelami funduszy oraz w analizie ryzyka i rebalansowaniu portfeli instytucjonalnych. W takich systemach algorytm pomaga porównywać możliwe wagi aktywów przy zadanych ograniczeniach; ostateczne decyzje wymagają dodatkowych danych i kontroli ryzyka. Ten projekt jest dydaktycznym prototypem i nie jest przeznaczony do podejmowania rzeczywistych decyzji inwestycyjnych.

## 9. Zespół *(D · 8 pkt)*

Zespół na tym etapie pracuje wspólnie nad założeniami projektu. Indywidualny podział ról zostanie ustalony później, wraz z planowaniem sprintów.

| Osoba | Za co odpowiadała |
|---|---|
| Kacper Nowaczyk (31838) | Wspólna praca nad założeniami; indywidualne zadania zostaną ustalone później |
| Adam Remfeld (31799) | Wspólna praca nad założeniami; indywidualne zadania zostaną ustalone później |
| Nikodem Boniecki (31865) | Wspólna praca nad założeniami; indywidualne zadania zostaną ustalone później |

## 10. Uruchomienie *(C · 4 pkt)*

Repozytorium nie zawiera jeszcze kodu ani `requirements.txt`, dlatego projektu nie da się obecnie uruchomić. Docelowa instrukcja po dodaniu szkieletu będzie zawierać wersję Pythona, konfigurację tokenu `TIINGO_API_TOKEN`, polecenie startowe i lokalizację wyników. Planowany punkt wejścia, zależności i katalog wynikowy nie są jeszcze ustalone.

```text
Instrukcja uruchomienia zostanie uzupełniona po dodaniu kodu i requirements.txt.
```

## 11. Narzędzia AI

ChatGPT pomógł uporządkować dokumentację według dostarczonych szablonów i przygotować wstępne sformułowania. Kod projektu, dane i wyniki eksperymentów nie zostały wygenerowane ani zweryfikowane przez narzędzia AI. Zespół powinien sprawdzić treść dokumentów, zasady wykorzystania Tiingo i wymagania prowadzącego przed zatwierdzeniem karty.
