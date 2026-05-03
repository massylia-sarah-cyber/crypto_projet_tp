letterGoodness = [0.0817, 0.0149, 0.0278, 0.0425, 0.127, 0.0223, 0.0202, 0.0609, 0.0697, 0.0015, 0.0077, 0.0402, 0.0241, 0.0675, 0.0751, 0.0193, 0.0009, 0.0599, 0.0633, 0.0906, 0.0276, 0.0098, 0.0236, 0.0015, 0.0197, 0.0007]

omessage = input("Enter the encrypted message: ").upper()  # FIXED: convert to uppercase
omessage2 = omessage
possibilitylist = []

def shiftletter(letter, shiftvalue):
    if letter == ' ':
        return ' '
    else:
        oldletter = ord(letter)
        newletter = oldletter - shiftvalue  # FIXED: subtract for decryption
        if newletter > 90:
            newletter -= 26
        if newletter < 65:
            newletter += 26
        return chr(newletter)

def testgoodness(testmessage):
    total = 0
    for char in testmessage:
        if char == ' ':
            continue
        index = ord(char) - 65  # Now char is always uppercase (0-25)
        total += letterGoodness[index]
    return total

def shiftmessage(message, shiftvalue):
    newmessage = ''
    for char in message:
        newmessage += shiftletter(char, shiftvalue)
    return newmessage

def addtolist(message):
    possibilitylist.append(testgoodness(message))

for shift in range(26):  # 0 to 25
    addtolist(shiftmessage(omessage2, shift))

maxgoodness = max(possibilitylist)
best_shift = possibilitylist.index(maxgoodness)
print(f"Best shift: {best_shift}")
print(f"Decrypted message: {shiftmessage(omessage2, best_shift)}")