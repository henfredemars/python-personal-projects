#Stack of Task objects

class GoalStack:

    def __init__(self):
        self.position = 0
        self.size = 0
        self.name = ""
        self.list = []

    def pop(self):
        if self.position == self.size-1:
            self.position -= 1
        self.size -= 1
        return self.list.pop()

    def push(self, task):
        self.list.append(task)
        self.size += 1
        self.position = self.size-1

    def getBackwardMoves(self):
        return self.position

    def getForwardMoves(self):
        return self.size-1-self.position

    def jumpToTop(self):
        self.position = self.size-1

    def lookForward(self):
        if self.position < self.size-1:
            self.position += 1
            return True
        else:
            return False

    def lookBackward(self):
        if self.position > 0:
            self.position -= 1
            return True
        else:
            return False

    def getTask(self):
        return self.list[self.position]

    
