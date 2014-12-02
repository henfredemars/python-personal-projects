#Stack of variables for executing opcodes

class Stack:

    def __init__(self):
        self.numbers = []

    def push(self,number):
        self.numbers.append(number)

    def pop(self):
        return self.numbers.pop()

