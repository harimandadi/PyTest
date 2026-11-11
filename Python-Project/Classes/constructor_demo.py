class Car:
    wheels = 4
    name = ""
    color = ""

    def __init__(self, car_name, car_color):
        self.name = car_name
        self.color = car_color

    def describe(self):
        print(self.name)
        print(self.color)
        print(self.wheels)

car1 = Car("BMW" , "White")
car1.describe() 

car2 = Car("Tesla" , "Black")
car2.describe() 
