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

my_list = [1, 2, 3, 4, 5]
my_list = [1, 2, 3, 4, 5]

my_typed_list: list[str] = ["Hello", "World"]

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
        my_lambda = lambda x: (y:=x**2) + y
        self.X = 10
        
def my_function():
    def my_sub_function():
        pass
    my_sub_function()
    s = 5
    return 5

my_lambda = lambda x: (y:=x**2) + y

print("Hello World!") # this is a comment