#!/usr/bin/env python3

class HillCipher:
    def __init__(self, key_matrix):
        """
        Initialize Hill cipher with a key matrix
        
        Args:
            key_matrix: list of lists for 2x2 or 3x3 matrix
        """
        self.key = key_matrix
        self.size = len(key_matrix)
        
        # Verify matrix is square (2x2 or 3x3)
        if self.size not in [2, 3]:
            raise ValueError("Matrix must be 2x2 or 3x3")
        
        for row in key_matrix:
            if len(row) != self.size:
                raise ValueError("Matrix must be square")
        
        # Verify matrix is invertible modulo 26
        if not self.is_invertible():
            raise ValueError("Matrix is not invertible modulo 26")
    
    def mod_inverse(self, a, m=26):
        """
        Calculate modular inverse using extended Euclidean algorithm
        """
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"No modular inverse for {a} modulo {m}")
    
    def determinant_mod26_2x2(self, matrix):
        """
        Calculate determinant of 2x2 matrix modulo 26
        |a b|
        |c d| = ad - bc
        """
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        det = (a * d - b * c) % 26
        return det
    
    def determinant_mod26_3x3(self, matrix):
        """
        Calculate determinant of 3x3 matrix modulo 26
        """
        a, b, c = matrix[0][0], matrix[0][1], matrix[0][2]
        d, e, f = matrix[1][0], matrix[1][1], matrix[1][2]
        g, h, i = matrix[2][0], matrix[2][1], matrix[2][2]
        
        det = (a * (e * i - f * h) - 
               b * (d * i - f * g) + 
               c * (d * h - e * g)) % 26
        return det
    
    def determinant_mod26(self, matrix):
        """
        Calculate determinant based on matrix size
        """
        if self.size == 2:
            return self.determinant_mod26_2x2(matrix)
        else:
            return self.determinant_mod26_3x3(matrix)
    
    def is_invertible(self):
        """
        Check if matrix is invertible modulo 26
        (determinant must be coprime with 26, i.e., gcd(det, 26) = 1)
        """
        det_mod26 = self.determinant_mod26(self.key)
        return self.gcd(det_mod26, 26) == 1
    
    def gcd(self, a, b):
        """
        Calculate greatest common divisor
        """
        while b:
            a, b = b, a % b
        return abs(a)
    
    def adjugate_matrix_2x2(self, matrix):
        """
        Calculate adjugate of 2x2 matrix
        For matrix [[a, b], [c, d]], adjugate = [[d, -b], [-c, a]]
        """
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        
        adj = [[d % 26, (-b) % 26],
               [(-c) % 26, a % 26]]
        
        return adj
    
    def adjugate_matrix_3x3(self, matrix):
        """
        Calculate adjugate of 3x3 matrix (transpose of cofactor matrix)
        """
        # Extract matrix elements
        a, b, c = matrix[0][0], matrix[0][1], matrix[0][2]
        d, e, f = matrix[1][0], matrix[1][1], matrix[1][2]
        g, h, i = matrix[2][0], matrix[2][1], matrix[2][2]
        
        # Calculate cofactors
        cofactor00 = (e * i - f * h)
        cofactor01 = -(d * i - f * g)
        cofactor02 = (d * h - e * g)
        
        cofactor10 = -(b * i - c * h)
        cofactor11 = (a * i - c * g)
        cofactor12 = -(a * h - b * g)
        
        cofactor20 = (b * f - c * e)
        cofactor21 = -(a * f - c * d)
        cofactor22 = (a * e - b * d)
        
        # Create cofactor matrix
        cofactor = [
            [cofactor00, cofactor01, cofactor02],
            [cofactor10, cofactor11, cofactor12],
            [cofactor20, cofactor21, cofactor22]
        ]
        
        # Transpose to get adjugate
        adj = [
            [cofactor[0][0] % 26, cofactor[1][0] % 26, cofactor[2][0] % 26],
            [cofactor[0][1] % 26, cofactor[1][1] % 26, cofactor[2][1] % 26],
            [cofactor[0][2] % 26, cofactor[1][2] % 26, cofactor[2][2] % 26]
        ]
        
        return adj
    
    def inverse_matrix_mod26(self):
        """
        Calculate inverse of key matrix modulo 26
        Formula: K⁻¹ = det⁻¹ × adj(K) mod 26
        """
        # Calculate determinant modulo 26
        det = self.determinant_mod26(self.key)
        
        # Calculate modular inverse of determinant
        det_inv = self.mod_inverse(det, 26)
        
        # Calculate adjugate matrix
        if self.size == 2:
            adj = self.adjugate_matrix_2x2(self.key)
        else:  # size == 3
            adj = self.adjugate_matrix_3x3(self.key)
        
        # Calculate inverse: det_inv * adj mod 26
        inverse = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                val = (det_inv * adj[i][j]) % 26
                row.append(val)
            inverse.append(row)
        
        return inverse
    
    def text_to_numbers(self, text):
        """
        Convert text to numbers (A=0, B=1, ..., Z=25)
        """
        text = text.upper().replace(" ", "")
        return [ord(char) - ord('A') for char in text]
    
    def numbers_to_text(self, numbers):
        """
        Convert numbers back to text
        """
        return ''.join(chr(num + ord('A')) for num in numbers)
    
    def multiply_matrix_vector(self, matrix, vector):
        """
        Multiply matrix by vector modulo 26
        """
        result = []
        for i in range(self.size):
            total = 0
            for j in range(self.size):
                total += matrix[i][j] * vector[j]
            result.append(total % 26)
        return result
    
    def encrypt_block(self, block):
        """
        Encrypt a single block of size n
        """
        return self.multiply_matrix_vector(self.key, block)
    
    def decrypt_block(self, block):
        """
        Decrypt a single block of size n
        """
        inverse_key = self.inverse_matrix_mod26()
        return self.multiply_matrix_vector(inverse_key, block)
    
    def encrypt(self, plaintext):
        """
        Encrypt full plaintext
        """
        # Convert to numbers
        numbers = self.text_to_numbers(plaintext)
        
        # Pad if necessary
        while len(numbers) % self.size != 0:
            numbers.append(23)  # 'X' as padding
        
        # Encrypt block by block
        encrypted_numbers = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            encrypted_block = self.encrypt_block(block)
            encrypted_numbers.extend(encrypted_block)
        
        # Convert back to text
        return self.numbers_to_text(encrypted_numbers)
    
    def decrypt(self, ciphertext):
        """
        Decrypt full ciphertext
        """
        # Convert to numbers
        numbers = self.text_to_numbers(ciphertext)
        
        # Decrypt block by block
        decrypted_numbers = []
        for i in range(0, len(numbers), self.size):
            block = numbers[i:i + self.size]
            decrypted_block = self.decrypt_block(block)
            decrypted_numbers.extend(decrypted_block)
        
        # Convert back to text
        return self.numbers_to_text(decrypted_numbers)
    
    def display_matrix(self, matrix, name="Matrix"):
        """
        Display matrix nicely
        """
        print(f"\n{name}:")
        for row in matrix:
            print(f"  {row}")


