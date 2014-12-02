#Main

import tkinter as tk
import threading
from os.path import basename as basename
from time import sleep
from GoalStack import GoalStack
from Database import Database
from Task import Task

class Get2It:

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.resizable(0,0)
        self.version = "0.06"
        self.goalsFrame = tk.Frame(self.root)
        self.goalStackList = [] #List of Stacks
        self.oldframes = [] #Frames to be destroyed
        self.textAreaText = ""
        self.sampleGoalStack = GoalStack() #Sample
        self.sampleGoalStack.push(Task("Sample Task","Notes"))
        self.goalStackList.append(self.sampleGoalStack)
        self.goalsFrame.grid(row=0,column=0)
        self.database = Database()
        self.readDatabase()
        self.root.title("Get2It! Task Manager Alpha")
        self.collectorLock = threading.Lock()
        self.renderMenu()
        self.renderGoals()
        self.renderHelpfulText()
        self.renderTail()
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.shuttingDown = False
        self.launchAutosaveThread()
        self.root.after(60000,self.collect)
        self.root.deiconify()

    def mainloop(self):
        self.root.mainloop()

    def shutdown(self):
        self.shuttingDown = True
        self.writeDatabase()
        self.root.destroy()

    def renderMenu(self):
        menu = tk.Menu(self.root)
        menu.add_command(label="Open",command=self.doOpenMenu)
        menu.add_command(label="New",command=self.doNewMenu)
        menu.add_separator()
        menu.add_command(label=":")
        menu.add_command(label="Database: " +
                         self.database.getLastFilename())
        self.root.config(menu=menu)

    def doNewMenu(self):
        self.writeDatabase() #Save current
        self.database.saveDatabaseByUser() #Get new name
        for i in range(0,len(self.goalStackList)):
            del self.goalStackList[i]
        self.goalStackList.append(self.sampleGoalStack)
        self.renderMenu()
        self.renderGoals()
        self.writeDatabase()

    def doOpenMenu(self):
        self.writeDatabase()
        self.database.getDatabaseNameFromUser()
        self.readDatabase()
        self.renderMenu()
        self.renderGoals()

    def launchAutosaveThread(self):
        self.autoSaveThread = threading.Thread(target=self.autoSaveTarget)
        self.autoSaveThread.start()

    def autoSaveTarget(self):
        #THREAD METHOD ONLY
        counter = 0
        while not self.shuttingDown:
            counter += 1
            if counter is 60: #Every 30secs
                self.writeDatabase()
                counter = 0
            sleep(0.5)

    def centerWindow(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = self.root.winfo_rootx() + 20
        y = self.root.winfo_rooty() + 20
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def writeDatabase(self):
        self.database.writeDatabase(self.goalStackList,self.textAreaObj)

    def readDatabase(self):
        if (self.database.readDatabase()):
            self.goalStackList = self.database.getGoalTaskList()
            self.textAreaText = self.database.getTextAreaText()

    def doAbout(self):
        tk.messagebox.showinfo(title="Information",
            message="This program embodies a novel approach to task "
                "management! Instead of a simple task list, we "
                "model each goal as being a human call stack of "
                "subtasks to be performed.\n\nPlace your root goals "
                "in first, and then if the task at the top of the "
                "stack seems like too much, break it into two, and "
                "push the remainder onto the stack.\n\n"
                "The purpose of this application is to remember "
                "everything about where you are in your big projects, "
                "so you don't have to!")
            
    def doForward(self,goalstacknumber):
        goalStack = self.goalStackList[goalstacknumber]
        if goalStack.lookForward():
            self.renderGoals()

    def collect(self):
        #Clean up old frames
        self.collectorLock.acquire()
        for crap in self.oldframes:
            crap.destroy()
        self.collectorLock.release()

    def doBackward(self,goalstacknumber):
        goalStack = self.goalStackList[goalstacknumber]
        if goalStack.lookBackward():
            self.renderGoals()

    def doDown(self,goalstacknumber):
        goalStack = self.goalStackList[goalstacknumber]
        if goalstacknumber < len(self.goalStackList)-1:
            temp = self.goalStackList[goalstacknumber+1]
            self.goalStackList[goalstacknumber+1] = (
                self.goalStackList[goalstacknumber])
            self.goalStackList[goalstacknumber] = temp
            self.renderGoals()

    def doUp(self,goalstacknumber):
        goalStack = self.goalStackList[goalstacknumber]
        if goalstacknumber > 0:
            temp = self.goalStackList[goalstacknumber-1]
            self.goalStackList[goalstacknumber-1] = (
                self.goalStackList[goalstacknumber])
            self.goalStackList[goalstacknumber] = temp
            self.renderGoals()

    def doNewTask(self):
        localroot = tk.Toplevel(self.root)
        localroot.title("New Task")
        localroot.focus_set()
        tk.Label(localroot,text="Task:",width=20).grid(row=0,column=0)
        tk.Label(localroot,text="Note:",width=20).grid(row=1,column=0)
        taskName = tk.Entry(localroot)
        taskName.grid(row=0,column=1,sticky='ew')
        taskNote = tk.Entry(localroot)
        taskNote.grid(row=1,column=1,sticky='ew')
        okayButton = tk.Button(localroot,text="Create!",
            command=lambda:self.acceptNewTask(taskName,taskNote,
                                      localroot))
        okayButton.grid(row=3,column=0,sticky='ew')
        cancelButton = tk.Button(localroot,text="Cancel",
                                 command=lambda:localroot.destroy())
        cancelButton.grid(row=3,column=1,sticky='ew')
        self.centerWindow(localroot)
        localroot.resizable(0,0)

    def acceptNewTask(self,taskName,taskNote,localroot):
        if taskName.get():
            task = Task(taskName.get(),taskNote.get())
            goalStack = GoalStack()
            goalStack.push(task)
            self.goalStackList.append(goalStack)
            self.renderGoals()
        localroot.destroy()

    def doPop(self,goalstacknumber):
        localroot = tk.Toplevel(self.root)
        localroot.title("Pop")
        localroot.focus_set()
        l=tk.Label(localroot,text="Are you sure you want to pop the stack?",
                   height=2)
        l.grid(row=0,column=0,columnspan=2)
        okayButton = tk.Button(localroot,text="Accept",
            command=lambda:self.acceptPop(goalstacknumber,localroot))
        okayButton.grid(row=1,column=0,sticky='ew')
        cancelButton = tk.Button(localroot,text="No wait!",
            command=lambda:localroot.destroy())
        cancelButton.grid(row=1,column=1,sticky='ew')
        self.centerWindow(localroot)
        localroot.resizable(0,0)

    def doEdit(self,goalstacknumber):
        localroot = tk.Toplevel(self.root)
        localroot.title("Edit Task")
        localroot.focus_set()
        tk.Label(localroot,text="Task:",width=20).grid(row=0,column=0)
        tk.Label(localroot,text="Note:",width=20).grid(row=1,column=0)
        taskName = tk.Entry(localroot,width=40)
        taskName.grid(row=0,column=1,sticky='ew')
        taskNote = tk.Entry(localroot,width=40)
        taskNote.grid(row=1,column=1,sticky='ew')
        goalStack = self.goalStackList[goalstacknumber]
        task = goalStack.getTask()
        taskName.insert(0,task.name)
        taskNote.insert(0,task.note)
        okayButton = tk.Button(localroot,text="Accept",
            command=lambda:self.acceptEdit(goalstacknumber,taskName,taskNote,
                                        localroot))
        okayButton.grid(row=3,column=0,sticky='ew')
        cancelButton = tk.Button(localroot,text="Cancel",
                                 command=lambda:localroot.destroy())
        cancelButton.grid(row=3,column=1,sticky='ew')
        self.centerWindow(localroot)
        localroot.resizable(0,0)

    def acceptEdit(self,goalstacknumber,taskName,taskNote,localroot):
        goalStack = self.goalStackList[goalstacknumber]
        task = goalStack.getTask()
        if taskName.get():
            task.name = taskName.get().strip()
            task.note = taskNote.get().strip()
        localroot.destroy()
        self.renderGoals()
        
    def acceptPop(self,goalstacknumber,localroot):
        goalStack = self.goalStackList[goalstacknumber]
        if goalStack.size is 0 or goalStack.size is 1:
            del self.goalStackList[goalstacknumber]
        else:
            goalStack.pop()
        self.renderGoals()
        self.collect()
        localroot.destroy()

    def doPush(self,goalstacknumber):
        localroot = tk.Toplevel(self.root)
        localroot.title("Push")
        localroot.focus_set()
        tk.Label(localroot,text="Task:",width=20).grid(row=0,column=0)
        tk.Label(localroot,text="Note:",width=20).grid(row=1,column=0)
        taskName = tk.Entry(localroot,width=40)
        taskName.grid(row=0,column=1,sticky='ew')
        taskNote = tk.Entry(localroot,width=40)
        taskNote.grid(row=1,column=1,sticky='ew')
        okayButton = tk.Button(localroot,text="Accept",
            command=lambda:self.acceptPush(goalstacknumber,taskName,taskNote,
                                      localroot))
        okayButton.grid(row=3,column=0,sticky='ew')
        cancelButton = tk.Button(localroot,text="Cancel",
                                 command=lambda:localroot.destroy())
        cancelButton.grid(row=3,column=1,sticky='ew')
        self.centerWindow(localroot)
        localroot.resizable(0,0)
        
    def acceptPush(self,goalstacknumber,taskName,taskNote,localroot):
        if taskName.get():
            goalStack = self.goalStackList[goalstacknumber]
            goalStack.push(Task(taskName.get(),
                taskNote.get()))
        localroot.destroy()
        self.renderGoals()
        
    def renderTail(self):
        frame = tk.Frame(self.root,height=150,width=250)
        frame.grid(row=2,column=0)
        tk.Button(frame,text="Create New Root Goal",width=27,height=2,
                  command=self.doNewTask).grid(row=0,column=0)
        tk.Button(frame,text="About",command=self.doAbout).grid(
                  row=0,column=1,sticky='ns')
        tk.Frame(frame,width=295).grid(row=0,column=2)
        tk.Label(frame,text="Version " + str(self.version) +
                  " by henfredemars et. al.",
                  font=("Helvetica", 10, 'italic')).grid(
                  row=0,column=2,sticky='ns')

    def renderHelpfulText(self):
        frame = tk.Frame(self.root,height=16,width=10)
        S = tk.Scrollbar(frame)
        S.pack(side='right',fill='y')
        tk.Label(frame,text="--Helpful notes area [autosave: enabled]--").pack()
        self.textAreaObj = tk.Text(frame,height=8,width=73,maxundo=12,
                                   undo=True)
        self.textAreaObj.insert(0.0,self.textAreaText)
        self.textAreaObj.pack(side='bottom')
        S.config(command=self.textAreaObj.yview)
        self.textAreaObj.config(yscrollcommand=S.set)
        frame.grid(row=1,column=0)

    def renderGoals(self):
        self.oldframes.append(self.goalsFrame)
        #Create new goals frame
        self.goalsFrame = tk.Frame(self.root)
        goalStackCount = -1
        numRows = 0
        for goalStack in self.goalStackList:
            goalStackCount += 1
            frame = tk.Frame(self.goalsFrame,bd=2,relief='ridge')
            frame.grid(row=numRows)
            task = goalStack.getTask()
            tk.Label(frame,text=task.name,width=18,font=("Purisa",12),
                     wraplen=170).pack(side='left')
            tk.Frame(frame,bd=5,width=2,height=10,relief='sunken'
                     ).pack(side='left',fill='y')
            tk.Label(frame,text=task.note,width=26,wraplen=180).pack(
                side='left')
            backCarrot = "<" + str(goalStack.getBackwardMoves())
            tk.Button(frame,text=backCarrot,font=("Purisa",16),
                command=lambda goalStackCount=goalStackCount:self.doBackward(
                goalStackCount)).pack(side='left',fill='y')
            microframe = tk.Frame(frame)
            microframe.pack(side='left',fill='y')
            tk.Button(microframe,text="Up",
                command=lambda goalStackCount=goalStackCount:self.doUp(
                goalStackCount)).pack(side='top',fill='y',expand=1)
            tk.Button(microframe,text="Dn",
                command=lambda goalStackCount=goalStackCount:self.doDown(
                goalStackCount)).pack(side='bottom',fill='y',expand=1)
            forwardCarrot = str(goalStack.getForwardMoves()) + ">"
            tk.Button(frame,text=forwardCarrot,font=("Purisa",16),
                command=lambda goalStackCount=goalStackCount:self.doForward(
                goalStackCount)).pack(side='left',fill='y')
            tk.Button(frame,text="Edit",width=5,
                command=lambda goalStackCount=goalStackCount:self.doEdit(
                    goalStackCount)).pack(side='left',fill='y')
            tk.Button(frame,text="Push",width=5,
                command=lambda goalStackCount=goalStackCount:self.doPush(
                    goalStackCount)).pack(side='left',fill='y')
            tk.Button(frame,text="Pop",width=5,
                command=lambda goalStackCount=goalStackCount:self.doPop(
                    goalStackCount)).pack(side='left',fill='y')
            numRows += 1
        #Draw new frame on top of the old one
        self.goalsFrame.grid(row=0,column=0)
        self.root.update()

if __name__=="__main__":
    app = Get2It()
    app.mainloop()
