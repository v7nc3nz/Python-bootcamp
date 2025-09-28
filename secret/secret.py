import os
import base64
import sqlite3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

db_file = "secret.db"
aes_key_file = "aes.key"

def checkaeskey():
    if os.path.exists(aes_key_file):
        print("key file present\n")
        file = open(aes_key_file, "rb")
        key = file.read()
        file.close()
        return key
    else:
        print("key file is not present\nCreating key file")
        key = get_random_bytes(32)
        file = open(aes_key_file, "wb")
        file.write(key)
        file.close()

def encrypt(value: str,aeskey: bytes):
    nonce = get_random_bytes(12)
    cipher = AES.new(aeskey,AES.MODE_GCM,nonce=nonce)
    encrypted_value, tag = cipher.encrypt_and_digest(value.encode("utf-8"))
    return encrypted_value, nonce, tag

def decrypt(value: bytes,aeskey: bytes,nonce: bytes, tag: bytes):
    cipher = AES.new(aeskey,AES.MODE_GCM,nonce=nonce)
    plaintext = cipher.decrypt_and_verify(value,tag)
    return plaintext.decode("utf-8")

def checkdb():
    if os.path.exists(db_file):
        return
    else:
        print(f"Db file doesn't exist, creating db file")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS secret (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    nonce TEXT NOT NULL,
                    tag TEXT NOT NULL)'''
                       )
        conn.commit()
        conn.close()



def setkey():
    checkdb()
    aeskey = checkaeskey()
    try:
        key = input("Enter Key Name: ").strip()
        value = input("Enter Secret Value: ").strip()
        encrypted_value, nonce, tag = encrypt(value,aeskey)
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT into secret (key,value,nonce,tag) values (?,?,?,?)',
                       (key, 
                        base64.b64encode(encrypted_value).decode("ascii"),
                        base64.b64encode(nonce).decode("ascii"),
                        base64.b64encode(tag).decode("ascii")
                        )
                    )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error in saving Api Key : {e}")

def getkey():
    aeskey = checkaeskey()
    try:
        key = input("Enter Key Name to get the value: ").strip()
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT value,nonce,tag FROM secret WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            print("Api key not found")
            return
        
        value,nonce,tag = row
        plaintext = decrypt(
            value=base64.b64decode(value.encode("ascii")),
            aeskey=aeskey,
            nonce=base64.b64decode(nonce.encode("ascii")),
            tag=base64.b64decode(tag.encode("ascii"))
            )
        print(f"{key} api key : {plaintext}")
    except Exception as e:
        print(f"Error in getting Api Key : {e}")

def getlist():
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT key from secret')
        rows = cursor.fetchall()
        for i,row in enumerate(rows, start=1):
            print(f"{i}. {row[0]}") 
    except Exception as e:
        print(f"Error in finding the list\n")

def main():
    try:
        option = input("Select options \n1. Save new Api Key.\n2. Retrieve saved Api key\n3. List saved Api keys.\nEnter Option: ")
        match option:
            case "1":
                setkey()
            case "2":
                getkey()
            case "3":
                getlist()

            case _:
                print("Select valid option\n")
    except Exception as e:
        print("User cancelled the selection.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("User cancelled the selection.")