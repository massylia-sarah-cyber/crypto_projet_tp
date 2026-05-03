letterGoodness = [0.0817, 0.0149, 0.0278, 0.0425, 0.127, 0.0223, 0.0202, 0.0609, 0.0697, 0.0015, 0.0077, 0.0402, 0.0241, 0.0675, 0.0751, 0.0193, 0.0009, 0.0599, 0.0633, 0.0906, 0.0276, 0.0098, 0.0236, 0.0015, 0.0197, 0.0007]

omessage = input("Enter the encrypted message: ").upper()

def shiftletter(letter, shiftvalue):
    if letter == ' ':
        return ' '
    else:
        oldletter = ord(letter)
        newletter = oldletter - shiftvalue  # Decryption (subtract)
        if newletter > 90:
            newletter -= 26
        if newletter < 65:
            newletter += 26
        return chr(newletter)

def shiftmessage(message, shiftvalue):
    newmessage = ''
    for jj in message:
        newmessage += shiftletter(jj, shiftvalue)
    return newmessage

# Display all 26 possible shifts
print("\n" + "="*50)
print("All possible shifts (human chooses the correct one):")
print("="*50)

for shift in range(26):
    decrypted = shiftmessage(omessage, shift)
    print(f"Shift {shift:2d}: {decrypted}")