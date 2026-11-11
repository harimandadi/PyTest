class Employee:
    name = "John"
    __salary = 1000

    def show_salary(self):
        return self.__salary

    

class Run:
    e = Employee()
    print(e.name)        
    print(e.show_salary())   

