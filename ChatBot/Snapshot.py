#A snapshot of a conversation segment

class Snapshot:

    def __init__(self):
        self.dialog = []
        self.uses = 0 #For pruning
        
    def append(self,s):
        self.dialog.append(s)

    def getFinale(self):
        self.uses += 1
        return self.dialog[-1]

    def getScore(self,sin):
        i = 0
        score = 0
        for j in range(0,len(self.dialog)-1):
            i += 1
            sd = self.dialog[j]
            mp = self.getStringPoints(sd,sin)
            score += 2*mp^i
        return score

    def getStringPoints(self,s0,s1):
        s0 = self.cleanString(s0)
        s1 = self.cleanString(s1)
        s0 = s0.split()
        s1 = s1.split()
        points = 0
        for word in s0:
            if word in s1:
                points += 1
        return points

    def cleanString(self,s0):
        punc = "\"\'.,;()[]{}\\/!?~`"
        s0 = s0.lower()
        for char in punc:
            s0 = s0.replace(char,'')
        l = s0.split()
        out = ''.join(s + ' ' for s in l)
        out = out[0:-1]
        return out


