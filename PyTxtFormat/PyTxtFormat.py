#An SMS Formatting/Compression Tool

symbols = """,./;[]\-=`<>?:"{}|_+~!@#$%^&*()1234567890"""

import tkinter as tk
import tkinter.messagebox
import os, pickle

class PyTxtFormat:

    def __init__(self):
        self.inputField = None
        self.outField = None
        self.root = tk.Tk()
        self.root.title("PyTxtFormat: SMS Formatting/Compression Tool")
        self.root.geometry("600x325")
        self.render()
        self.root.bind_class("Text","<Control-a>",self.selectAll)
        self.charmax = 160
        self.database = Database()
        self.translations = self.database.read()
        self.root.after(300,self.updateCounts)
        self.textmodified = True

    def mainloop(self):
        self.root.mainloop()

    def selectAll(self,e):
        e.widget.tag_add("sel","0.0","end")

    def updateCounts(self):
        if not self.textmodified:
            self.root.after(300,self.updateCounts)
            return
        instr = self.inputField.get(0.0,tk.END)
        outstr = self.format(instr)
        self.characterCount.set("Output Character Count: {}".format(
            len(outstr.strip().replace("\n",""))))
        self.messageCount.set("Total Messages: 0")
        self.messageCount.set("Total Messages: {}".format(
            outstr.count("\n\n")))
        self.textmodified = False
        self.root.after(300,self.updateCounts)

    def render(self):
        mainframe = tk.Frame(self.root)
        mainframe.pack(expand=True,fill='both')
        mainframe.columnconfigure(index=0,weight=1)
        mainframe.rowconfigure(index=0,weight=1)
        mainframe.rowconfigure(index=2,weight=1)
             
        upperframe = tk.Frame(mainframe)
        upperframe.grid(row=0,column=0,sticky="nsew")
        upperframe.columnconfigure(index=0,weight=1)
        upperframe.rowconfigure(index=0,weight=1)
        inputField = tk.Text(upperframe,width=1,height=1)
        inputField.grid(row=0,column=0,sticky="nsew")
        inputField.config(maxundo=30,undo=True)
        self.inputField = inputField
        
        midframe = tk.Frame(mainframe)
        midframe.grid(row=1,column=0,sticky="nsew")
        midframe.columnconfigure(index=0,weight=1)
        midframe.columnconfigure(index=1,weight=3)
        midframe.columnconfigure(index=2,weight=1)
        midframe.rowconfigure(index=0,weight=1)
        settingsButton = tk.Button(midframe,text="Settings",
                                   command=self.doSettings)
        settingsButton.grid(row=0,column=0,sticky="nsew")
        processButton = tk.Button(midframe,text="<---------Process!--------->",
                                  command=self.doProcess,height=2)
        processButton.grid(row=0,column=1,sticky="nsew")
        aboutButton = tk.Button(midframe,text="About",
                                command=self.doAbout)
        aboutButton.grid(row=0,column=2,sticky="nsew")
        
        lowerframe = tk.Frame(mainframe)
        lowerframe.grid(row=2,column=0,sticky="nsew")
        lowerframe.columnconfigure(index=0,weight=1)
        lowerframe.rowconfigure(index=0,weight=1)
        outField = tk.Text(lowerframe,state=tk.DISABLED,width=1,height=1)
        outField.grid(row=0,column=0,sticky="nsew")
        self.outField = outField

        upperScrollBar = tk.Scrollbar(upperframe,command=inputField.yview)
        upperScrollBar.grid(row=0,column=1,sticky="ns")
        lowerScrollBar = tk.Scrollbar(lowerframe,command=outField.yview)
        lowerScrollBar.grid(row=0,column=1,sticky="ns")
        inputField.config(yscrollcommand=upperScrollBar.set)
        outField.config(yscrollcommand=lowerScrollBar.set)

        bottomframe = tk.Frame(mainframe)
        bottomframe.grid(row=3,column=0,sticky="nsew")
        self.characterCount = tk.StringVar()
        self.messageCount = tk.StringVar()
        self.characterCount.set("Output Character Count: 0")
        self.messageCount.set("Total Messages: 0")
        tk.Label(bottomframe,textvariable=self.messageCount).pack(side="left")
        tk.Label(bottomframe,textvariable=self.characterCount).pack(
            side="right")

        inputField.bind('<<Modified>>', self.setModified)

    def setModified(self,e):
        self.textmodified = True
        self.inputField.edit_modified(False)

    def doProcess(self):
        instr = self.inputField.get(0.0,tk.END)
        outstr = self.format(instr)
        self.outField.config(state=tk.NORMAL)
        self.outField.delete(0.0,tk.END)
        self.outField.insert(0.0,outstr)
        self.outField.config(state=tk.DISABLED)

    def doAbout(self):
        tk.messagebox.showinfo(title="About PyTxtFormat",message=
            "PyTxtFormat is a tool to help squish down English text into "
            "a form that's easy to read and effectively uses the limited "
            "space in an SMS message.\n\nThis program was created to "
            "help me save money when texting my foreign girlfriend over "
            "Skype. She doesn't have internet access, and I have a lot to "
            "say...\n\nMessages are squished and then divided at word "
            "bounds. You can specify word substitutions as well to replace "
            "long words with abbreviations automatically. The translation "
            "dictionary is written to a file upon modification.")

    def doSettings(self):
        localroot = tk.Toplevel(self.root)
        localroot.title("Settings")
        localroot.focus_set()
        frame1 = tk.Frame(localroot)
        frame1.grid(row=0,column=0,sticky="ew")
        tk.Label(frame1,text="Message Length: ").pack(side="left")
        e = tk.Entry(frame1,width=42)
        e.pack(side='left')
        e.insert(0,"160")
        configButton = tk.Button(frame1,text="Configure",command=lambda:
                               self.acceptSettingsLength(localroot,e.get()))
        configButton.pack(side='right')
        frame2 = tk.Frame(localroot)
        frame2.grid(row=1,column=0,sticky="ew")
        tk.Label(frame2,text="New Translation: ").pack(side="left")
        e2 = tk.Entry(frame2)
        e2.pack(side="left")
        tk.Label(frame2,text=":").pack(side="left")
        e3 = tk.Entry(frame2)
        e3.pack(side="left")
        configButton2 = tk.Button(frame2,text="Configure",command=lambda:
                                self.acceptTranslation(localroot,e2.get(),
                                                       e3.get()))
        configButton2.pack(side="right")
        frame3 = tk.Frame(localroot)
        frame3.grid(row=2,column=0,sticky="ew")
        tk.Label(frame3,text="Delete Translation By Key: ").pack(side="left")
        e4 = tk.Entry(frame3,width=34)
        e4.pack(side="left",expand=True,fill="x")
        configButton3 = tk.Button(frame3,text="Configure",command=lambda:
                                self.removeTranslation(localroot,e4.get()))
        configButton3.pack(side="right")

    def removeTranslation(self,localroot,text):
        if not text:
            return
        try:
            del self.translations[text]
        except KeyError:
            tk.messagebox.showinfo(title="KeyError",message=
                "No translation found.")
        localroot.destroy()

    def acceptTranslation(self,localroot,text1,text2):
        if not text1 or not text2 or "_" in text2:
            return
        self.translations[text1] = text2
        self.database.write(self.translations)
        tk.messagebox.showinfo(title="Information",message=
                "Translation added!")
        localroot.destroy()

    def acceptSettingsLength(self,localroot,text):
        try:
            val = int(text)
        except ValueError:
            tk.messagebox.showwarning(title="ValueError",message=
                "Error converting message length value to a number! "
                "Settings change aborted!")
            localroot.destroy()
            return
        self.charmax = val
        localroot.destroy()

    def format(self,instr):
        instr = ' '.join(instr.split()) #Remove dup whitespace
        replaced = [] #Strip symbols
        instr = list(instr)
        for i in range(0,len(instr)):
            if instr[i] in symbols:
                replaced.append(instr[i])
                instr[i] = "_"
        instr = ''.join(instr)
        stringsArray = instr.split()
        #Allow translations to take place, if any
        for i in range(0,len(stringsArray)):
            if "_" in stringsArray[i] and (stringsArray[i][-1] !='_' or
                                           stringsArray[i][0] == '_'):
                stringsArray[i] = self.translate(stringsArray[i])
                continue #Behave for smilies
            stringsArray[i] = self.translate(stringsArray[i])
            stringsArray[i] = stringsArray[i].capitalize()
        outstr = ' '.join(stringsArray)
        #Return symbols
        for i in range(0,len(replaced)):
            outstr = outstr.replace("_",replaced[i],1)
        #Limit to 160 characters
        outArrayStr = ""
        loopSafetyMax = 10000
        loopSafety = 0
        while len(outstr) and loopSafety < loopSafetyMax:
            loopSafety += 1
            outstr = outstr.split()
            charcount = 0
            outArray = []
            leftOvers = []
            trip = False
            for word in outstr:
                if len(word) + charcount <= self.charmax and not trip:
                    outArray.append(word)
                    charcount += len(word)
                else:
                    trip = True
                    leftOvers.append(word)
            outArrayStr += ''.join(outArray) + "\n\n"
            outstr = ' '.join(leftOvers)
        if loopSafety >= loopSafetyMax:
            tk.messagebox.showerror(title="Error",message=
                "Possible infinite loop detected. Aborting.")
            quit()
        return outArrayStr
    
    def translate(self,instr):
        #If you want to peform word substitutions, do it here
        try: 
            return self.translations[instr]
        except KeyError:
            return instr

class Database:

    def __init__(self,filename="translations.dat"):
        self.dataVersionNumber = 1
        self.filename = filename

    def read(self):
        if os.path.isfile(self.filename):
            fd = open(self.filename,"rb")
            if pickle.load(fd) != 1:
                tk.messagebox.showerror(title="Error",message=
                    "Database version incorrect!")
                quit()
            translations = pickle.load(fd)
            fd.close()
            return translations
        return {}

    def write(self,translations):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        fd = open(self.filename,"wb")
        pickle.dump(self.dataVersionNumber,fd)
        pickle.dump(translations,fd)
        fd.close()
        

if __name__=='__main__':
    print("I'm main!")
    app = PyTxtFormat()
    app.mainloop()
        
