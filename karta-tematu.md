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
| Źródło (link do konkretnego zbioru, nie do serwisu) | [Huge Stock Market Dataset, wersja 3](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs). Wybierzemy pliki dla NVDA, AMD, MSFT, EA i TTWO. Zbiór ma licencję CC0. |
| Rozmiar i format | Pięć plików CSV z dziennymi cenami OHLCV. Planowany okres to 2012-01-03 do 2017-01-03, około 1 260 sesji na spółkę, łącznie około 6 300 obserwacji przed sprawdzeniem braków. |
| Czy dane są już dostępne? | Nie. Wybraliśmy zbiór, ale nie pobraliśmy jeszcze plików. |
| Plan pozyskania danych | Pobierzemy wybrane pliki z Kaggle, sprawdzimy dostępność tickerów i zakres dat, a potem przygotujemy wspólny plik CSV z datą i skorygowaną ceną zamknięcia. Kaggle opisuje ceny jako skorygowane o splity i dywidendy. |

## 7. Stos technologiczny

Program działa na Pythonie 3.10 lub nowszym i CPU. Do obliczeń używa `numpy` i `scipy`; zależności znajdują się w `requirements.txt`. Zbiór pobierzemy ręcznie z Kaggle, a do programu wczytamy przygotowany plik CSV. Nie korzystamy z API ani tokenu.

## 8. Kryterium sukcesu (obowiązkowe)

- **Metryka:** odsetek portfeli GA spełniających limit rocznej zmienności oraz roczna relacja zwrotu GA do zwrotu Markowitza przy tym samym limicie.
- **Próg (liczba):** każdy portfel zwrócony przez algorytm genetyczny musi spełniać limit ryzyka. Mediana pięciu rocznych relacji zwrotu GA do Markowitza, dla lat 2012-2016, ma wynieść co najmniej 0,95 (95%). To nasz cel na ewaluację.
- **Punkt odniesienia** (prosta metoda, z którą porównacie wynik): klasyczny model Markowitza (punkt odniesienia jakości) i portfel równoważony 1/N (prosta metoda bazowa).

## 9. Zakres minimalny (obowiązkowe)

Nasz program wczyta historyczne ceny dla kilku tickerów, obliczy dzienne stopy zwrotu i macierz kowariancji, a następnie uruchomi algorytm genetyczny. Dopuścimy tylko długie pozycje, a wagi portfela będą sumować się do 1. Program pokaże wagi, szacowany zwrot i ryzyko. Algorytm genetyczny nie zwróci rozwiązania przekraczającego limit, a wyniki porównamy z Markowitzem i 1/N na tych samych danych. Jeśli portfel 1/N przekroczy limit, oznaczymy go jako niespełniający ograniczenia.

## 10. Zakres opcjonalny

Jeśli wystarczy czasu, porównamy kilka ustawień parametrów i ziaren losowości, narysujemy granicę efektywną albo przygotujemy prosty ekran do wyboru tickerów i limitu ryzyka.

## 11. Repozytorium

Link: https://github.com/NikodemBoniecki/Alpha221

Raporty sprintów prowadzimy w pliku `sprints.txt` w głównym katalogu repozytorium.

## 12. Główne ryzyko i plan awaryjny (obowiązkowe)

Największym ryzykiem jest to, że wybrane tickery nie będą miały wspólnego zakresu dat albo stary zbiór nie będzie dobrze opisywał obecnego rynku. Przed ewaluacją sprawdzimy pliki i wspólny okres. Jeśli danych będzie za mało, użyjemy innego zbioru CC0 albo zmniejszymy liczbę tickerów. Przy zbyt niskim limicie ryzyka program zgłosi brak dopuszczalnego portfela. Dane syntetyczne wykorzystamy tylko do sprawdzenia kodu, nie do końcowej ewaluacji.

---

## Decyzja prowadzącego

> Wypełnia prowadzący. Tej sekcji nie edytujemy.

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**

---
*Bartosz Lewandowski · bartosz.lewandowski@cdv.pl · Sztuczna inteligencja, laboratorium · Collegium Da Vinci · rok akademicki 2026/2027*
