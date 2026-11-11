try:
    number = 100
    divisor = int(input("Enter the divisor: "))

    result = number / divisor
    print("Result:", result)

except ZeroDivisionError:
    print("Zero division exception has occurred.")

except ValueError:
    print("Value error has occurred.")

else:
    print("Else block is executed.")

finally:
    print("Finally block is executed.")
