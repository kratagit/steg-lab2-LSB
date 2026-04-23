import numpy as np
from PIL import Image
import math
import io
import os

class SteganographyLSB:
    """
    System steganograficzny wykorzystujący metodę Least Significant Bit (LSB).
    Gwarantuje zgodność ze standardami Clean Code oraz implementuje
    oznaczanie końca wiadomości za pomocą Null Terminatora ('\x00').
    """

    def __init__(self):
        self.terminator = '\x00'

    def calculate_psnr(self, original_img: np.ndarray, stego_img: np.ndarray) -> float:
        """
        Oblicza wartość Peak Signal-to-Noise Ratio (PSNR) między dwoma obrazami.
        """
        # Rzutowanie na int64 zapobiega przepełnieniu podczas obliczania różnic i potęgowania
        mse = np.mean((original_img.astype(np.int64) - stego_img.astype(np.int64)) ** 2)
        if mse == 0:
            return float('inf') # Obrazy są identyczne
        
        max_pixel_value = 255.0
        psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
        return psnr

    def text_to_binary(self, text: str) -> str:
        """
        Konwertuje tekst na strumień bitów w formacie stringa, dołączając terminator.
        """
        text_with_terminator = text + self.terminator
        return ''.join(format(ord(char), '08b') for char in text_with_terminator)

    def binary_to_text(self, binary_data: str) -> str:
        """
        Konwertuje strumień bitów z powrotem na tekst, przerywając po napotkaniu terminatora.
        """
        extracted_chars = []
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if len(byte) < 8: 
                break
            char_code = int(byte, 2)
            char = chr(char_code)
            if char == self.terminator:
                break
            extracted_chars.append(char)
        return ''.join(extracted_chars)

    def encode(self, input_image_path: str, secret_message: str, output_image_path: str) -> dict:
        """
        Ukrywa wiadomość tekstową w obrazie ze wsparciem operacyjnym na plikach.
        Zwraca słownik ze statystykami operacji (w tym PSNR).
        """
        # Wczytanie obrazu i wymuszenie trybu RGB
        image = Image.open(input_image_path).convert('RGB')
        img_array = np.array(image)
        original_shape = img_array.shape
        
        # Spłaszczenie tablicy z jednoczesnym rzutowaniem zapobiegającym błędom przepełnienia
        flat_img = img_array.flatten().astype(np.uint16)
        
        # Konwersja wiadomości
        binary_secret = self.text_to_binary(secret_message)
        data_length = len(binary_secret)
        
        # Weryfikacja pojemności nośnika
        max_capacity = len(flat_img)
        if data_length > max_capacity:
            raise ValueError(
                f"Pojemność obrazu jest niewystarczająca. "
                f"Wymagane bity: {data_length}, Dostępne: {max_capacity}."
            )
            
        # Zastępowanie najmniej znaczącego bitu
        for i in range(data_length):
            # val & 254 zeruje ostatni bit, a następnie bitowe OR (|) wstawia nowy bit.
            flat_img[i] = (flat_img[i] & 254) | int(binary_secret[i])
            
        # Przywrócenie pierwotnego kształtu i zapisanie, powrót do uint8
        stego_img_array = flat_img.reshape(original_shape).astype(np.uint8)
        stego_image = Image.fromarray(stego_img_array, 'RGB')
        stego_image.save(output_image_path)
        
        # Obliczenie statystyk w oparciu o czystą formę macierzową
        psnr_value = self.calculate_psnr(img_array, stego_img_array)
        
        return {
            "status": "Sukces",
            "ukryte_znaki": len(secret_message),
            "zmienione_bity": data_length,
            "psnr_db": psnr_value
        }

    def decode(self, stego_image_path: str) -> str:
        """
        Odczytuje ukrytą wiadomość tekstową z pliku wejściowego na podstawie terminatora.
        """
        image = Image.open(stego_image_path).convert('RGB')
        img_array = np.array(image)
        flat_img = img_array.flatten().astype(np.uint16)
        
        binary_data = []
        # Przeszukiwanie najmniej znaczących bitów piksel po pikselu
        for i in range(len(flat_img)):
            # Wyciągnięcie najmniej znaczącego bitu (val & 1)
            binary_data.append(str(flat_img[i] & 1))
            
            # Gdy zebrano pełen bajt, można sprawdzić czy to nie terminator
            if len(binary_data) % 8 == 0:
                current_byte = "".join(binary_data[-8:])
                if chr(int(current_byte, 2)) == self.terminator:
                    # Napotkano koniec wiadomości
                    return self.binary_to_text("".join(binary_data))
                    
        return "BŁĄD ODCZYTU: Nie znaleziono znacznika końca wiadomości."


