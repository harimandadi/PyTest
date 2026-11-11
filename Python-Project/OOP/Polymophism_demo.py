class Animal:
    def speak(self):
        print("Animal makes a sound")

class Dog(Animal):
    def speak(self):
        print("Dog is barking")


class Cat(Animal):
    def speak(self):
        print("Cat says meow")


dog = Dog()
dog.speak()

cat = Cat()
cat.speak()