#!/usr/bin/env python3

class HillCipherAttack:
    def __init__(self):
        self.mod = 26
    
    def gcd(self, a, b):
        """Calculate greatest common divisor"""
        while b:
            a, b = b, a % b
        return abs(a)
    
    def mod_inverse(self, a, m=26):
        """Calculate modular inverse using extended Euclidean algorithm"""
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"No modular inverse for {a} modulo {m}")
    
    def determinant_mod26(self, matrix):
        """Calculate determinant of 2x2 or 3x3 matrix modulo 26"""
        size = len(matrix)
        
        if size == 2:
            return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
        
        elif size == 3:
            a, b, c = matrix[0][0], matrix[0][1], matrix[0][2]
            d, e, f = matrix[1][0], matrix[1][1], matrix[1][2]
            g, h, i = matrix[2][0], matrix[2][1], matrix[2][2]
            
            det = (a * (e * i - f * h) - 
                   b * (d * i - f * g) + 
                   c * (d * h - e * g)) % 26
            return det
    
    def adjugate_matrix_2x2(self, matrix):
        """Calculate adjugate of 2x2 matrix"""
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        
        adj = [[d % 26, (-b) % 26],
               [(-c) % 26, a % 26]]
        return adj
    
    def adjugate_matrix_3x3(self, matrix):
        """Calculate adjugate of 3x3 matrix"""
        a, b, c = matrix[0][0], matrix[0][1], matrix[0][2]
        d, e, f = matrix[1][0], matrix[1][1], matrix[1][2]
        g, h, i = matrix[2][0], matrix[2][1], matrix[2][2]
        
        cofactor00 = (e * i - f * h)
        cofactor01 = -(d * i - f * g)
        cofactor02 = (d * h - e * g)
        
        cofactor10 = -(b * i - c * h)
        cofactor11 = (a * i - c * g)
        cofactor12 = -(a * h - b * g)
        
        cofactor20 = (b * f - c * e)
        cofactor21 = -(a * f - c * d)
        cofactor22 = (a * e - b * d)
        
        cofactor = [
            [cofactor00, cofactor01, cofactor02],
            [cofactor10, cofactor11, cofactor12],
            [cofactor20, cofactor21, cofactor22]
        ]
        
        adj = [
            [cofactor[0][0] % 26, cofactor[1][0] % 26, cofactor[2][0] % 26],
            [cofactor[0][1] % 26, cofactor[1][1] % 26, cofactor[2][1] % 26],
            [cofactor[0][2] % 26, cofactor[1][2] % 26, cofactor[2][2] % 26]
        ]
        
        return adj
    
    def inverse_matrix(self, matrix):
        """Calculate inverse of matrix modulo 26"""
        size = len(matrix)
        det = self.determinant_mod26(matrix)
        
        if det == 0:
            raise ValueError("Determinant is zero, matrix not invertible")
        
        det_inv = self.mod_inverse(det)
        
        if size == 2:
            adj = self.adjugate_matrix_2x2(matrix)
        else:
            adj = self.adjugate_matrix_3x3(matrix)
        
        inverse = []
        for i in range(size):
            row = []
            for j in range(size):
                val = (det_inv * adj[i][j]) % 26
                row.append(val)
            inverse.append(row)
        
        return inverse
    
    def text_to_numbers(self, text):
        """Convert text to numbers (A=0, B=1, ..., Z=25)"""
        text = text.upper().replace(" ", "")
        return [ord(char) - ord('A') for char in text]
    
    def numbers_to_text(self, numbers):
        """Convert numbers back to text"""
        return ''.join(chr(num + ord('A')) for num in numbers)
    
    def find_key_from_known_plaintext(self, plaintext, ciphertext, size):
        """
        Recover the Hill cipher key using known plaintext-ciphertext pairs
        
        Formula: K = C × P⁻¹ mod 26
        
        Args:
            plaintext: known plaintext string
            ciphertext: corresponding ciphertext string
            size: matrix size (2 or 3)
        
        Returns:
            key_matrix: recovered key matrix
        """
        # Convert to numbers
        P_nums = self.text_to_numbers(plaintext)
        C_nums = self.text_to_numbers(ciphertext)
        
        # Check we have enough letters
        needed_letters = size * size
        if len(P_nums) < needed_letters or len(C_nums) < needed_letters:
            raise ValueError(f"Need at least {needed_letters} letters (got plaintext: {len(P_nums)}, ciphertext: {len(C_nums)})")
        
        # Build plaintext matrix P (size x size)
        P = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append(P_nums[i * size + j])
            P.append(row)
        
        # Build ciphertext matrix C (size x size)
        C = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append(C_nums[i * size + j])
            C.append(row)
        
        print("\n Building matrices from your data:")
        print(f"  Plaintext matrix P:")
        for row in P:
            print(f"    {row}")
        print(f"\n  Ciphertext matrix C:")
        for row in C:
            print(f"    {row}")
        
        # Calculate P⁻¹
        try:
            P_inv = self.inverse_matrix(P)
            print(f"\n  P⁻¹ matrix:")
            for row in P_inv:
                print(f"    {row}")
        except ValueError as e:
            raise ValueError(f"Plaintext matrix is not invertible modulo 26: {e}")
        
        # Calculate K = C × P⁻¹ mod 26
        K = []
        for i in range(size):
            row = []
            for j in range(size):
                total = 0
                for k in range(size):
                    total += C[i][k] * P_inv[k][j]
                row.append(total % 26)
            K.append(row)
        
        return K
    
    def encrypt(self, key, plaintext):
        """Encrypt using given key"""
        size = len(key)
        numbers = self.text_to_numbers(plaintext)
        
        # Pad if necessary
        while len(numbers) % size != 0:
            numbers.append(23)  # 'X'
        
        encrypted_numbers = []
        for i in range(0, len(numbers), size):
            block = numbers[i:i + size]
            result = []
            for j in range(size):
                total = 0
                for k in range(size):
                    total += key[j][k] * block[k]
                result.append(total % 26)
            encrypted_numbers.extend(result)
        
        return self.numbers_to_text(encrypted_numbers)


