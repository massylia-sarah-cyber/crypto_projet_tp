#!/usr/bin/env python3
import re
from collections import Counter

class VigenereCryptanalysis:
    def __init__(self, ciphertext, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        # Keep only letters and convert to uppercase
        self.ciphertext = re.sub(f"[^{alphabet}]", "", ciphertext.upper())
        self.alphabet = alphabet
        self.n = len(self.ciphertext)
        
        # English letter frequencies (from A to Z)
        self.english_freq = [
            0.0817, 0.0149, 0.0278, 0.0425, 0.1270, 0.0223, 0.0202, 0.0609, 0.0697, 0.0015,
            0.0077, 0.0402, 0.0241, 0.0675, 0.0751, 0.0193, 0.0009, 0.0599, 0.0633, 0.0906,
            0.0276, 0.0098, 0.0236, 0.0015, 0.0197, 0.0007
        ]

    def index_of_coincidence(self, text):
        """
        Calculate Index of Coincidence for a given text
        IC = sum(n_i * (n_i - 1)) / (N * (N - 1))
        where n_i is frequency of letter i, N is text length
        """
        N = len(text)
        if N < 2:
            return 0
        
        freq = Counter(text)
        ic = sum(count * (count - 1) for count in freq.values()) / (N * (N - 1))
        return ic

    def find_key_length(self, max_key_length=20):
        """
        Find probable key length by analyzing IC for each possible k
        For the correct key length, the average IC of subsequences should be ~0.066 (English)
        """
        print("\n=== Index of Coincidence Analysis ===")
        print(f"{'Key Length':<12} {'Avg IC':<10} {'Verdict'}")
        print("-" * 40)
        
        results = []
        for k in range(1, max_key_length + 1):
            # Split ciphertext into k subsequences
            subsequences = [''] * k
            for i, char in enumerate(self.ciphertext):
                subsequences[i % k] += char
            
            # Calculate IC for each subsequence
            ic_values = [self.index_of_coincidence(subseq) for subseq in subsequences]
            
            # Average IC
            avg_ic = sum(ic_values) / k
            
            # Determine if this key length is promising
            verdict = ""
            if 0.06 <= avg_ic <= 0.07:
                verdict = "*** GOOD (likely English) ***"
            elif avg_ic > 0.07:
                verdict = "(higher than English)"
            elif avg_ic < 0.05:
                verdict = "(too low, unlikely)"
            
            results.append((k, avg_ic, verdict))
            print(f"{k:<12} {avg_ic:<10.6f} {verdict}")
        
        # Sort by how close IC is to 0.066 and return top candidates
        results.sort(key=lambda x: abs(x[1] - 0.066))
        return [k for k, ic, _ in results[:5]]

    def find_key_letter_from_subsequence(self, subsequence):
        """
        Find the key letter for a given subsequence using frequency analysis
        For each possible shift (0-25), decrypt the subsequence and compute
        chi-squared goodness-of-fit with English frequencies
        """
        best_shift = 0
        best_chi2 = float('inf')
        
        for shift in range(26):
            # Decrypt the subsequence with this shift
            decrypted = ""
            for char in subsequence:
                idx = (ord(char) - ord('A') - shift) % 26
                decrypted += chr(idx + ord('A'))
            
            # Calculate chi-squared statistic
            observed = Counter(decrypted)
            chi2 = 0
            total = len(decrypted)
            
            for i, letter in enumerate(self.alphabet):
                expected = self.english_freq[i] * total
                observed_count = observed.get(letter, 0)
                if expected > 0:
                    chi2 += ((observed_count - expected) ** 2) / expected
            
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift
        
        # Convert shift to key letter (shift applied to plaintext to get ciphertext)
        # key_letter = shift (since key_letter encrypts by adding its position)
        return self.alphabet[best_shift]

    def find_key(self, key_length):
        """
        Find the full key by analyzing each subsequence
        """
        print(f"\n=== Finding Key for Length {key_length} ===")
        
        key = ""
        subsequences = [''] * key_length
        
        # Split into subsequences
        for i, char in enumerate(self.ciphertext):
            subsequences[i % key_length] += char
        
        # Find each key letter
        for i, subseq in enumerate(subsequences):
            if len(subseq) > 0:
                key_letter = self.find_key_letter_from_subsequence(subseq)
                key += key_letter
                print(f"  Subsequence {i+1}: length={len(subseq):3d}, key letter = '{key_letter}'")
        
        return key

    def decrypt(self, key):
        """
        Decrypt the ciphertext using the found key
        """
        plaintext = ""
        key_length = len(key)
        
        for i, char in enumerate(self.ciphertext):
            shift = ord(key[i % key_length]) - ord('A')
            plain_idx = (ord(char) - ord('A') - shift) % 26
            plaintext += chr(plain_idx + ord('A'))
        
        return plaintext

    def attack(self):
        """
        Perform full cryptanalysis
        """
        print("\n" + "="*60)
        print("VIGENÈRE CRYPTANALYSIS USING INDEX OF COINCIDENCE")
        print("="*60)
        print(f"Ciphertext length: {self.n} characters")
        print(f"Ciphertext: {self.ciphertext[:100]}{'...' if self.n > 100 else ''}")
        
        # Step 1: Find probable key lengths using IC
        candidate_lengths = self.find_key_length()
        
        print(f"\n📊 Most likely key lengths: {candidate_lengths}")
        
        # Step 2: Try each candidate key length
        best_result = None
        best_key = None
        best_ic = 0
        
        for k in candidate_lengths[:3]:  # Try top 3 candidates
            # Find key
            key = self.find_key(k)
            
            # Decrypt
            plaintext = self.decrypt(key)
            
            # Calculate IC of plaintext to verify
            plaintext_ic = self.index_of_coincidence(plaintext)
            
            print(f"\n  Key: {key}")
            print(f"  Decrypted text IC: {plaintext_ic:.6f}")
            print(f"  Decrypted (first 80 chars): {plaintext[:80]}...")
            
            if abs(plaintext_ic - 0.066) < abs(best_ic - 0.066) or best_result is None:
                best_ic = plaintext_ic
                best_result = plaintext
                best_key = key
        
        # Step 3: Show best result
        print("\n" + "="*60)
        print("✅ BEST RESULT")
        print("="*60)
        print(f"Key: {best_key}")
        print(f"Index of Coincidence: {best_ic:.6f} (expected 0.066 for English)")
        print(f"\nDecrypted message:\n{best_result}")
        
        return best_key, best_result

def main():
    print("Vigenère Cipher Cryptanalysis Tool")
    print("-" * 40)
    
    # Get ciphertext from user
    ciphertext = input("Enter the ciphertext: ")
    
    # Create cryptanalysis instance
    analysis = VigenereCryptanalysis(ciphertext)
    
    # Perform attack
    key, plaintext = analysis.attack()

if __name__ == "__main__":
    main()