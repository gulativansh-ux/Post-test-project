import bcrypt

def generatePassword(plainText):
    # Fix: Explicitly convert the string to raw bytes
    hashed_bytes = bcrypt.hashpw(plainText.encode('utf-8'), bcrypt.gensalt(rounds=12))
    return hashed_bytes.decode('utf-8')
 


