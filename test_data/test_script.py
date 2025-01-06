from json import dumps, loads
from pathlib import Path


def seven():
    return 7

# BEGIN PARAMETERS
u = seven()
x: int = 5 # this is a comment
y: float = 6
s = """
Hello World!
Goodbye World!
""" # this is another comment
# END PARAMETERS
z = 7 # this is also a comment

z = 9

nooooo = 4.56 # NO PARAM
not_you = "Hello" # no param

def my_first_function():
    g = 5 # should not be saved
    return g

g = 8 + 9

class MyClass:
    X = 8
    def __init__(self):
        pass
    
    def method(self):
        self.X = 9
        
    def method2(self):
        self.X = 10
        
def my_function():
    s = 5
    return 5

print("Hello World!") # this is a comment