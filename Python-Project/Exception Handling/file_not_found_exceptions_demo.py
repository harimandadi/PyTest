try:
    file = open("employee.txt", "r")
    content = file.read()
    print(content)
except FileNotFoundError:
    print("The file was not found.")