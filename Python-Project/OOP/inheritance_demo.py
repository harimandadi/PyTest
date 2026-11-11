class Vehicle:
    wheels = 4
    def move(self):
        print("Moving forward...")




class Car(Vehicle):
    def honk(self):
        print("Beep beep!")



car1 = Car()
car1.move()
car1.honk()
