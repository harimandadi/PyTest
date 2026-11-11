age = int(input("Enter your age: "))

if age < 18:
    raise ValueError("You must be 18 or older to register.")

print("Registration successful!")