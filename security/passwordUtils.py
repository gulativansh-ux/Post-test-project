import bcrypt

def generatePassword(plainText:str):
    # Fix: Explicitly convert the string to raw bytes
    hashed_bytes = bcrypt.hashpw(plainText.encode('utf-8'), bcrypt.gensalt(rounds=12))
    return hashed_bytes.decode('utf-8')
 

def checkPassword(plaintext: str,hashPassword: str):
    result = bcrypt.checkpw(plaintext.encode('utf-8'),hashPassword.encode('utf-8'))
    return result

