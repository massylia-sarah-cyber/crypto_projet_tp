# we use kaiski test + the IC
#!/usr/bin/env python3
from argparse import ArgumentParser
import re
from collections import Counter
from itertools import product

class KasiskiTest:
    def __init__(self, text, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.text = re.sub(f"[^{alphabet}]", "", text.upper())
        self.abc = alphabet

    def find_distance_between_sequences(self, min_seq_length=3):
        """Find distances between repeated sequences"""
        sequences = {}
        
        for i in range(len(self.text) - min_seq_length + 1):
            for length in range(min_seq_length, min(6, len(self.text) - i + 1)):
                seq = self.text[i:i + length]
                if seq in sequences:
                    if i not in sequences[seq]:
                        sequences[seq].append(i)
                else:
                    sequences[seq] = [i]

        sequences_cleaned = {seq: positions for seq, positions in sequences.items() if len(positions) > 1}

        distances = []
        for positions in sequences_cleaned.values():
            for i in range(len(positions) - 1):
                distance = positions[i + 1] - positions[i]
                if distance > 0:
                    distances.append(distance)

        return distances

    def get_primefactors(self, number):
        """Return all prime factors of a number"""
        if number < 2:
            return []
        
        factors = []
        i = 2
        while i * i <= number:
            while number % i == 0:
                factors.append(i)
                number //= i
            i += 1
        if number > 1:
            factors.append(number)
        return factors

    def get_candidate_key_length(self, distances):
        """Find most common prime factors among distances"""
        if not distances:
            return []
        
        prime_factors = []
        for distance in distances:
            prime_factors.extend(self.get_primefactors(distance))

        if not prime_factors:
            return []

        frequency = Counter(prime_factors)
        sorted_frequency = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
        return sorted_frequency

    def find_shift_for_column(self, column):
        """Find the most likely shift for a column using chi-squared test"""
        # English letter frequencies
        english_freq = {
            'A': 0.0817, 'B': 0.0149, 'C': 0.0278, 'D': 0.0425, 'E': 0.1270,
            'F': 0.0223, 'G': 0.0202, 'H': 0.0609, 'I': 0.0697, 'J': 0.0015,
            'K': 0.0077, 'L': 0.0402, 'M': 0.0241, 'N': 0.0675, 'O': 0.0751,
            'P': 0.0193, 'Q': 0.0009, 'R': 0.0599, 'S': 0.0633, 'T': 0.0906,
            'U': 0.0276, 'V': 0.0098, 'W': 0.0236, 'X': 0.0015, 'Y': 0.0197, 'Z': 0.0007
        }
        
        best_shift = 0
        best_score = float('inf')
        
        for shift in range(26):
            # Decrypt column with this shift
            decrypted = ""
            for char in column:
                idx = (self.abc.index(char) - shift) % 26
                decrypted += self.abc[idx]
            
            # Calculate chi-squared statistic
            observed = Counter(decrypted)
            chi_square = 0
            
            for letter in self.abc:
                expected = english_freq[letter] * len(column)
                observed_count = observed.get(letter, 0)
                if expected > 0:
                    chi_square += ((observed_count - expected) ** 2) / expected
            
            if chi_square < best_score:
                best_score = chi_square
                best_shift = shift
        
        return best_shift

    def find_key(self, keylength):
        """Find the key using frequency analysis on each column"""
        key = ""
        
        for offset in range(keylength):
            # Extract column
            column = ""
            for pos in range(offset, len(self.text), keylength):
                column += self.text[pos]
            
            if column:
                shift = self.find_shift_for_column(column)
                key += self.abc[shift]
            else:
                key += "?"
        
        return key

    def vigenere_decrypt(self, ciphertext, key):
        """Decrypt Vigenère cipher"""
        plaintext = ""
        key_length = len(key)
        
        for i, char in enumerate(ciphertext):
            if char in self.abc:
                shift = self.abc.index(key[i % key_length])
                plain_index = (self.abc.index(char) - shift) % 26
                plaintext += self.abc[plain_index]
            else:
                plaintext += char
        
        return plaintext

    def index_of_coincidence(self, text):
        """Calculate Index of Coincidence"""
        n = len(text)
        if n < 2:
            return 0
        
        freq = Counter(text)
        ic = sum(count * (count - 1) for count in freq.values()) / (n * (n - 1))
        return ic

    def attack(self):
        """Perform Kasiski attack"""
        print("\n=== Kasiski Analysis ===")
        distances = self.find_distance_between_sequences()
        
        if distances:
            print(f"Found {len(distances)} repeated sequence distances")
            candidate_key_length = self.get_candidate_key_length(distances)
            
            print("\nPrime factor frequencies:")
            for factor, freq in candidate_key_length[:10]:
                print(f"  {factor}: {freq} times")
            
            suggested = [factor for factor, _ in candidate_key_length[:3]]
            return suggested
        else:
            print("No repeated sequences found.")
            return []

    def try_key_lengths(self, key_lengths):
        """Try different key lengths and show results"""
        print("\n=== Trying Candidate Key Lengths ===")
        
        for key_len in key_lengths:
            key = self.find_key(key_len)
            decrypted = self.vigenere_decrypt(self.text, key)
            ic = self.index_of_coincidence(decrypted)
            
            print(f"\nKey Length: {key_len}")
            print(f"Key: {key}")
            print(f"IC: {ic:.4f} (0.066 = English)")
            print(f"Decrypted text: {decrypted[:100]}...")
            
            # Also try multiples of the key length
            for mult in [2, 3, 4]:
                mult_len = key_len * mult
                if mult_len <= 20:
                    key2 = self.find_key(mult_len)
                    decrypted2 = self.vigenere_decrypt(self.text, key2)
                    ic2 = self.index_of_coincidence(decrypted2)
                    print(f"  Length {mult_len} (2x): Key={key2}, IC={ic2:.4f}")

def main():
    cipher = input("Enter cipher text: ")
    
    kasiski = KasiskiTest(cipher)
    suggestions = kasiski.attack()
    
    if suggestions:
        # Also try nearby lengths
        all_lengths = set(suggestions)
        for length in suggestions:
            for nearby in [length-1, length+1, length*2]:
                if 1 <= nearby <= 20:
                    all_lengths.add(nearby)
        
        kasiski.try_key_lengths(sorted(all_lengths)[:6])
    else:
        # Try common lengths
        kasiski.try_key_lengths([3, 4, 5, 6, 7, 8])

if __name__ == '__main__':
    main()