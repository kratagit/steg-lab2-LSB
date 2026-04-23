import numpy as np
from PIL import Image
import math
import io
import os

class SteganographyLSB:
    """
    Steganographic system using the Least Significant Bit (LSB) method.
    Guarantees compliance with Clean Code standards and implements
    marking the end of the message using a Null Terminator ('\x00').
    """

    def __init__(self):
        self.terminator = '\x00'

    def calculate_psnr(self, original_img: np.ndarray, stego_img: np.ndarray) -> float:
        """
        Calculates the Peak Signal-to-Noise Ratio (PSNR) value between two images.
        """
        # Casting to int64 prevents overflow during difference calculation and exponentiation
        mse = np.mean((original_img.astype(np.int64) - stego_img.astype(np.int64)) ** 2)
        if mse == 0:
            return float('inf') # Images are identical
        
        max_pixel_value = 255.0
        psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
        return psnr

    def text_to_binary(self, text: str) -> str:
        """
        Converts text to a bit stream in string format, appending a terminator.
        """
        text_with_terminator = text + self.terminator
        return ''.join(format(ord(char), '08b') for char in text_with_terminator)

    def binary_to_text(self, binary_data: str) -> str:
        """
        Converts a bit stream back to text, stopping when a terminator is encountered.
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
        Hides a text message in an image with file operation support.
        Returns a dictionary with operation statistics (including PSNR).
        """
        # Load image and force RGB mode
        image = Image.open(input_image_path).convert('RGB')
        img_array = np.array(image)
        original_shape = img_array.shape
        
        # Flatten array while casting to prevent overflow errors
        flat_img = img_array.flatten().astype(np.uint16)
        
        # Message conversion
        binary_secret = self.text_to_binary(secret_message)
        data_length = len(binary_secret)
        
        # Carrier capacity verification
        max_capacity = len(flat_img)
        if data_length > max_capacity:
            raise ValueError(
                f"Image capacity is insufficient. "
                f"Required bits: {data_length}, Available: {max_capacity}."
            )
            
        # Replacing the least significant bit
        for i in range(data_length):
            # val & 254 clears the last bit, then bitwise OR (|) inserts the new bit.
            flat_img[i] = (flat_img[i] & 254) | int(binary_secret[i])
            
        # Restore original shape and save, return to uint8
        stego_img_array = flat_img.reshape(original_shape).astype(np.uint8)
        stego_image = Image.fromarray(stego_img_array, 'RGB')
        stego_image.save(output_image_path)
        
        # Calculate statistics based on pure matrix form
        psnr_value = self.calculate_psnr(img_array, stego_img_array)
        
        return {
            "status": "Success",
            "hidden_chars": len(secret_message),
            "changed_bits": data_length,
            "psnr_db": psnr_value
        }

    def decode(self, stego_image_path: str) -> str:
        """
        Reads a hidden text message from an input file based on the terminator.
        """
        image = Image.open(stego_image_path).convert('RGB')
        img_array = np.array(image)
        flat_img = img_array.flatten().astype(np.uint16)
        
        binary_data = []
        # Search the least significant bits pixel by pixel
        for i in range(len(flat_img)):
            # Extract the least significant bit (val & 1)
            binary_data.append(str(flat_img[i] & 1))
            
            # When a full byte is collected, check if it's the terminator
            if len(binary_data) % 8 == 0:
                current_byte = "".join(binary_data[-8:])
                if chr(int(current_byte, 2)) == self.terminator:
                    # End of message encountered
                    return self.binary_to_text("".join(binary_data))
                    
        return "READ ERROR: End of message marker not found."


# Execution block with procedural definitions of laboratory tests
if __name__ == "__main__":
    s = SteganographyLSB()

    # GENERATING TEST DATA (Creating random graphic noise to avoid "file not found" error)
    # Replaces natural images with precisely measured matrices.
    img1_mock = Image.fromarray(np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8), 'RGB')
    img1_mock.save("test1_cover.png")
    
    img2_mock = Image.fromarray(np.random.randint(0, 256, (1024, 1024, 3), dtype=np.uint8), 'RGB')
    img2_mock.save("test2_cover.png")
    
    img3_mock = Image.fromarray(np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8), 'RGB')
    img3_mock.save("test3_cover.png")

    print("==================================================")
    print("[>] Running Test 1: Short message...")
    stats1 = s.encode("test1_cover.png", "Hello, World!", "test1_stego.png")
    print(f"[-] Input image: test1_cover.png (512x512)")
    print(f"[-] Message: 'Hello, World!'")
    print(f"[+] Saved to: test1_stego.png")
    print(f"[+] Measured PSNR ratio: {stats1['psnr_db']:.2f} dB")
    dec1 = s.decode("test1_stego.png")
    print(f"[+] Data extraction (output): {dec1}")

    print("==================================================")
    print("[>] Running Test 2: Long message (1000 characters)...")
    msg2 = "A" * 1000
    stats2 = s.encode("test2_cover.png", msg2, "test2_stego.png")
    print(f"[-] Input image: test2_cover.png (1024x1024)")
    print(f"[-] Dynamically generated message (string of 1000x'A')")
    print(f"[+] Saved to: test2_stego.png")
    print(f"[+] Measured PSNR ratio: {stats2['psnr_db']:.2f} dB")

    print("==================================================")
    print("[>] Running Test 3: Reading a fixed message...")
    s.encode("test3_cover.png", "Steganography is fun!", "test3_stego.png")
    print("[-] Prepared nested image test3_stego.png with message.")
    dec3 = s.decode("test3_stego.png")
    print(f"[+] Data extraction (output): {dec3}")

    print("==================================================")
    print("[>] Running Test 4: Resistance to JPEG compression (90% Quality)...")
    img_for_jpeg = Image.open("test3_stego.png")
    img_for_jpeg.save("test4_compressed.jpg", format='JPEG', quality=90)
    print("[-] Created file test4_compressed.jpg")
    dec4 = s.decode("test4_compressed.jpg")
    # Display only a truncated part of the output due to visual garbage
    print(f"[!] Read attempt returned corrupted data: {dec4[:50]}...")
    print("==================================================")