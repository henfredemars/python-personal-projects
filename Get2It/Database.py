#Database

import pickle, os
from tkinter import messagebox
from tkinter import filedialog as tkFileDialog
import threading
from time import sleep

class Database:

    def __init__(self):
        self.dataVersionNumber = 1
        self.configVersionNumber = 1
        self.lastfilename = ""
        self.databaseLock = threading.Lock()
        self.writeConfigLock = threading.Lock()

    def getDatabaseNameFromUser(self):
        filename = tkFileDialog.askopenfilename()
        databasechosen = False
        if not filename:
            return self.lastfilename
        if (filename[-3:] != "dat" and filename[-10:] !=
            "inprogress"):
            messagebox.showwarning(
                "File Error",
                "\"" + filename + "\"" + " does not appear to be a "
                "valid database.")
        else:
            databasechosen = True
        if not databasechosen:
            return self.lastfilename
        else:
            self.lastfilename = filename
            return filename

    def saveDatabaseByUser(self):
        filename = tkFileDialog.asksaveasfilename()
        if self.lastfilename:
            self.lastfilename = filename + ".dat"
        return self.lastfilename

    def writeConfig(self):
        self.writeConfigLock.acquire()
        if os.path.isfile("config.info"):
            os.remove("config.info")
        file = open("config.info.inprogress","wb")
        pickle.dump(self.configVersionNumber,file)
        pickle.dump(self.lastfilename,file)
        file.close()
        os.rename("config.info.inprogress","config.info")
        self.writeConfigLock.release()

    def getLastFilename(self):
        return self.lastfilename

    def writeDatabase(self, goalTaskList, textAreaObj):
        self.databaseLock.acquire()
        self.writeConfig()
        file = open(self.lastfilename + ".inprogress","wb")
        pickle.dump(self.dataVersionNumber,file)
        pickle.dump(goalTaskList,file)
        pickle.dump(textAreaObj.get(1.0,9999.9999),file)
        file.close()
        if os.path.isfile(self.lastfilename):
            os.remove(self.lastfilename)
        os.rename(self.lastfilename + ".inprogress",self.lastfilename)
        self.databaseLock.release()

    def readDatabase(self):
         if os.path.isfile("config.info.inprogress"):
             if os.path.isfile("config.info"):
                 os.remove("config.info.inprogress")
             else:
                 os.rename("config.info.inprogress","config.info")
         if not self.lastfilename:
             if os.path.isfile("config.info"):
                 file = open("config.info","rb")
                 version = pickle.load(file)
                 if version != self.configVersionNumber:
                     messagebox.showwarning(
                        "Config Version Warning",
                        "Configuration file version mismatch!")
                 self.lastfilename = pickle.load(file)
                 file.close
             else:
                 self.lastfilename = os.path.join(os.getcwd(),"stacks.dat")
                 self.writeConfig()
         if os.path.isfile(self.lastfilename + ".inprogress"):
             if os.path.isfile(self.lastfilename):
                 os.remove(self.lastfilename + ".inprogress")
             else:
                 os.rename(self.lastfilename + ".inprogress",
                           self.lastfilename)
         if os.path.isfile(self.lastfilename):
            try:
                file = open(self.lastfilename,"rb")
                if self.dataVersionNumber is not pickle.load(file):
                    messagebox.showwarning(
                        "Database Version Warning",
                        "Version mismatch! Discarding data read...")
                    return False
                self.goalTaskList = pickle.load(file)
                self.textAreaText = pickle.load(file).strip()
                file.close()
            except:
                messagebox.showwarning(
                    "Error",
                    "Error loading most recent database!")
                return False
            for goalStack in self.goalTaskList:
                goalStack.jumpToTop()
            return True
         else:
            messagebox.showwarning(
                "File Error",
                "Failed to load last database. "
                "Making new one there if possible...\n\n"
                "Location: " + self.lastfilename)
            return False

    def getGoalTaskList(self):
        return self.goalTaskList

    def getTextAreaText(self):
        return self.textAreaText
    
