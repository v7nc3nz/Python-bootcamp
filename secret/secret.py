def setkey():
    try:
        key = input("Enter Key Name: ")
        value = input("Enter Secret Value: ")
        file = open(".secret","a")
        file.write(f"{key}:{value}\n")
        file.close
    except Exception as e:
        print(f"File write error: {e}")

def getkey():
    try:
        key = input("Enter Key Name to get the value: ")
        with open(".secret","r") as file:
            for line in file:
                if line.startswith(key):
                    value = line.strip()
                    print(f"Api key for {key} : {value.split(":",1)[1]}")
                    found = True
                    break
            if not found:    
                print("Api Key not found.\n")            
    except Exception as e:
        print(f"File read error: {e}")

def getlist():
    try:
        with open(".secret","r") as file:
            for i, line in enumerate(file,start=1):    
                constant = line.strip()
                print(f"{i}. {constant.split(":",-1)[0]}")
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