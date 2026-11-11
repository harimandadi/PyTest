

status = 100

match status:
    case 200:
        print("OK")
    case 301:
        print("Moved Permanently")
    case 404:
        print("Not Found")

    case _:
        print("Status Unknown")    



            

