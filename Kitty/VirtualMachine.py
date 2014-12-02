#Core Virtual Machine for the Kitty Language interpreter

from Context import Context
from Stack import Stack
from time import sleep
import os

class VirtualMachine:

    def __init__(self, debug=False):
        self.file = None
        self.bytecode = None
        self.debug = debug

    def dprint(self, string, end="\n"):
        if self.debug:
            print("DEBUG: " + string, end=end)
            
    def loadFile(self, filename):
        with open(filename) as file:
            codes = file.read()
        self.bytecode = codes.split('\n')
        for i in range(len(self.bytecode)):
            self.bytecode[i] = self.bytecode[i].split()
        if not self.bytecode[0]:
            print("File is empty")
            return
        newcode = []
        for i in range(len(self.bytecode)):
            if self.bytecode[i]:
                newcode.append(self.bytecode[i])
        self.bytecode = newcode
        self.dprint("LOADED BYTECODE")
        for i in range(len(self.bytecode)):
            line = ""
            for item in self.bytecode[i]:
                line = line + " " + item
            self.dprint(line)

    def run(self):
        pc = 0
        context = Context()
        stack = Stack()
        self.dprint("Begining execution...")
        while True:
            line = self.bytecode[pc]
            opcode = line[0]
            arg = ' '.join(line[1:])
            if opcode == "LOAD":
                try:
                    if float(arg) == int(arg):
                        self.dprint("Load '{}' as int"
                                    .format(arg))
                        stack.push(int(arg))
                    else:
                        self.dprint("Load '{}' as float"
                                    .format(arg))
                        stack.push(float(arg))
                except ValueError:
                    if context.getSymbol(arg) is not None:
                        self.dprint("Load symbol '{}'"
                                    .format(arg))
                        stack.push(context.getSymbol(
                            arg))
                    else:
                        self.dprint("Raw load '{}'".
                                    format(arg))
                        stack.push(arg)
            elif opcode == "LOADSTR":
                arg = arg[1:-1]
                stack.push(arg)
                self.dprint("Load '{}' as string".format(arg))
            elif opcode == "STORE":
                val = stack.pop()
                self.dprint("Store '{}' as symbol '{}'"
                            .format(val,arg))
                context.setSymbol(arg,val)
            elif opcode == "ADD":
                val2 = stack.pop()
                val1 = stack.pop()
                if isinstance(val2,str) or isinstance(val1,str):
                    stack.push(''.join([str(val1),str(val2)]))
                    self.dprint("Add {} and {} as str".format(val1,val2))
                else:
                    stack.push(val1 + val2)
                    self.dprint("Add {} and {}".format(val1,val2))
            elif opcode == "SUBTRACT":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 - val2)
                self.dprint("Subtract {} from {}".format(
                    val2,val1))
            elif opcode == "MULTIPLY":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 * val2)
                self.dprint("Multiply {} and {}".format(
                    val1,val2))
            elif opcode == "DIVIDE":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 / val2)
                self.dprint("Divide {} and {}".format(
                    val1,val2))
            elif opcode == "LESSTHAN":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 < val2)
                self.dprint("{} < {}".format(val1,val2))
            elif opcode == "GREATERTHAN":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 > val2)
                self.dprint("{} > {}".format(val1,val2))
            elif opcode == "EQUALS":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val1 == val2)
                self.dprint("{} == {}".format(val1,val2))
            elif opcode == "NEGATE":
                val1 = stack.pop()
                stack.push(-1*val1)
                self.dprint("Negate {}".format(val1))
            elif opcode == "BNOT":
                val1 = stack.pop()
                stack.push(not val1)
                self.dprint("BoolNot {}".format(val1))
            elif opcode == "AND":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val2 and val1)
                self.dprint("{} AND {}".format(val2,val1))
            elif opcode == "OR":
                val2 = stack.pop()
                val1 = stack.pop()
                stack.push(val2 or val1)
                self.dprint("{} OR {}".format(val2,val1))
            elif opcode == "POWER":
                val1 = stack.pop()
                val2 = stack.pop()
                stack.push(val2**val1)
            elif opcode == "PAUSE":
                if arg:
                    val = arg
                else:
                    val = stack.pop()
                sleep(val)
                self.dprint("Sleep for {} seconds".format(val))
            elif opcode == "JUMPNEWCONTEXT":
                context = context.newContext()
                context.setReturnPc(pc)
                pc = int(arg)-1
                self.dprint("Procedure call to line {}"
                            .format(pc))
            elif opcode == "JUMPOLDCONTEXT":
                pc = context.getReturnPc()
                context = context.destroy()
                self.dprint("Return to caller")
            elif opcode == "JUMPIFNOT":
                loc = int(arg)
                condition = not stack.pop()
                if condition:
                    self.dprint("Jump to {}".format(loc))
                    pc = loc-1
                else:
                    self.dprint("Jump not taken")
            elif opcode == "JUMP":
                loc = int(arg)
                pc = loc-1
                self.dprint("Jumping back to loop condition.")
            elif opcode == "INPUT":
                if arg:
                    val = input(arg)
                else:
                    val = input()
                try:
                    if float(val) == int(val):
                        stack.push(int(val))
                    else:
                        stack.push(float(val))
                except ValueError:
                    stack.push(val)
                self.dprint("Read input '{}'".format(val))
            elif opcode == "PRINT":
                if arg:
                    val = context.getSymbol(arg)
                else:
                    val = stack.pop()
                self.dprint("Printing '{}'".format(val))
                if isinstance(val,str):
                    val = val.replace("\\n","\n")
                    val = val.replace("\_"," ")
                    val = val.replace("\\","")
                print(val,end="")
            elif opcode == "TERM":
                self.dprint("Terminating...")
                input("Press ENTER to continue...")
                break
            else:
                self.dprint("Unexpected opcode '{}'".format(opcode))
                raise Exception("VirtualMachine - Invalid Opcode")
            pc += 1

    
if __name__=='__main__':
    vm = VirtualMachine(False)
    vm.loadFile("testSource.kit")
    vm.run()
