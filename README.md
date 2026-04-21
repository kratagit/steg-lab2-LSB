# steg-lab2-LSB

# Laboratorium 2: Steganografia LSB

## Cel zadania
Celem zadania jest implementacja prostego systemu steganografii w obrazach cyfrowych z wykorzystaniem metody **LSB (Least Significant Bit)** w środowisku Matlab lub Python.

## Opis zadania
Zaimplementuj system steganograficzny, który pozwoli na ukrycie wiadomości tekstowej w obrazie cyfrowym. System powinien składać się z dwóch głównych funkcji:
1.  **Funkcja ukrywająca** wiadomość w obrazie.
2.  **Funkcja wyodrębniająca** ukrytą wiadomość z obrazu.

## Wymagania funkcjonalne

### Funkcja ukrywająca wiadomość powinna:
* Przyjmować obraz wejściowy w formacie **RGB**.
* Przyjmować wiadomość tekstową do ukrycia.
* Wykorzystywać metodę **LSB** do ukrycia wiadomości w najmniej znaczących bitach pikseli obrazu.
* Sprawdzać, czy pojemność obrazu jest wystarczająca do ukrycia całej wiadomości.
* Zapisywać wraz z wiadomością informację o jej długości albo stosować jednoznaczny znacznik końca wiadomości (null terminator).
* Zwracać obraz z ukrytą wiadomością.

### Funkcja wyodrębniająca wiadomość powinna:
* Przyjmować obraz z ukrytą wiadomością.
* Odczytywać ukrytą wiadomość z najmniej znaczących bitów pikseli.
* Odtwarzać wiadomość na podstawie zapisanej długości albo znacznika końca.
* Zwracać odczytaną wiadomość tekstową.

## Kryteria akceptacji
* System poprawnie ukrywa i odczytuje wiadomości o długości do **1000 znaków**, o ile pojemność obrazu na to pozwala.
* Obraz z ukrytą wiadomością jest wizualnie nieodróżnialny od oryginału.
* Wartość **PSNR** po osadzeniu wiadomości jest większa niż odpowiednio **45 dB** i **50 dB** (w zależności od długości wiadomości).
* System działa poprawnie dla bezstratnych formatów obrazów, w szczególności **PNG** i **BMP**.
* Kod jest czytelny, dobrze udokumentowany i zgodny z zasadami czystego kodu.

## Przypadki testowe

1.  **Test ukrywania krótkiej wiadomości:**
    * **Wejście:** obraz 512x512 PNG, wiadomość „Hello, World!”
    * **Oczekiwany wynik:** obraz z ukrytą wiadomością, poprawny odczyt wiadomości, PSNR > 50 dB.
2.  **Test ukrywania długiej wiadomości:**
    * **Wejście:** obraz 1024x1024 BMP, wiadomość o długości 1000 znaków.
    * **Oczekiwany wynik:** obraz z ukrytą wiadomością, poprawny odczyt wiadomości, PSNR > 45 dB.
3.  **Test odczytu ukrytej wiadomości:**
    * **Wejście:** obraz z ukrytą wiadomością „Steganography is fun!”
    * **Oczekiwany wynik:** odczytana wiadomość „Steganography is fun!”.
4.  **Test odporności na kompresję:**
    * **Wejście:** obraz z ukrytą wiadomością zapisany do formatu JPG (jakość 90%).
    * **Oczekiwany wynik:** brak gwarancji poprawnego odczytu; dopuszczalny błędny odczyt lub komunikat o uszkodzeniu danych.

## Dodatkowe wytyczne
* Do kodu źródłowego dołącz **sprawozdanie** opisujące wykonane zadanie oraz wyniki weryfikacji przypadków testowych.
* Dodaj funkcję obliczającą **PSNR** (Peak Signal-to-Noise Ratio) między oryginalnym obrazem a obrazem z wiadomością.
* W opisie implementacji wskaż, czy wiadomość jest zakończona znacznikiem końca, czy poprzedzona informacją o długości.
