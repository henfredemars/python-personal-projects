#Kitty ASM compiler for the Kitty langauge!

from Expression import Expression

class Compiler:

    def __init__(self):
        self.sourceCode = []
        self.sourceFile = None
        self.bytecode = []
        self.funbytecode = {}
        self.controlPairs = []
        self.bindDefine = []
        self.funStart = {}

    def loadFile(self,file):
        with open(file,'r') as fd:
            allLines = fd.read()
        self.sourceFile = file
        self.sourceCode = allLines.split('\n')
        self.sourceCode = [source.strip() for source in self.sourceCode]
        self.sourceCode = [source for source in self.sourceCode if source]
        print("Read {} lines.".format(len(self.sourceCode)))

    def includeFile(self,file,ind):
        file += ".kitty"
        with open(file,'r') as fd:
            allLines = fd.read()
        allLines = allLines.split('\n')
        self.sourceCode[ind+1:ind+1] = [line.strip() for line in allLines]
        self.sourceCode = [source for source in self.sourceCode if source]
        print("Read {} lines on include.".format(len(allLines)))

    def getBytecode(self):
        return self.bytecode

    def compileFunctionBody(self,lines):
        c = Compiler()
        c.sourceCode = [line.strip() for line in lines if line.strip()]
        c.compile()
        return c.getBytecode()[:-1]

    def write(self):
        if not self.sourceFile:
            raise Exception("Compiler - no source file loaded yet")
        if not self.bytecode:
            self.compile()
        fnameArr = self.sourceFile.split('.')
        fname = fnameArr[0] + '.kit'
        with open(fname,'w') as fd:
            for line in self.bytecode:
                fd.write(line + "\n")
        print("Wrote {} lines.".format(len(self.bytecode)))

    def getBinding(self,lineNumber):
        for j in range(len(self.bindDefine)):
            if self.bindDefine[j][0] == lineNumber:
                self.bytecode.append(self.bindDefine[j][1])
                return True
        return False

    def compile(self):

        #Includes
        i = 0
        while True:
            if i > len(self.sourceCode)-1:
                break
            if self.sourceCode[i].startswith("include"):
                line = self.sourceCode[i]
                line = line[len("include"):]
                filename = self.sourceCode[i].split(" ")[1]
                self.includeFile(filename,i)
                del self.sourceCode[i]
                i -= 1
            i += 1

        #Extract functions and compile
        for i in range(len(self.sourceCode)):
            if i >= len(self.sourceCode):
                break
            if self.sourceCode[i].startswith("function "):
                funname,argslist = getNameAndArgs(self.sourceCode[i])
                startLoc = i
                depthCount = 1
                while True:
                    startLoc += 1
                    line = self.sourceCode[startLoc]
                    if line.startswith("if ") or line.startswith("while "):
                        depthCount += 1
                    elif line.startswith("end"):
                        depthCount -= 1
                    if depthCount == 0:
                        break
                functionLines = self.sourceCode[i+1:startLoc]
                functionCode = self.compileFunctionBody(functionLines)
                prepFC = []
                argslist.reverse()
                for item in argslist:
                    prepFC.append("STORE %s" % item)
                prepFC.extend(functionCode)
                self.sourceCode[i:startLoc+1] = []
                self.funbytecode[funname] = (argslist,prepFC)
                
        #Mark all other statement/end pairs
        stateStack = []
        controlEnter = ['if ','while ']
        for i in range(len(self.sourceCode)):
            for controlWord in controlEnter:
                if self.sourceCode[i].startswith(controlWord):
                    stateStack.append((i,))
            if self.sourceCode[i].startswith("end"):
                if len(stateStack[-1]) == 1:
                    litem = stateStack.pop()
                    self.controlPairs.append((litem[0],i))
                    
        #Bytecode generation loop
        for i in range(len(self.sourceCode)):

            #Handle bound lines
            self.getBinding(i)

            #Classify line of source code
            assign = False
            for j in range(1,len(self.sourceCode[i])-1):
                if self.sourceCode[i][j] == "=":
                    if self.sourceCode[i][j+1] != "=":
                        if self.sourceCode[i][j-1] != "=":
                            assign = True
            printing = False
            if self.sourceCode[i].startswith("printugly!"):
                printing = True
            readinput = False
            if self.sourceCode[i].startswith("input!"):
                readinput = True
            commenting = False
            if self.sourceCode[i].startswith("#"):
                commenting = True
            ifstatement = False
            if self.sourceCode[i].startswith("if "):
                ifstatement = True
            whilestatement = False
            if self.sourceCode[i].startswith("while "):
                whilestatement = True
            returnstatement = False
            if self.sourceCode[i].startswith("return"):
                returnstatement = True

            #Emit bytecodes
            if printing:
                line = self.sourceCode[i]
                line = line[10:]
                expr = Expression(line)
                expr.parse()
                self.bytecode += expr.getBytecode()
                self.bytecode += ["PRINT"]
            elif readinput:
                line = self.sourceCode[i]
                line = line[5:]
                expr = Expression(line)
                expr.parse()
                self.bytecode += expr.getBytecode()
                self.bytecode += ["INPUT " + self.sourceCode[i].split(" ")[1]]
            elif assign:
                line = self.sourceCode[i].split("=",1)
                targetSymbol = line[0].strip()
                expression = line[1].strip()
                if symbolIsValid(targetSymbol):
                    expr = Expression(expression)
                    expr.parse()
                    self.bytecode += expr.getBytecode()
                    self.bytecode += ["STORE " + targetSymbol]
                else:
                    raise Exception("Compiler - invalid symbol")
            elif commenting:
                pass
            elif ifstatement:
                expr = Expression(self.sourceCode[i][3:])
                expr.parse()
                self.bytecode += expr.getBytecode()
                ctrlPair = None
                for j in range(len(self.controlPairs)):
                    if self.controlPairs[j][0] == i:
                        ctrlPair = self.controlPairs[j]
                if not ctrlPair:
                    raise Exception("Compiler - no matching end")
                self.bytecode += ["JUMPIFNOT {}".format(ctrlPair[1])]
            elif whilestatement:
                expr = Expression(self.sourceCode[i][6:])
                expr.parse()
                self.bytecode += expr.getBytecode()
                ctrlPair = None
                for j in range(len(self.controlPairs)):
                    if self.controlPairs[j][0] == i:
                        ctrlPair = self.controlPairs[j]
                if not ctrlPair:
                    raise Exception("Compiler - no matching end")
                self.bytecode += ["JUMPIFNOT {}".format(ctrlPair[1])]
                self.bindDefine.append((ctrlPair[1],
                                   "JUMP {}".format(ctrlPair[0])))
            elif returnstatement:
                if self.sourceCode[i][6:].strip():
                    expr = Expression(self.sourceCode[i][6:])
                    expr.parse()
                    self.bytecode += expr.getBytecode()
                self.bytecode += ["JUMPOLDCONTEXT"]
            elif not self.sourceCode[i].startswith("end"):
                expr = Expression(self.sourceCode[i])
                expr.parse()
                self.bytecode += expr.getBytecode()
            self.bytecode.append("MARKLINE {}".format(i+1))
        self.bytecode += ["TERM"]

        #Append function codes
        unmarkCode = [code for code in self.bytecode
                      if not code.startswith("MARK")]
        for tup in self.funbytecode.keys():
            self.funStart[tup] = len(unmarkCode)
            self.bytecode += self.funbytecode[tup][1]

        #Calculate jump targets
        for i in range(len(self.bytecode)):
            line = self.bytecode[i]
            if line.startswith("JUMPNEWCONTEXT"):
                target = line.split()[1]
                target = target.replace("+","")
                lineNumber = self.funStart[target]
                self.bytecode[i] = "JUMPNEWCONTEXT %s" % lineNumber
        for i in range(len(self.bytecode)):
            line = self.bytecode[i]
            if line.startswith("JUMP") and (
                not line.startswith("JUMPOLDCONTEXT")) and (
                    not line.startswith("JUMPNEWCONTEXT")):
                s = line.split()
                oldTarget = s[1]
                for j in range(len(self.bytecode)):
                    line2 = self.bytecode[j]
                    if line2.startswith("MARKLINE"):
                        s2 = line2.split()
                        if s2[1] == oldTarget:
                            newTarget = j-1
                            break
                s[1] = str(newTarget)
                self.bytecode[i] = ' '.join(s)
        i = -1
        while True:
            i += 1
            try:
                line = self.bytecode[i]
            except IndexError:
                break
            if line.startswith("MARKLINE"):
                del self.bytecode[i]
                for j in range(i,len(self.bytecode)):
                    line2 = self.bytecode[j]
                    if line2.startswith("JUMPIF"):
                        lsl = line2.split()
                        lsl[1] = str(int(lsl[1])-1)
                        line2 = ' '.join(lsl)
                        self.bytecode[j] = line2
                i -= 1
        
def getNameAndArgs(functionDec):
    functionDec = functionDec.replace("function ","")
    fname = functionDec.split("(")[0].strip()
    args = functionDec.replace(fname,"").strip()
    args = args[1:-1].replace(" ","")
    args = args.split(",")
    return (fname,args)

def symbolIsValid(symbol):
    for op in Expression.operators:
        if op in symbol:
            return False
    noStart = ['0','1','2','3','4','5','6','7','8','9','$']
    otherIllegal = ['%','#','(',')','`','\'','\"',' ','\n',
                    '\t','\\','/']
    illegalSymbols = ["not","is","if","while","include","return"]
    for item in otherIllegal:
        if item in symbol:
            return False
    if symbol[0] in noStart:
        return False
    if symbol.strip() in illegalSymbols:
        return False
    return True

if __name__=='__main__':
    file = r'testSource.kitty'
    compiler = Compiler()
    compiler.loadFile(file)
    compiler.compile()
    compiler.write()
    input("Press ENTER to continue...")
    