def main():
    print("=" * 60)
    print("HILL CIPHER IMPLEMENTATION (2x2 and 3x3)")
    print("=" * 60)
    
    # Interactive mode only
    print("\n INTERACTIVE MODE")
    print("-" * 40)
    
    size = int(input("Enter matrix size (2 or 3): "))
    
    print(f"\nEnter {size}x{size} key matrix (row by row):")
    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            val = int(input(f"  matrix[{i+1}][{j+1}] = "))
            row.append(val)
        matrix.append(row)
    
    try:
        hill = HillCipher(matrix)
        hill.display_matrix(matrix, "Your Key Matrix")
        
        # Show inverse
        inv = hill.inverse_matrix_mod26()
        hill.display_matrix(inv, "Inverse Matrix")
        
        plaintext = input("\nEnter plaintext to encrypt: ")
        ciphertext = hill.encrypt(plaintext)
        print(f"Ciphertext: {ciphertext}")
        
        decrypted = hill.decrypt(ciphertext)
        print(f"Decrypted: {decrypted}")
        
        # Verify
        if plaintext.upper().replace(" ", "")[:len(decrypted)] == decrypted:
            print("\n Encryption and decryption successful!")
    
    except ValueError as e:
        print(f"\n Error: {e}")


if __name__ == "__main__":
    main()