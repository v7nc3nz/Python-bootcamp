import getpass
import os
import base64
import sqlite3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(BASE_DIR, "secret.db")
aes_key_file = os.path.join(BASE_DIR, "aes.key")

def checkaeskey():
    if os.path.exists(aes_key_file):
        print("key file present\n")
        with open(aes_key_file, "rb") as f:
            return f.read()
    else:
        print("key file is not present\nCreating key file")
        key = get_random_bytes(32)
        with open(aes_key_file, "wb") as f:
            f.write(key)
        os.chmod(aes_key_file, 0o600)
        return key

def encrypt(value: str, aeskey: bytes):
    nonce = get_random_bytes(12)
    cipher = AES.new(aeskey, AES.MODE_GCM, nonce=nonce)
    encrypted_value, tag = cipher.encrypt_and_digest(value.encode("utf-8"))
    return encrypted_value, nonce, tag

def decrypt(value: bytes, aeskey: bytes, nonce: bytes, tag: bytes):
    cipher = AES.new(aeskey, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(value, tag)
    return plaintext.decode("utf-8")

def checkdb():
    if os.path.exists(db_file):
        return
    print("Db file doesn't exist, creating db file")
    with sqlite3.connect(db_file) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS secret (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                nonce TEXT NOT NULL,
                tag TEXT NOT NULL
            )
        ''')

def key_exists(name: str) -> bool:
    """Return True if key exists in DB, False otherwise."""
    if not os.path.exists(db_file):
        return False
    with sqlite3.connect(db_file) as conn:
        cur = conn.execute('SELECT 1 FROM secret WHERE key = ?', (name,))
        return cur.fetchone() is not None

def list_keys() -> None:
    """Print all saved keys."""
    if not os.path.exists(db_file):
        print("Please save a Key first")
        return
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute('SELECT key FROM secret ORDER BY key').fetchall()
    if not rows:
        print("No keys saved yet.")
        return
    for i, (k,) in enumerate(rows, start=1):
        print(f"{i}. {k}")

def insert_or_update_secret(name: str, plaintext: str, aeskey: bytes):
    enc, nonce, tag = encrypt(plaintext, aeskey)
    v = base64.b64encode(enc).decode("ascii")
    n = base64.b64encode(nonce).decode("ascii")
    t = base64.b64encode(tag).decode("ascii")
    with sqlite3.connect(db_file) as conn:
        if key_exists(name):
            conn.execute(
                'UPDATE secret SET value = ?, nonce = ?, tag = ? WHERE key = ?',
                (v, n, t, name)
            )
        else:
            conn.execute(
                'INSERT INTO secret (key, value, nonce, tag) VALUES (?, ?, ?, ?)',
                (name, v, n, t)
            )

def setkey():
    checkdb()
    aeskey = checkaeskey()
    try:
        key_name = input("Enter Key Name: ").strip()
        exists = key_exists(key_name)
        if exists:
            print("Api key already exists.")
            option = input("Select\n1 to update\n2 to exit\nEnter: ").strip()
            if option != "1":
                print("Exiting without changes.")
                return
        value = getpass.getpass("Enter Secret Value: ")
        insert_or_update_secret(key_name, value, aeskey)
        print("Secret saved successfully.")
    except Exception as e:
        print(f"Error in saving Api Key : {e}")

def getkey():
    if not os.path.exists(db_file):
        print("Please save a Key first")
        return
    aeskey = checkaeskey()
    try:
        key_name = input("Enter Key Name to get the value: ").strip()
        with sqlite3.connect(db_file) as conn:
            row = conn.execute(
                'SELECT value, nonce, tag FROM secret WHERE key = ?', (key_name,)
            ).fetchone()
        if row is None:
            print("Api key not found")
            return
        value_b64, nonce_b64, tag_b64 = row
        plaintext = decrypt(
            value=base64.b64decode(value_b64.encode("ascii")),
            aeskey=aeskey,
            nonce=base64.b64decode(nonce_b64.encode("ascii")),
            tag=base64.b64decode(tag_b64.encode("ascii"))
        )
        print(f"{key_name} api key : {plaintext}")
    except Exception as e:
        print(f"Error in getting Api Key : {e}")

def main():
    try:
        option = input("Select options \n1. Save new/Update Api Key.\n2. Retrieve saved Api key\n3. List saved Api keys.\nEnter Option: ").strip()
        match option:
            case "1":
                setkey()
            case "2":
                getkey()
            case "3":
                list_keys()
            case _:
                print("Select valid option\n")
    except KeyboardInterrupt:
        print("\nUser cancelled the selection.")
    except Exception:
        print("Unexpected error.")

if __name__ == "__main__":
    main()
