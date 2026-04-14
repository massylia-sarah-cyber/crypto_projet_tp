import random
import base64

def rand_key(length):
    return "".join(str(random.randint(0, 1)) for _ in range(length))

def xor(a, b):
    return "".join("0" if a[i] == b[i] else "1" for i in range(len(a)))

def feistel_round(left, right, key):
    f = xor(right, key)
    new_left = right
    new_right = xor(left, f)
    return new_left, new_right

def text_to_binary(text):
    return "".join(format(ord(c), "08b") for c in text)

def binary_to_text(binary):
    text = ""
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
    return text

def feistel_encrypt(plain_text, rounds=4):
    pt_bin = text_to_binary(plain_text)
    
    # Ensure even length by padding if needed
    if len(pt_bin) % 2 != 0:
        pt_bin += "0"
    
    n = len(pt_bin) // 2
    left, right = pt_bin[:n], pt_bin[n:]
    
    keys = [rand_key(len(right)) for _ in range(rounds)]
    
    for i in range(rounds):
        left, right = feistel_round(left, right, keys[i])
    
    cipher_bin = left + right
    
    # Convert binary to bytes then to base64 for safe storage
    byte_array = bytearray()
    for i in range(0, len(cipher_bin), 8):
        if i + 8 <= len(cipher_bin):
            byte = int(cipher_bin[i:i+8], 2)
            byte_array.append(byte)
    
    cipher_text = base64.b64encode(byte_array).decode('utf-8')
    
    return cipher_text, keys

def feistel_decrypt(cipher_text_b64, keys):
    # Decode from base64 to bytes then to binary
    byte_array = base64.b64decode(cipher_text_b64)
    ct_bin = ""
    for byte in byte_array:
        ct_bin += format(byte, "08b")
    
    n = len(ct_bin) // 2
    left, right = ct_bin[:n], ct_bin[n:]
    
    for i in reversed(range(len(keys))):
        right, left = feistel_round(right, left, keys[i])
    
    plain_bin = left + right
    
    # Remove padding if necessary
    plain_text = binary_to_text(plain_bin)
    
    return plain_text

def save_keys(keys, filename="feistel_keys.txt"):
    with open(filename, "w") as f:
        for key in keys:
            f.write(key + "\n")
    print(f"Keys saved to {filename}")

def load_keys(filename="feistel_keys.txt"):
    keys = []
    try:
        with open(filename, "r") as f:
            keys = [line.strip() for line in f.readlines()]
        return keys
    except FileNotFoundError:
        print("Key file not found!")
        return None

print("=" * 60)
print("FEISTEL CIPHER")
print("=" * 60)

while True:
    print("\nWhat would you like to do?")
    print("1. Encrypt a message")
    print("2. Decrypt a message")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == '1':
        plaintext = input("Enter the plaintext to encrypt: ")
        rounds = input("Enter number of rounds (default 4): ")
        
        if rounds.isdigit():
            rounds = int(rounds)
        else:
            rounds = 4
        
        ciphertext, keys = feistel_encrypt(plaintext, rounds)
        
        print("\n" + "=" * 60)
        print("ENCRYPTION RESULTS")
        print("=" * 60)
        print(f"Original Message: {plaintext}")
        print(f"Ciphertext (Base64): {ciphertext}")
        print(f"Rounds used: {rounds}")
        
        save_option = input("\nSave keys to file? (y/n): ").lower()
        if save_option == 'y':
            save_keys(keys)
        
        print("=" * 60)
        
    elif choice == '2':
        ciphertext = input("Enter the ciphertext (Base64 format): ")
        key_option = input("Load keys from file? (y/n): ").lower()
        
        if key_option == 'y':
            keys = load_keys()
            if keys is None:
                continue
        else:
            print("Enter the round keys (comma separated):")
            keys_input = input("Keys: ")
            keys = [k.strip() for k in keys_input.split(",")]
        
        try:
            decrypted = feistel_decrypt(ciphertext, keys)
            
            print("\n" + "=" * 60)
            print("DECRYPTION RESULTS")
            print("=" * 60)
            print(f"Ciphertext: {ciphertext}")
            print(f"Decrypted Message: {decrypted}")
            print("=" * 60)
        except Exception as e:
            print(f"\nError: Decryption failed. {str(e)}")
        
    elif choice == '3':
        print("\nGoodbye!")
        break
        
    else:
        print("\nInvalid choice! Please enter 1, 2, or 3.")

print("\n" + "=" * 60)
print("DEMONSTRATION")
print("=" * 60)

test_text = "massylia"
print(f"Testing with: '{test_text}'")

encrypted, test_keys = feistel_encrypt(test_text, rounds=4)
decrypted = feistel_decrypt(encrypted, test_keys)

print(f"Original: {test_text}")
print(f"Encrypted (Base64): {encrypted}")
print(f"Decrypted: {decrypted}")
print(f"Success: {test_text == decrypted}")
print("=" * 60)