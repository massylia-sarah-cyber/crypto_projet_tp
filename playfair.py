def toLowerCase(plain):
    """Convert string to lowercase"""
    result = ""
    for char in plain:
        if 'A' <= char <= 'Z':
            result += chr(ord(char) + 32)
        else:
            result += char
    return result

def removeSpaces(plain):
    """Remove all spaces from string"""
    result = ""
    for char in plain:
        if char != ' ':
            result += char
    return result

def generateKeyTable(key, keyT):
    """Generate the 5x5 key square"""
    keyT.clear()
    for i in range(5):
        keyT.append([''] * 5)
    
    # Mark letters that are in the key
    key_letters = []
    for char in key:
        if char != 'j' and char not in key_letters:
            key_letters.append(char)
    
    # Fill key table with key letters
    idx = 0
    for i in range(5):
        for j in range(5):
            if idx < len(key_letters):
                keyT[i][j] = key_letters[idx]
                idx += 1
    
    # Fill remaining letters (skip 'j')
    remaining_letters = []
    for k in range(26):
        letter = chr(k + 97)
        if letter != 'j' and letter not in key_letters:
            remaining_letters.append(letter)
    
    idx = 0
    for i in range(5):
        for j in range(5):
            if keyT[i][j] == '':
                keyT[i][j] = remaining_letters[idx]
                idx += 1

def findPosition(keyT, char):
    """Find position of character in key table"""
    if char == 'j':
        char = 'i'
    
    for i in range(5):
        for j in range(5):
            if keyT[i][j] == char:
                return (i, j)
    return (-1, -1)

def prepareText(string):
    """Prepare text for encryption: handle duplicates and make even length"""
    result = []
    i = 0
    
    while i < len(string):
        # Get current character
        current = string[i]
        result.append(current)
        
        # Check if we need to add padding
        if i + 1 < len(string):
            next_char = string[i + 1]
            if current == next_char:
                # Insert 'x' between duplicate letters
                result.append('x')
                i += 1
            else:
                result.append(next_char)
                i += 2
        else:
            i += 1
    
    # Add 'z' if length is odd
    if len(result) % 2 != 0:
        result.append('z')
    
    return ''.join(result)

def encrypt(string, keyT):
    """Perform encryption"""
    result = []
    
    for i in range(0, len(string), 2):
        char1 = string[i]
        char2 = string[i + 1]
        
        row1, col1 = findPosition(keyT, char1)
        row2, col2 = findPosition(keyT, char2)
        
        if row1 == row2:  # Same row
            result.append(keyT[row1][(col1 + 1) % 5])
            result.append(keyT[row2][(col2 + 1) % 5])
        elif col1 == col2:  # Same column
            result.append(keyT[(row1 + 1) % 5][col1])
            result.append(keyT[(row2 + 1) % 5][col2])
        else:  # Rectangle
            result.append(keyT[row1][col2])
            result.append(keyT[row2][col1])
    
    return ''.join(result)

def decrypt(string, keyT):
    """Perform decryption"""
    result = []
    
    for i in range(0, len(string), 2):
        char1 = string[i]
        char2 = string[i + 1]
        
        row1, col1 = findPosition(keyT, char1)
        row2, col2 = findPosition(keyT, char2)
        
        if row1 == row2:  # Same row
            result.append(keyT[row1][(col1 - 1) % 5])
            result.append(keyT[row2][(col2 - 1) % 5])
        elif col1 == col2:  # Same column
            result.append(keyT[(row1 - 1) % 5][col1])
            result.append(keyT[(row2 - 1) % 5][col2])
        else:  # Rectangle
            result.append(keyT[row1][col2])
            result.append(keyT[row2][col1])
    
    return ''.join(result)

def encryptByPlayfairCipher(string, key):
    """Main encryption function"""
    # Prepare key and text
    key = toLowerCase(removeSpaces(key))
    string = toLowerCase(removeSpaces(string))
    
    # Store original for reference
    original = string
    
    # Generate key table
    keyT = []
    generateKeyTable(key, keyT)
    
    # Prepare text for encryption
    prepared = prepareText(string)
    
    print("\nKey Table (5x5):")
    for row in keyT:
        print(' '.join(row))
    
    print(f"\nOriginal text: {original}")
    print(f"Prepared text (with padding): {prepared}")
    
    # Encrypt
    ciphertext = encrypt(prepared, keyT)
    
    return ciphertext

