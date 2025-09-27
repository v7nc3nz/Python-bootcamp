import os
import sqlite3

db_file = "secret.db"

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
                    value TEXT NOT NULL)'''
                       )
        conn.commit()
        conn.close()



def setkey():
    checkdb()
    try:
        key = input("Enter Key Name: ")
        value = input("Enter Secret Value: ")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT into secret (key,value) values (?,?)',(key, value))
        conn.commit()

    except Exception as e:
        print(f"Error in saving Api Key : {e}")

def getkey():
    try:
        key = input("Enter Key Name to get the value: ")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM secret WHERE key = ?', (key,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"\n{key} api key : {row[0]}")
        conn.close()
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