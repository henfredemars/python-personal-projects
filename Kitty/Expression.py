#General expression parser for the Kitty language

class Expression:

    #In reverse order of operations, operators and opcodes
    operators = ["`","|","&",">","<","==","+","-","*","/","~","^","!"]
    opcodes = ["BNOT","OR","AND","GREATERTHAN","LESSTHAN","EQUALS",
               "ADD","SUBTRACT","MULTIPLY","DIVIDE","NEGATE",
               "POWER","JUMPNEWCONTEXT"]

    def __init__(self,text):
        self.text = text
        self.leftChild = None
        self.rightChild = None
        self.parsed = False
        self.subbytecodes = []

    def parse(self):
        self.parsed = True
        self.text = replaceIfNotInQuotes(self.text,"not ","`")
        self.text = replaceIfNotInQuotes(self.text," is ","==")
        self.text = replaceIfNotInQuotes(self.text," ","")
        if "`" in self.text and "(" not in self.text:
            if self.text.count("`") == 1:
                self.text = self.text.replace("`","")
                self.text = "`" + self.text
        balance = 0
        startLoc = -1
        endLoc = 0
        subexprind = 0
        for i in range(len(self.text)):
            if self.text[i] == "\"" and startLoc == -1:
                startLoc = i
            elif self.text[i] == "\"":
                endLoc = i
        if startLoc != -1:
            theString = self.text[startLoc+1:endLoc]
            self.text = self.text.replace("\"" + theString + "\"",
                           "${}".format(subexprind))
            self.subbytecodes += ["LOADSTR \"{}\"".format(theString)]
            self.subbytecodes = self.subbytecodes + ["STORE ${}".
                                        format(subexprind)]

        for i in range(len(self.text)):
            if self.text[i] == "(":
                balance = balance + 1
            elif self.text[i] == ")":
                balance = balance - 1
            if balance < 0:
                raise Exception("Expression - unmached parenthesis")
        if balance != 0:
            raise Exception("Expression - unmached parenthesis")
        for i in range(len(self.text)):
            if self.text[i] == "\"":
                if i > 0:
                    if self.text[i-1] != "\\":
                        balance = balance + 1
                else:
                    balance = balance + 1
        if balance > 2:
            raise Exception("Expression - only one string per subexpression")
        elif balance == 1:
            raise Exception("Expression - unbalanced quotations")
        subexprind += 1
        while "(" in self.text:
            lastopenpos = 0
            for i in range(len(self.text)):
                if self.text[i] == "(":
                    lastopenpos = i
                elif self.text[i] == ")":
                    subexprstring = self.text[lastopenpos+1:i]
                    subexpr = Expression(subexprstring)
                    subexpr.parse()
                    bytecodes = subexpr.getBytecode()
                    bytecodes.append("STORE ${}".format(subexprind))
                    self.text = self.text.replace(
                        "(" + subexprstring + ")", "${}".format(
                            subexprind))
                    subexprind = subexprind + 1
                    self.subbytecodes = self.subbytecodes + bytecodes
                    break
        if len(self.text) == 2 and self.text[0] == "-":
            self.text = list(self.text)
            self.text[0] = "~"
            self.text = ''.join(self.text)
        for i in range(len(self.text)-1):
            if self.text[i] in Expression.operators:
                if self.text[i+1] == "-":
                    self.text = list(self.text)
                    self.text[i+1] = '~'
                    self.text = ''.join(self.text)
        for op in Expression.operators:
            if self.text.find(op) != -1:
                index = self.text.find(op)
                leftString = self.text[:index]
                rightString = self.text[index+len(op):]
                unaryAllowed = ["~","`","!"]
                leftSet = False
                rightSet = False
                if leftString:
                    leftSet = True
                    expr = Expression(leftString)
                    self.leftChild = expr
                    self.leftChild.parse()
                if rightString:
                    rightSet = True
                    expr = Expression(rightString)
                    self.rightChild = expr
                    self.rightChild.parse()
                if leftSet != rightSet and op not in unaryAllowed:
                    raise Exception("Expression - parse error")
                self.text = self.text[index:index+len(op)]
                return

    def getPostOrder(self):
        if not self.parsed:
            raise Exception("Expression - must be parsed first")
        vals = []
        postOrderRecursive(self,vals)
        return vals

    def getBytecode(self):
        if not self.parsed:
            self.parse()
        bytecodes = []
        vals = self.getPostOrder()
        for val in vals:
            if "," in val.text:
                bytecodes.extend(parseArgList(val.text))
            elif not val.text in Expression.operators:
                if not isValidSymbol(val.text):
                    throwExcep = False
                    try:
                        a = float(val.text)
                    except ValueError:
                        throwExcep = True
                    if throwExcep:
                        raise Exception("Expression - illegal symbol name")
                bytecodes.append("LOAD " + val.text)
            elif val.text == "!":
                ind = Expression.operators.index(val.text)
                bytecodes.append(Expression.opcodes[ind] + " +"
                                 + val.leftChild.text)
            else:
                ind = Expression.operators.index(val.text)
                bytecodes.append(Expression.opcodes[ind])
        return self.subbytecodes + bytecodes
                
    def __str__(self):
        res = []
        if self.text:
            res.append(self.text)
            res.append(self.leftChild.__str__())
            res.append(self.rightChild.__str__())
        res = [item for item in res if item]
        return '\n'.join(res)


def postOrderRecursive(expr,vals):
    if not expr:
        return
    if not expr.text == "!":
        postOrderRecursive(expr.leftChild,vals)
    postOrderRecursive(expr.rightChild,vals)
    vals.append(expr)

def isValidSymbol(symbol):
    for op in Expression.operators:
        if symbol.find(op) != -1 and op != "-":
            return False
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    illegalSymbols = ["if","while","is","not"]
    for num in numbers:
        if symbol[0] == num:
            return False
    otherIllegal = ["="]
    for o in otherIllegal:
        if symbol.find(o) != -1:
            return False
    if symbol in illegalSymbols:
        return False
    return True

def replaceIfNotInQuotes(text,find,replace):
    cnt = 0
    for i in range(len(text)):
        if text[i] == "\"":
            if i > 0:
                if text[i-1] != "\\":
                    cnt += 1
            else:
                cnt += 1
    if not cnt:
        return text.replace(find,replace)
    if cnt % 2 != 0:
        raise Exception("Expression - unbalanced quotations")
    marker = 0
    markers = []
    strings = []
    while "\"" in text:
        text,strings,markers,marker = replaceSubstring(text,strings,markers,marker)
    text.replace(find,replace)
    for i in range(len(markers)):
        mark = markers[i]
        text = text.replace(mark,strings[i])
    return text

def replaceSubstring(text,strings,markers,marker):
    for i in range(len(text)):
        preval = None
        if i > 0:
            preval = text[i-1]
        val = text[i]
        if val == "\"" and preval != "\\":
            for j in range(i+1,len(text)):
                preval2 = None
                if j > 0:
                    preval2 = text[j-1]
                val2 = text[j]
                if val2 == "\"" and preval2 != "\\":
                    strings.append(text[i:j+1])
                    text = text.replace(text[i:j+1],"${}".format(marker))
                    markers.append("${}".format(marker))
                    marker += 1
                    return (text,strings,markers,marker)
    raise Exception("Expression - should have returned")

def parseArgList(text):
    text = text.strip()
    vars2load = text.split(",")
    bytecodes = []
    for v in vars2load:
        bytecodes.append("LOAD %s" % v)
    return bytecodes

if __name__=='__main__':
    expr = Expression("fun! asas")
    print(expr.getBytecode())
