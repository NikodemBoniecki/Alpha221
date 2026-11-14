# Karta zgłoszenia tematu projektu

**Grupa:** L2 / L3 | **Zespół:** Z4 | **Data ostatniej zmiany:** 2026-11-14
Sztuczna inteligencja, laboratorium | Collegium Da Vinci | rok akademicki 2026/2027

Plik `karta-tematu.md` w głównym katalogu repozytorium zespołu. Karta w repozytorium jest wersją obowiązującą.

## 1. Skład zespołu (obowiązkowe)

| Imię i nazwisko | Nr albumu | Rola (wstępna) |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Projekt algorytmu genetycznego i operatory GA |
| Adam Remfeld | 31799 | Wybór licencjonowanego źródła, pozyskanie i przygotowanie danych |
| Nikodem Boniecki | 31865 | Punkty odniesienia, ewaluacja, integracja i dokumentacja |

## 2. Tytuł

- **Po polsku:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **Po angielsku:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem (obowiązkowe)

Chcemy pomóc inwestorom indywidualnym zdecydować, jak podzielić kapitał między wybrane akcje, uwzględniając oczekiwany zwrot i ryzyko. Program przyjmie historyczne ceny dzienne spółek oraz limit ryzyka podany przez użytkownika. Na tej podstawie zaproponuje udziały spółek w portfelu i oszacuje jego zwrot oraz ryzyko. Na początek skupimy się na firmach z obszarów AI, gamedev i półprzewodników.

## 4. Dlaczego zwykły algorytm nie wystarczy

- [ ] nie umiemy zapisać reguły krok po kroku
- [ ] przepis istnieje, ale jest obliczeniowo za drogi
- [ ] reguł jest za dużo i zmieniają się w czasie

Uzasadnienie: Podstawowy problem portfelowy da się rozwiązać klasyczną optymalizacją średnia-wariancja, więc nie twierdzimy, że dla naszej skali zwykły algorytm jest za wolny. Wybraliśmy algorytm genetyczny, aby sprawdzić metodę z zajęć i porównać ją z rozwiązaniem Markowitza oraz portfelem równoważonym.

## 5. Technologia SI (obowiązkowe)

- [ ] sieć neuronowa
- [ ] system ekspertowy / wnioskowanie regułowe
- [x] algorytm genetyczny
- [ ] klasyczne uczenie maszynowe

Dlaczego ta technologia pasuje do tego problemu: Algorytm genetyczny pozwoli nam przeszukać wiele możliwych zestawów wag portfela i uwzględnić limit ryzyka przy ocenie każdego z nich. Zobaczymy, jak jego wyniki wypadają w porównaniu z analitycznym rozwiązaniem Markowitza.

## 6. Dane (obowiązkowe)

| | |
|---|---|
| Źródło (link do konkretnego zbioru, nie do serwisu) | Nie wybraliśmy jeszcze konkretnego zbioru. Rozważamy [Tiingo EOD Daily Prices](https://www.tiingo.com/documentation/end-of-day), endpoint `/tiingo/daily/{ticker}/prices`. Musimy ustalić tickery i daty. Opisaliśmy wymagania w [`docs/tiingo-data-notes.md`](docs/tiingo-data-notes.md). |
| Rozmiar i format | Celujemy w 50 do 100 tickerów i do 5 lat cen dziennych. API zwraca dane w JSON, może też zwracać CSV. Dokładny zakres ustalimy po wyborze źródła i tickerów. |
| Czy dane są już dostępne? | Nie. Nie wybraliśmy zbioru ani nie pobraliśmy danych. |
| Plan pozyskania danych | Ustalimy tickery i daty, a potem sprawdzimy dostępność każdego symbolu. Przed pobraniem danych uzyskamy licencję Enterprise Tiingo na ewaluację AI albo wybierzemy inny konkretny zbiór, którego licencja pozwala przechowywać dane i porównywać algorytmy. Starter ani Power nie dają prawa do takiego benchmarku Tiingo. |

## 7. Stos technologiczny

Napiszemy program w Pythonie 3, tak aby działał na CPU. Do pobierania danych możemy użyć `requests`, a do obliczeń `numpy` i `pandas`. Wersję Pythona i zależności ustalimy przy tworzeniu szkieletu. Tiingo wymaga tokenu, ale nie pobierzemy danych bez licencji Enterprise na ich przechowywanie i porównawczą ewaluację AI. Więcej informacji znajduje się w [`docs/tiingo-data-notes.md`](docs/tiingo-data-notes.md).

## 8. Kryterium sukcesu (obowiązkowe)

- **Metryka:** odsetek zwróconych portfeli spełniających limit rocznej zmienności oraz relacja rocznego oczekiwanego zwrotu GA do wyniku modelu Markowitza przy tym samym limicie.
- **Próg (liczba):** każdy zwrócony portfel musi spełniać limit ryzyka. W pięciu przypadkach testowych mediana zwrotu ma wynieść co najmniej 95% wyniku Markowitza. To nasz cel na ewaluację.
- **Punkt odniesienia** (prosta metoda, z którą porównacie wynik): klasyczny model Markowitza (punkt odniesienia jakości) i portfel równoważony 1/N (prosta metoda bazowa).

## 9. Zakres minimalny (obowiązkowe)

Nasz program wczyta historyczne ceny dla kilku tickerów, obliczy dzienne stopy zwrotu i macierz kowariancji, a następnie uruchomi nasz algorytm genetyczny. Dopuścimy tylko długie pozycje, a wagi portfela będą sumować się do 1. Program pokaże wagi, szacowany zwrot i ryzyko, nie zwróci portfela przekraczającego limit i porówna wynik z Markowitzem oraz 1/N na tych samych danych.

## 10. Zakres opcjonalny

Jeśli wystarczy czasu, dodamy pobieranie danych z API, porównamy kilka ustawień parametrów i ziaren losowości, narysujemy granicę efektywną albo przygotujemy prosty ekran do wyboru tickerów i limitu ryzyka.

## 11. Repozytorium

Link: https://github.com/NikodemBoniecki/Alpha221

Raporty sprintów prowadzimy w pliku `sprints.txt` w głównym katalogu repozytorium.

## 12. Główne ryzyko i plan awaryjny (obowiązkowe)

Największym ryzykiem jest brak licencji na przechowywanie danych i ewaluację algorytmu. Przed pobraniem danych wybierzemy źródło, którego warunki pozwalają na taki użytek. Jeśli limit ryzyka okaże się zbyt niski, program zgłosi brak dopuszczalnego portfela zamiast zwracać wynik, który łamie ograniczenie. Dane syntetyczne wykorzystamy tylko do sprawdzenia kodu, nie do końcowej ewaluacji.

---

## Decyzja prowadzącego

> Wypełnia prowadzący. Tej sekcji nie edytujemy.

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**

---
*Bartosz Lewandowski · bartosz.lewandowski@cdv.pl · Sztuczna inteligencja, laboratorium · Collegium Da Vinci · rok akademicki 2026/2027*
