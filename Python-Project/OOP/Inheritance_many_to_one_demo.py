class Vehicle:
    wheels = 4
    def move(self):
        print("Moving forward...")

class Rentable:
    def rent(self):
        print("This vehicle is available for rent.")


class Car(Vehicle, Rentable):
    def honk(self):
        print("Beep beep!")

car1 = Car()
car1.move()
car1.rent()        