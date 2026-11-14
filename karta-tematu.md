# Karta zgłoszenia tematu projektu

**Grupa:** L2 / L3 · **Zespół:** Z4 · **Data ostatniej zmiany:** 2026-11-14  
Sztuczna inteligencja — laboratorium · Collegium Da Vinci · rok akad. 2026/2027

Plik `karta-tematu.md` w głównym katalogu repozytorium zespołu. Karta w repozytorium jest wersją obowiązującą.

## 1. Skład zespołu (obowiązkowe)

| Imię i nazwisko | Nr albumu | Rola (wstępna) |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Wspólna praca zespołu; role indywidualne do podziału później |
| Adam Remfeld | 31799 | Wspólna praca zespołu; role indywidualne do podziału później |
| Nikodem Boniecki | 31865 | Wspólna praca zespołu; role indywidualne do podziału później |

## 2. Tytuł

- **Po polsku:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **Po angielsku:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem (obowiązkowe)

Inwestor indywidualny musi zdecydować, jak podzielić kapitał pomiędzy wybrane akcje, równoważąc oczekiwany zwrot i ryzyko. System przyjmie historyczne ceny dzienne wybranych spółek oraz maksymalny poziom ryzyka wskazany przez użytkownika. Obliczy proponowane udziały spółek w portfelu i oszacuje jego oczekiwany zwrot oraz ryzyko. Projekt koncentruje się na spółkach z obszarów AI, gamedev i półprzewodników.

## 4. Dlaczego zwykły algorytm nie wystarczy

- [ ] nie umiemy zapisać reguły krok po kroku
- [ ] przepis istnieje, ale jest obliczeniowo za drogi
- [ ] reguł jest za dużo i zmieniają się w czasie

Uzasadnienie: Podstawowy problem portfelowy można rozwiązać klasyczną optymalizacją średnia-wariancja, dlatego nie zakładamy, że zwykły algorytm jest niewystarczający dla planowanej liczby spółek. Algorytm genetyczny wybieramy jako metodę SI badaną w ramach laboratorium i porównamy go z klasycznym rozwiązaniem oraz prostym portfelem równoważonym.

## 5. Technologia SI (obowiązkowe)

- [ ] sieć neuronowa
- [ ] system ekspertowy / wnioskowanie regułowe
- [x] algorytm genetyczny
- [ ] klasyczne uczenie maszynowe

Dlaczego ta technologia pasuje do tego problemu: Algorytm genetyczny może przeszukiwać wiele możliwych zestawów wag portfela i uwzględniać limit ryzyka w ocenie kandydatów. Pozwoli nam porównać jakość heurystycznego przeszukiwania z rozwiązaniem analitycznym Markowitza.

## 6. Dane (obowiązkowe)

| | |
|---|---|
| Źródło (link do konkretnego zbioru, nie do serwisu) | [Tiingo EOD Daily Prices API](https://www.tiingo.com/documentation/end-of-day), endpoint `/tiingo/daily/{ticker}/prices`; lista tickerów i dat do ustalenia |
| Rozmiar i format | Plan: ok. 50–100 tickerów, do 5 lat danych dziennych; odpowiedzi API w JSON. Faktyczny rozmiar zależy od wybranych spółek i okresu. |
| Czy dane są już dostępne? | Nie — nie pobraliśmy jeszcze danych ani nie skonfigurowaliśmy tokenu API. |
| Jeśli nie — plan pozyskania | Założyć konto Tiingo, uzyskać token i pobierać ceny historyczne dla ustalonej listy tickerów. Token będzie przechowywany lokalnie w zmiennej środowiskowej, a pobrane dane nie będą commitowane do repozytorium. |

## 7. Stos technologiczny

Planowany jest Python 3, uruchamiany na CPU. Biblioteki: `requests` do komunikacji z API oraz `numpy` i `pandas` do obróbki szeregów cen i obliczeń. Dokładna wersja Pythona i zależności zostaną przypięte przy tworzeniu szkieletu projektu. Dostęp do Tiingo wymaga tokenu; warunki planu Starter określają dane jako przeznaczone do użytku wewnętrznego, dlatego nie będziemy umieszczać surowych danych w repozytorium ani rozpowszechniać ich bez sprawdzenia uprawnień.

## 8. Kryterium sukcesu (obowiązkowe)

- **Metryka:** odsetek zwróconych portfeli spełniających limit rocznej zmienności oraz relacja rocznego oczekiwanego zwrotu GA do wyniku modelu Markowitza przy tym samym limicie.
- **Próg (liczba):** 100% zwracanych portfeli spełnia limit ryzyka, a mediana relacji zwrotu do Markowitza wynosi co najmniej 95% w 5 ustalonych przypadkach testowych. To wstępny cel do potwierdzenia przed ewaluacją.
- **Punkt odniesienia** (prosta metoda, z którą porównacie wynik): klasyczny model Markowitza (punkt odniesienia jakości) i portfel równoważony 1/N (prosta metoda bazowa).

## 9. Zakres minimalny (obowiązkowe)

Program wczyta historyczne ceny dla co najmniej kilku tickerów, obliczy dzienne stopy zwrotu i macierz kowariancji, uruchomi własną implementację algorytmu genetycznego dla długich pozycji o wagach sumujących się do 1 oraz nie zwróci portfela przekraczającego zadany limit ryzyka. Pokaże wagi, szacowany zwrot i ryzyko oraz porówna wynik z portfelem Markowitza i 1/N na tych samych danych.

## 10. Zakres opcjonalny

Pobieranie danych bezpośrednio z API, porównanie kilku ustawień parametrów i ziaren losowości, wykres granicy efektywnej oraz prosty interfejs do wyboru tickerów i limitu ryzyka.

## 11. Repozytorium

Link: https://github.com/NikodemBoniecki/Alpha221

Raporty sprintów: plik `sprints.txt` w głównym katalogu repozytorium.

## 12. Główne ryzyko i plan awaryjny (obowiązkowe)

Główne ryzyka to brak dostępu do API lub ograniczenia licencyjne oraz brak znalezienia portfela spełniającego zbyt niski limit ryzyka. Najpierw sprawdzimy dostęp do API i warunki wykorzystania danych; jeśli pobranie danych nie będzie możliwe, użyjemy jawnie oznaczonych, syntetycznych danych testowych z ustalonym ziarnem losowości. Gdy limit będzie nieosiągalny dla danego zbioru aktywów, program zgłosi brak rozwiązania zamiast zwracać portfel naruszający ograniczenie.

---

## Decyzja prowadzącego

> Wypełnia prowadzący — nie edytujcie tej sekcji.

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**

---
*Bartosz Lewandowski · bartosz.lewandowski@cdv.pl · Sztuczna inteligencja — laboratorium · Collegium Da Vinci · rok akad. 2026/2027*
