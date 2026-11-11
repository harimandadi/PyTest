class Vehicle:
    wheels = 4
    def move(self):
        print("Moving forward...")


class Car(Vehicle):
    def honk(self):
        print("Beep beep!")


class Bike(Vehicle):
   def ring_bell(self):
       print("Ring Ring!")

bike1 = Bike()
bike1.move()
bike1.ring_bell()       