def decryptByPlayfairCipher(string, key):
    """Main decryption function"""
    # Prepare key and text
    key = toLowerCase(removeSpaces(key))
    string = toLowerCase(removeSpaces(string))
    
    # Generate key table
    keyT = []
    generateKeyTable(key, keyT)
    
    print("\nKey Table (5x5):")
    for row in keyT:
        print(' '.join(row))
    
    # Decrypt
    decrypted = decrypt(string, keyT)
    
    print(f"\nDecrypted with padding: {decrypted}")
    
    # Remove padding 'x' that was inserted between duplicate letters
    result = []
    i = 0
    while i < len(decrypted):
        if i + 2 < len(decrypted) and decrypted[i + 1] == 'x' and decrypted[i] == decrypted[i + 2]:
            # Found pattern: letter + x + same letter -> remove the x
            result.append(decrypted[i])
            i += 2
        else:
            result.append(decrypted[i])
            i += 1
    
    final_result = ''.join(result)
    
    # Remove trailing 'z' if it was added for odd length
    # Check if last character is 'z' and removing it would make the text match the pattern
    if len(final_result) > 0 and final_result[-1] == 'z':
        # Try removing the trailing z
        test_result = final_result[:-1]
        # Check if this might be the original (heuristic)
        # If the last character of the original was 'z', we might be removing a real 'z'
        # For simplicity, we'll assume 'z' at the end is padding
        final_result = test_result
    
    return final_result

# Test with your specific example
print("=" * 60)
print("PLAYFAIR CIPHER - TESTING WITH 'massylia'")
print("=" * 60)

key = "monarchy"
plaintext = "massylia"

print(f"\nKey: {key}")
print(f"Original Plaintext: {plaintext}")

# Encrypt
ciphertext = encryptByPlayfairCipher(plaintext, key)
print(f"\nEncrypted Ciphertext: {ciphertext.upper()}")

# Decrypt
decrypted = decryptByPlayfairCipher(ciphertext, key)
print(f"\nFinal Decrypted Text: {decrypted}")

# Verify
if decrypted == plaintext:
    print("\n✓ SUCCESS! Decrypted text matches original!")
else:
    print(f"\n✗ FAILED! Expected '{plaintext}', got '{decrypted}'")

# Additional test with different inputs
print("\n" + "=" * 60)
print("ADDITIONAL TESTS")
print("=" * 60)

test_cases = [
    ("monarchy", "hello"),
    ("monarchy", "balloon"),
    ("keyword", "instruments"),
    ("playfair", "example")
]

for test_key, test_text in test_cases:
    print(f"\nTesting: Key='{test_key}', Text='{test_text}'")
    encrypted = encryptByPlayfairCipher(test_text, test_key)
    decrypted = decryptByPlayfairCipher(encrypted, test_key)
    
    if decrypted == test_text:
        print(f"✓ Success! '{test_text}' -> '{encrypted.upper()}' -> '{decrypted}'")
    else:
        print(f"✗ Failed! Expected '{test_text}', got '{decrypted}'")

# Main program with user choice
print("\n" + "=" * 60)
print("PLAYFAIR CIPHER - MAIN MENU")
print("=" * 60)

while True:
    print("\nWhat would you like to do?")
    print("1. Encrypt a message")
    print("2. Decrypt a message")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == '1':
        key = input("Enter the key: ")
        plaintext = input("Enter the plaintext to encrypt: ")
        
        ciphertext = encryptByPlayfairCipher(plaintext, key)
        
        print("\n" + "=" * 60)
        print("ENCRYPTION RESULTS")
        print("=" * 60)
        print(f"Key: {key}")
        print(f"Original Plaintext: {plaintext}")
        print(f"Ciphertext: {ciphertext.upper()}")
        print("=" * 60)
        
    elif choice == '2':
        key = input("Enter the key: ")
        ciphertext = input("Enter the ciphertext to decrypt: ")
        
        plaintext = decryptByPlayfairCipher(ciphertext, key)
        
        print("\n" + "=" * 60)
        print("DECRYPTION RESULTS")
        print("=" * 60)
        print(f"Key: {key}")
        print(f"Ciphertext: {ciphertext.upper()}")
        print(f"Decrypted Plaintext: {plaintext}")
        print("=" * 60)
        
    elif choice == '3':
        print("\nGoodbye!")
        break
        
    else:
        print("\nInvalid choice! Please enter 1, 2, or 3.")