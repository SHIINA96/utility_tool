class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, sid):
        super().__init__(name)
        self.sid = sid
