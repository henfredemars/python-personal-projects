#A database of snapshots

import os, pickle
from time import sleep
from Snapshot import Snapshot

class Database:

    def __init__(self):
        self.history = []
        self.historyLength = 14
        self.snapshots = []
        self.lastss = Snapshot()

    def addSnapshot(self,ss):
        self.snapshots.append(ss)
        self.history.append(ss)
        self.maintainHistory()

    def size(self):
        return len(self.snapshots)

    def writeDatabase(self):
        print("Writing database...")
        if os.path.isfile("database.dat"):
            os.remove("database.dat")
        file = open("database.dat",mode="wb")
        pickle.dump(self.snapshots,file)
        file.close()
        print("Database written. {} Snapshots".format(len(self.snapshots)))

    def readDatabase(self):
        print("Reading database...")
        if not os.path.isfile("database.dat"):
            print("Could not locate database.dat.")
            return
        file = open("database.dat",mode="rb")
        self.snapshots = pickle.load(file)

    def getFinale(self,sin,which=0):
        scores = self.getScores(sin)
        if not scores:
            return "..."
        list3 = list(zip(scores,self.snapshots))
        list3 = sorted(list3,key=lambda x:x[0])
        scores, ssl = zip(*list3)
        ss = ssl[which]
        while ss in self.history:
            try:
                which += 1
                ss = ssl[which]
            except:
                return "..."
        self.history.append(ss)
        self.maintainHistory()
        return ss.getFinale()

    def prune(self,usesLowerLimit):
        for item in self.snapshots:
            if item.uses < usesLowerLimit:
                self.snapshots.remove(item)

    def maintainHistory(self):
        if len(self.history) > self.historyLength:
            self.history = self.history[-self.historyLength:]
        
    def getScores(self,sin):
        answer = []
        for ss in self.snapshots:
            answer.append(ss.getScore(sin))
        return answer

    def getSnapshot(self,i):
        return self.snapshots[i]
