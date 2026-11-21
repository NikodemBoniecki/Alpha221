# Karta zgłoszenia tematu projektu

**Grupa:** L2 / L3 | **Zespół:** Z4 | **Aktualizacja:** 2026-11-21
Sztuczna inteligencja, laboratorium | Collegium Da Vinci | rok akademicki 2026/2027

## 1. Skład zespołu

| Imię i nazwisko | Nr albumu | Zakres |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Algorytm genetyczny i jego operatory |
| Adam Remfeld | 31799 | Pozyskanie i przygotowanie danych |
| Nikodem Boniecki | 31865 | Punkty odniesienia, ewaluacja, integracja i dokumentacja |

## 2. Tytuł

- **Po polsku:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **Po angielsku:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem

Projekt bada, jak podział portfela wpływa na szacowany zwrot i ryzyko. Użytkownik podaje limit rocznej zmienności. Program ma dobrać wagi aktywów i porównać algorytm genetyczny z modelem Markowitza oraz portfelem równoważonym.

## 4. Dlaczego używamy algorytmu genetycznego?

Klasyczną optymalizację średnia-wariancja można rozwiązać bez algorytmu genetycznego. GA wybraliśmy jako metodę omawianą na zajęciach i punkt porównania dla mieszanego problemu doboru aktywów i wag.

## 5. Technologia SI

- [ ] Sieć neuronowa
- [ ] System ekspertowy lub wnioskowanie regułowe
- [x] Algorytm genetyczny
- [ ] Klasyczne uczenie maszynowe

## 6. Dane

Źródłem dziennych notowań jest Yahoo Finance, pobierane przez nieoficjalną bibliotekę yfinance. Wykorzystujemy je wyłącznie w zamkniętym projekcie edukacyjnym. Dane w CSV są lokalne i ignorowane przez Git.

| Grupa | Ticker | Waluta notowania |
|---|---|---|
| Spółki | AAPL, MSFT, NVDA, JPM, KO, TTWO, AMD, ASML, TSLA | USD |
| Spółka | UBI.PA | EUR |
| Spółki | CDR.WA, XTB.WA, PKN.WA, ASB.WA, CBF.WA | PLN |
| ETF S&P 500 | SPY | USD |
| ETF WIG20TR | ETFBW20TR.WA | PLN |

Pobieracz domyślnie pobiera ostatnie dwa lata danych dla 15 spółek, dwóch ETF-ów oraz kursów USDPLN=X i EURUSD=X. Obsługuje też odtwarzalne okno `--start/--end`. Historyczne ceny skorygowane o działania korporacyjne przelicza na USD. PLN dzieli przez USD/PLN, a EUR mnoży przez EUR/USD. Ceny instrumentów nie są uzupełniane.

Siedmioletni zbiór z okresu 21.11.2019-20.11.2026 zawiera 1703 wspólne sesje dzienne oraz 366 cen tygodniowych, czyli 365 okresów zwrotu. Audyt nie wykazał błędnych tickerów, walut, typów instrumentów, luk ani niepoprawnych cen. Każdy potrzebny kurs FX pochodził z tego samego dnia.

## 7. Stos technologiczny

Python 3.10+, NumPy, SciPy, pandas i yfinance. Dane pobiera polecenie python -m alpha221.market_data; nie jest wymagany token API. Aplikacja jest konsolowym prototypem.

## 8. Kryteria porównania

GA maksymalizuje szacowane prawdopodobieństwo dodatniego skumulowanego zwrotu USD w 6 miesięcy przy limicie rocznej zmienności. Wagi są wyznaczane z kroczącego 2-letniego okna tygodniowych danych i oceniane w 5-letnim teście poza próbą, z aktualizacją co 26 tygodni. Wyniki GA, Markowitza i 1/N są porównywane na tych samych 10 okresach.

GA wybiera dokładnie 10 z 15 spółek. Każda wybrana spółka ma wagę 1-20%. Spółki zajmują łącznie 80% portfela, a ETF-y 20%, przy minimum 1% na każdy ETF. Markowitz ma te same limity, ale może użyć dowolnej liczby spółek. 1/N dzieli obie części po równo.

Końcowy przebieg przy limicie 22% dał łączne zwroty historyczne: GA 199,71%, Markowitz 319,40% i 1/N 177,29%. Każda metoda miała 9 dodatnich okresów półrocznych z 10. Są to wyniki historyczne bez prowizji, podatków i kosztów rebalansowania, a nie prognoza ani dowód przewagi metody.

## 9. Zakres i stan implementacji

Program pobiera i sprawdza dane, przelicza ceny na USD, eksportuje pliki dzienne i tygodniowe oraz zapisuje manifest z sumami SHA-256. Działają też GA, Markowitz, 1/N, ograniczenia wag, bootstrap, pięcioletni test kroczący i sprawdzenie wszystkich 3003 składów po 10 spółek.

Wagi w każdym z 3003 składów wyznacza Markowitz, więc nie jest to pełne przeszukanie wszystkich możliwych wag. Zostało przeliczenie kwoty inwestycji w USD na jednostki aktywów, które można faktycznie kupić.

## 10. Ograniczenia

Wyniki będą zależeć od wybranego okna historycznego i nie przewidują przyszłości. Nie uwzględniamy kosztów transakcji, podatków ani płynności. Dane Yahoo Finance nie są gwarantowane jako bezbłędne ani stale dostępne. Nie publikujemy pobranych szeregów cenowych. Projekt nie jest poradą inwestycyjną.

## 11. Repozytorium

https://github.com/NikodemBoniecki/Alpha221

## Decyzja prowadzącego

> Tę sekcję wypełnia prowadzący.

- [ ] Zatwierdzony
- [ ] Do poprawy

**Uwagi:**
