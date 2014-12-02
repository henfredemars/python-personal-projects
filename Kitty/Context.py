#Symbol table as a tree-like structure
#
#Should only create Context explicitly for the master Context
#Do not hold references to a context unless you are the one
# who created the master context in the first place because
# your copy can become outdated as the tree evolves

from Stack import Stack

class Context:

    def __init__(self):
        self.parent = None
        self.child = None
        self.symbols = dict()
        self.returnpc = None

    def setSymbol(self,symbol,value):
        self.symbols[symbol] = value

    def deleteSymbol(self,symbol):
        del self.symbols[symbol]

    def getSymbol(self,symbol):
        return self.symbols.get(symbol)

    def setReturnPc(self,pc):
        if not self.returnpc:
            self.returnpc = pc
        else:
            raise Exception('Context - return address already set')

    def getReturnPc(self):
        val = self.returnpc
        if not val:
            raise Exception('Context - pc not set')
        self.returnpc = None
        return val

    def newContext(self):
        if self.child:
            raise Exception("Context - may only have one child")
        c = Context()
        c.parent = self
        self.child = c
        return c

    def destroy(self):
        if self.parent:
            parentsParent = self.parent.parent
            if self.parent.parent:
                self.parent.parent.child = self
            parentsSymbols = self.parent.symbols
            parentsReturnPc = self.parent.returnpc
            self.parent = parentsParent
            self.child = None
            self.symbols = parentsSymbols
            self.returnpc = parentsReturnPc
        else:
            self.symbols = dict()
        return self

    def __str__(self):
        print(self.symbols)