def main():
    print("=" * 70)
    print("HILL CIPHER - KNOWN PLAINTEXT ATTACK")
    print("=" * 70)
    print("\nCe programme retrouve la matrice de chiffrement de Hill")
    print("à partir de paires (texte clair, texte chiffré) fournies par l'utilisateur.")
    
    attack = HillCipherAttack()
    
    # Demander la taille de la matrice
    print("\n" + "-" * 70)
    size = int(input("Entrez la taille de la matrice (2 ou 3) : "))
    
    needed_letters = size * size
    
    print(f"\n Pour une matrice {size}x{size}, vous avez besoin de {needed_letters} lettres.")
    print("   (Soit 2 blocs de 2 lettres pour 2x2, ou 3 blocs de 3 lettres pour 3x3)")
    
    # Demander le texte clair
    print("\n" + "-" * 70)
    plaintext = input(f"Entrez le texte clair connu ({needed_letters} lettres) : ").upper()
    plaintext = plaintext.replace(" ", "")
    
    if len(plaintext) < needed_letters:
        print(f" Erreur: Vous devez entrer au moins {needed_letters} lettres!")
        exit(1)
    
    # Demander le texte chiffré
    ciphertext = input(f"Entrez le texte chiffré correspondant ({needed_letters} lettres) : ").upper()
    ciphertext = ciphertext.replace(" ", "")
    
    if len(ciphertext) < needed_letters:
        print(f" Erreur: Vous devez entrer au moins {needed_letters} lettres!")
        exit(1)
    
    print("\n" + "=" * 70)
    print(" LANCEMENT DE L'ATTAQUE...")
    print("=" * 70)
    
    try:
        # Trouver la matrice de chiffrement
        recovered_key = attack.find_key_from_known_plaintext(plaintext[:needed_letters], 
                                                              ciphertext[:needed_letters], 
                                                              size)
        
        print("\n" + "=" * 70)
        print(" MATRICE DE CHIFFREMENT TROUVÉE :")
        print("=" * 70)
        for row in recovered_key:
            print(f"  {row}")
        
        # Vérification avec le même texte
        print("\n" + "=" * 70)
        print(" VÉRIFICATION")
        print("=" * 70)
        
        # Chiffrer le texte clair avec la matrice trouvée
        encrypted_test = attack.encrypt(recovered_key, plaintext[:needed_letters])
        expected = ciphertext[:needed_letters]
        
        print(f"Texte clair original : {plaintext[:needed_letters]}")
        print(f"Chiffré attendu      : {expected}")
        print(f"Chiffré obtenu       : {encrypted_test}")
        
        if encrypted_test == expected:
            print("\n SUCCÈS! La matrice de chiffrement est correcte!")
        else:
            print("\n Échec de la vérification...")
        
        # Tester sur un nouveau message
        print("\n" + "=" * 70)
        print(" TEST SUR UN NOUVEAU MESSAGE")
        print("=" * 70)
        test_msg = input("Entrez un nouveau message à chiffrer avec la matrice trouvée : ")
        
        if test_msg:
            encrypted = attack.encrypt(recovered_key, test_msg)
            print(f"\nMessage original : {test_msg}")
            print(f"Message chiffré  : {encrypted}")
            
            # Déchiffrer pour vérifier (optionnel)
            print("\n Vous pouvez maintenant utiliser cette matrice")
            print("   dans le programme de chiffrement de Hill pour déchiffrer.")
    
    except ValueError as e:
        print(f"\n ERREUR: {e}")
        print("\nAssurez-vous que:")
        print(f"   - Vous avez entré {needed_letters} lettres exactement")
        print("   - La matrice de texte clair est inversible modulo 26")
        print("   - Les lettres sont de A à Z uniquement")


if __name__ == "__main__":
    main()