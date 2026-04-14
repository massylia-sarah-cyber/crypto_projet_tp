# One Time Pad Algorithm

def stringEncryption(text, key):
    cipherText = ""
    cipher = []
    
    for i in range(len(key)):
        cipher.append(ord(text[i]) - ord('A') + ord(key[i]) - ord('A'))
    
    for i in range(len(key)):
        if cipher[i] > 25:
            cipher[i] = cipher[i] - 26
    
    for i in range(len(key)):
        x = cipher[i] + ord('A')
        cipherText += chr(x)
    
    return cipherText

def stringDecryption(s, key):
    plainText = ""
    plain = []
    
    for i in range(len(key)):
        plain.append(ord(s[i]) - ord('A') - (ord(key[i]) - ord('A')))
    
    for i in range(len(key)):
        if (plain[i] < 0):
            plain[i] = plain[i] + 26
    
    for i in range(len(key)):
        x = plain[i] + ord('A')
        plainText += chr(x)
    
    return plainText

# Main program with user choice
print("=" * 50)
print("ONE TIME PAD CIPHER")
print("=" * 50)

while True:
    print("\nWhat would you like to do?")
    print("1. Encrypt a message")
    print("2. Decrypt a message")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == '1':
        plainText = input("Enter the plaintext to encrypt: ")
        key = input("Enter the key (must be same length as plaintext): ")
        
        # Convert to uppercase and check length
        plainText = plainText.upper().replace(" ", "")
        key = key.upper().replace(" ", "")
        
        if len(plainText) != len(key):
            print(f"Error: Key length ({len(key)}) must match plaintext length ({len(plainText)})")
            continue
        
        encryptedText = stringEncryption(plainText, key)
        
        print("\n" + "=" * 50)
        print("ENCRYPTION RESULTS")
        print("=" * 50)
        print(f"Original Message: {plainText}")
        print(f"Key: {key}")
        print(f"Cipher Text: {encryptedText}")
        print("=" * 50)
        
    elif choice == '2':
        cipherText = input("Enter the ciphertext to decrypt: ")
        key = input("Enter the key (must be same length as ciphertext): ")
        
        # Convert to uppercase and check length
        cipherText = cipherText.upper().replace(" ", "")
        key = key.upper().replace(" ", "")
        
        if len(cipherText) != len(key):
            print(f"Error: Key length ({len(key)}) must match ciphertext length ({len(cipherText)})")
            continue
        
        decryptedText = stringDecryption(cipherText, key)
        
        print("\n" + "=" * 50)
        print("DECRYPTION RESULTS")
        print("=" * 50)
        print(f"Cipher Text: {cipherText}")
        print(f"Key: {key}")
        print(f"Decrypted Message: {decryptedText}")
        print("=" * 50)
        
    elif choice == '3':
        print("\nGoodbye!")
        break
        
    else:
        print("\nInvalid choice! Please enter 1, 2, or 3.")

# Example with any word
print("\n" + "=" * 50)
print("EXAMPLE DEMONSTRATION")
print("=" * 50)

plainText = "CRYPTOGRAPHY"
key = "SECRETKEYABC"
encrypted = stringEncryption(plainText, key)
decrypted = stringDecryption(encrypted, key)

print(f"Plaintext: {plainText}")
print(f"Key: {key}")
print(f"Encrypted: {encrypted}")
print(f"Decrypted: {decrypted}")
print("=" * 50)