# Blok wykonawczy z proceduralnymi definicjami testów laboratoryjnych
if __name__ == "__main__":
    s = SteganographyLSB()

    # GENEROWANIE DANYCH TESTOWYCH (Tworzenie losowych szumów graficznych w celu braku błędu "file not found")
    # Zastępuje naturalne obrazy precyzyjnie wymierzonymi matrycami.
    img1_mock = Image.fromarray(np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8), 'RGB')
    img1_mock.save("test1_cover.png")
    
    img2_mock = Image.fromarray(np.random.randint(0, 256, (1024, 1024, 3), dtype=np.uint8), 'RGB')
    img2_mock.save("test2_cover.png")
    
    img3_mock = Image.fromarray(np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8), 'RGB')
    img3_mock.save("test3_cover.png")

    print("==================================================")
    print("[>] Uruchamianie Testu 1: Krótka wiadomość...")
    stats1 = s.encode("test1_cover.png", "Hello, World!", "test1_stego.png")
    print(f"[-] Obraz wejściowy: test1_cover.png (512x512)")
    print(f"[-] Wiadomość: 'Hello, World!'")
    print(f"[+] Zapisano do: test1_stego.png")
    print(f"[+] Zmierzony współczynnik PSNR: {stats1['psnr_db']:.2f} dB")
    dec1 = s.decode("test1_stego.png")
    print(f"[+] Weryfikacja odczytu: {dec1}")

    print("==================================================")
    print("[>] Uruchamianie Testu 2: Długa wiadomość (1000 znaków)...")
    msg2 = "A" * 1000
    stats2 = s.encode("test2_cover.png", msg2, "test2_stego.png")
    print(f"[-] Obraz wejściowy: test2_cover.png (1024x1024)")
    print(f"[-] Wiadomość wygenerowana dynamicznie (ciąg 1000x'A')")
    print(f"[+] Zapisano do: test2_stego.png")
    print(f"[+] Zmierzony współczynnik PSNR: {stats2['psnr_db']:.2f} dB")

    print("==================================================")
    print("[>] Uruchamianie Testu 3: Odczyt ustalonej wiadomości...")
    s.encode("test3_cover.png", "Steganography is fun!", "test3_stego.png")
    print("[-] Przygotowano zagnieżdżony obraz test3_stego.png z przekazem.")
    dec3 = s.decode("test3_stego.png")
    print(f"[+] Ekstrakcja danych (output): {dec3}")

    print("==================================================")
    print("[>] Uruchamianie Testu 4: Odporność na kompresję JPEG (Jakość 90%)...")
    img_for_jpeg = Image.open("test3_stego.png")
    img_for_jpeg.save("test4_compressed.jpg", format='JPEG', quality=90)
    print("[-] Utworzono plik test4_compressed.jpg")
    dec4 = s.decode("test4_compressed.jpg")
    # Wyświetlamy tylko obciętą cześć wyjścia z racji na wizualne śmieci
    print(f"[!] Próba odczytu zwróciła uszkodzone dane: {dec4[:50]}...")
    print("==================================================")