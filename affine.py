# Affine Cipher Algorithm Encrypt/Decrypt (Substitution Cipher)

# Create dictionaries to map letters to indices and vice versa
letter_to_index = {chr(i + ord('A')): i for i in range(26)}
index_to_letter = {i: chr(i + ord('A')) for i in range(26)}

def encryptAffine(plaintext, alpha, beta, m):
    # Remove spaces
    plaintext = "".join(plaintext.split())
    
    if not plaintext.isalpha() or len(plaintext) < 1:
        return "Error: Please use only alphabetic characters."
    
    ciphertext = []
    for char in plaintext:
        idx = letter_to_index[char.upper()]
        encrypted_idx = (alpha * idx + beta) % m
        ciphertext.append(index_to_letter[encrypted_idx])
    
    return "".join(ciphertext)

def decryptAffine(ciphertext, alpha, beta, m):
    # Remove spaces
    ciphertext = "".join(ciphertext.split())
    
    if not ciphertext.isalpha() or len(ciphertext) < 1:
        return "Error: Please use only alphabetic characters."
    
    # Find modular multiplicative inverse of alpha
    alpha_inv = None
    for i in range(m):
        if (i * alpha) % m == 1:
            alpha_inv = i
            break
    
    if alpha_inv is None:
        return "Error: Modular inverse not found."
    
    plaintext = []
    for char in ciphertext:
        idx = letter_to_index[char.upper()]
        decrypted_idx = (alpha_inv * (idx - beta)) % m
        plaintext.append(index_to_letter[decrypted_idx])
    
    return "".join(plaintext)

# Main code
import math

m = 26

# Get user choice
user_input = input("Would you like to perform encryption or decryption?\nPlease Enter 'e' or 'd': ").lower()

isValid = True

if user_input not in ['e', 'd']:
    print("Invalid input, please enter 'e' for encryption or 'd' for decryption.")
    isValid = False
else:
    # Get alpha and beta values
    try:
        alpha = int(input(f"Enter an alpha value between 1 and {m-1} (int): "))
        beta = int(input(f"Enter a beta value between 0 and {m-1} (int): "))
        
        if alpha < 1 or alpha > (m - 1):
            print("Please enter a valid number in proper range for alpha.")
            isValid = False
        elif beta < 0 or beta > (m - 1):
            print("Please enter a valid number in proper range for beta.")
            isValid = False
        elif math.gcd(alpha, m) != 1:
            print(f"The GCD of alpha and {m} must be equal to 1.")
            isValid = False
    except ValueError:
        print("Invalid numeric input, please enter a valid whole number.")
        isValid = False

# Process encryption or decryption
if user_input == 'e' and isValid:
    plaintext = input("\nPlease enter the plaintext to encrypt:\n")
    ciphertext = encryptAffine(plaintext, alpha, beta, m)
    print("\nPlaintext (Original): " + plaintext)
    print("Ciphertext (Generated): " + ciphertext)
    print("Alphabet Size:", m)
    print("Alpha Value Chosen:", alpha)
    print("Beta Value Chosen:", beta)

elif user_input == 'd' and isValid:
    ciphertext = input("\nPlease enter the ciphertext to decrypt:\n")
    plaintext = decryptAffine(ciphertext, alpha, beta, m)
    print("\nCiphertext (Original): " + ciphertext)
    print("Plaintext (Generated): " + plaintext)
    print("Alphabet Size:", m)
    print("Alpha Value Chosen:", alpha)
    print("Beta Value Chosen:", beta)

else:
    print("\nAn error has occurred, please try again.")