#Main

import tkinter as tk
import tkinter.messagebox
import threading
from time import sleep
import socket

class ChatterBox:

    def __init__(self):
        self.port = 51540
        self.root = tk.Tk()
        self.q = None
        self.root.geometry("460x250")
        self.root.title("ChatterBox! Messenger")
        self.RemoteCallsign = "Remote"
        self.MyCallsign = "Me"
        self.render()
        self.historylock = threading.Lock()
        self.sendinglock = threading.Lock()
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.shuttingdown = False
        self.killserver = False
        self.connected = False
        self.launchServer()
        self.historyboxqueue = []
        self.typingStatusToSet = "Waiting for connect..."
        self.root.after(200,self.updateHistory) #Evil polling, but tk is not t-safe by def.
        self.root.after(600,self.updateNotifyTyping)
        self.root.after(150,self.updateTyping)
        self.root.after(100,self.cleanEmptySend)
        self.oldText = ""

    def launchServer(self):
        self.serverThread = threading.Thread(target=self.server)
        self.serverThread.start()

    def launchClient(self):
        self.clientThread = threading.Thread(target=self.client)
        self.clientThread.start()

    def centerWindow(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = self.root.winfo_rootx() + 20
        y = self.root.winfo_rooty() + 20
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def shutdown(self):
        self.shuttingdown = True
        if self.q:
            if self.connected:
                self.sendMessage("_DISCONNECT")
                self.connected = False
            sleep(1.4) #Wait for Disconnect
            self.q.close()
        self.root.destroy()

    def updateTyping(self):
        self.statusLabel.configure(text=self.typingStatusToSet)
        self.root.after(150,self.updateTyping)

    def updateNotifyTyping(self):
        curText = self.sendbox.get(0.0,tk.END).strip()
        if curText != self.oldText:
            self.sendMessage("_ISTYPING")
        elif curText:
            self.sendMessage("_ISENTERED")
        else:
            self.sendMessage("_NOTYPING")
        self.oldText = curText
        self.root.after(600,self.updateNotifyTyping)

    def updateHistory(self):
        self.historylock.acquire()
        self.historybox.config(state=tk.NORMAL)
        pos = self.scrollbar.get()[1]
        for item in self.historyboxqueue:
            self.historybox.insert(tk.END,item)
        if pos == 1:
            self.historybox.yview(tk.END)
        self.historyboxqueue = []
        self.historybox.config(state=tk.DISABLED)
        self.historylock.release()
        self.root.after(200,self.updateHistory)

    def submitToHistory(self,message):
        self.historylock.acquire()
        self.historyboxqueue.append(message + "\n")
        self.historylock.release()

    def sendMessage(self,message):
        self.sendinglock.acquire()
        message = bytes(message,"UTF-8")
        if self.connected:
            sentChars = 0
            while message:
                j = self.q.send(message)
                if j < 0:
                    self.sendinglock.release()
                    return False #Error
                sentChars += j
                message = message[j:]
            self.sendinglock.release()
            return True
        else:
            self.sendinglock.release()
            return False

    def server(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(('0.0.0.0',self.port))
        s.listen(1)
        s.setblocking(False)
        self.submitToHistory("Server thread is listening on port " +
                             str(self.port))
        while not self.shuttingdown and not self.killserver:
            try:
                q,v = s.accept()
            except:
                q = None
                sleep(2)
            if q:
                self.q = q
                self.submitToHistory("Got connection! " + str(v[0]))
                self.connected = True
                break
        if not self.shuttingdown and not self.killserver:
            self.sendMessage("This is ChatterBox server.")
            self.sendMessage("You are now free to move about the cabin.")
            self.launchClient()
        return

    def prepsetIsTyping(self):
        self.typingStatusToSet = "Remote is typing..." 

    def prepsetIsEntered(self):
        self.typingStatusToSet = "Remote has entered text."

    def prepsetNoTyping(self):
        self.typingStatusToSet = "No remote activity." 

    def client(self):
        self.submitToHistory("Client thread initialized.")
        while not self.shuttingdown:
            try:
                msg = self.q.recv(1024).decode('utf-8')
                if "_ISTYPING" in msg:
                    self.prepsetIsTyping()
                elif "_ISENTERED" in msg:
                    self.prepsetIsEntered()
                elif "_NOTYPING" in msg:
                    self.prepsetNoTyping()
                elif "_DISCONNECT" in msg:
                    self.submitToHistory("Remote does proper disconnect")
                    self.connected = False
                msg = msg.replace("_ISTYPING",'',100)
                msg = msg.replace("_ISENTERED",'',100)
                msg = msg.replace("_NOTYPING",'',100)
                if "_NEWCALLSIGN" in msg:
                    old = self.RemoteCallsign
                    self.RemoteCallsign = msg.replace("_NEWCALLSIGN",'',100)
                    msg = (old + " changed their name to " +
                           self.RemoteCallsign)
                    leadingAlready = True
                else:
                    leadingAlready = False
                msg = msg.replace("_DISCONNECT",'',100)
                if msg and not leadingAlready:
                    self.submitToHistory(self.RemoteCallsign + ": " + msg)
                if msg and leadingAlready:
                    self.submitToHistory(msg)
                sleep(0.2)
            except:
                sleep(0.2)
            if not self.connected:
                self.launchServer()
                return

    def mainloop(self):
        self.root.mainloop()

    def doAbout(self):
        tk.messagebox.showinfo(title="About ChatterBox",
            message="ChatterBox is an alpha chat client written "
                "in pure Python, using tkinter for graphics.\n\n"
                "Press Connect to start a new connection, or "
                "wait until someone connects to you. \n\n"
                "You can also change your callsign as seen by "
                "your connected partner. \n\n"
                "This program was written by henfredemars to "
                "learn about networking and the unreliable nature "
                "of data transfer over the internet.")
        

    def doSetCallsign(self):
        localroot = tk.Toplevel(self.root)
        localroot.title("Set Callsign")
        localroot.focus_set()
        tk.Label(localroot,text="Callsign:").pack(side='left')
        e = tk.Entry(localroot)
        e.pack(side='left')
        okayButton = tk.Button(localroot,text="Configure",
                               command=lambda:self.acceptCallsign(
                                   localroot,e.get()))
        okayButton.pack(side='left')
        self.centerWindow(localroot)

    def acceptCallsign(self,localroot,text):
        if text:
            self.MyCallsign = text
        self.submitToHistory("I changed my name to " + text)
        self.sendMessage("_NEWCALLSIGN" + text)
        localroot.destroy()

    def doConnect(self):
        localroot = tk.Toplevel(self.root)
        localroot.title("Connect")
        localroot.focus_set()
        tk.Label(localroot,text="IP Address:Port").pack(side='left')
        e = tk.Entry(localroot)
        e.pack(side='left')
        okayButton = tk.Button(localroot,text="Configure",
                               command=lambda:self.acceptConnect(localroot,
                                                                e.get()))
        okayButton.pack(side='left')
        self.centerWindow(localroot)

    def acceptConnect(self,localroot,addrstring):
        self.submitToHistory("Configured for address " + addrstring)
        localroot.destroy()
        f = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            tl = addrstring.split(":")
            f.connect((tl[0],int(tl[1])))
            self.q = f
            self.connected = True
        except:
            self.submitToHistory("Could not connect to address.")
            return
        self.killserver = True
        self.submitToHistory("Server thread shutting down...")
        self.launchClient()

    def cleanEmptySend(self):
        if not self.sendbox.get(0.0,tk.END).strip():
            self.sendbox.delete(0.0,tk.END)
        self.root.after(100,self.cleanEmptySend)

    def doSend(self, event=None):
        text = self.sendbox.get(0.0,tk.END).strip()
        if not text:
            return
        self.sendbox.delete(0.0,tk.END)
        self.submitToHistory("Me: " + text)
        if not self.sendMessage(text):
            self.submitToHistory("Send failed.")
        
    def render(self):
        mainframe = tk.Frame(self.root)
        mainframe.pack(expand=True,fill='both')
        connect = tk.Button(mainframe,text="Connect",command=self.doConnect)
        connect.grid(row=0,column=3,sticky='nsew')
        newcall = tk.Button(mainframe,text="Set Callsign",
                            command=self.doSetCallsign)
        newcall.grid(row=1,column=3,sticky='nsew')
        about = tk.Button(mainframe,text="About",command=self.doAbout)
        about.grid(row=2,column=3,sticky='nsew')
        send = tk.Button(mainframe,text="Send!",command=self.doSend)
        send.grid(row=4,column=3,sticky='nsew')
        self.sendbox = tk.Text(mainframe,height=4,width=20)
        self.sendbox.bind('<Return>',self.doSend)
        self.sendbox.grid(row=4,column=0,columnspan=3,sticky='nsew')
        mainframe.columnconfigure(0,weight=1)
        for i in range(0,3):
            mainframe.rowconfigure(i,weight=1)
        minframe = tk.Frame(mainframe)
        self.historybox = tk.Text(minframe,height=6,width=20,state=tk.DISABLED)
        self.historybox.grid(row=0,column=0,sticky='nsew')
        minframe.rowconfigure(0,weight=1)
        minframe.columnconfigure(0,weight=1)
        self.scrollbar = tk.Scrollbar(minframe,
            command=self.historybox.yview)
        self.scrollbar.grid(row=0,column=1,sticky='ns')
        minframe.grid(row=0,column=0,columnspan=3,rowspan=3,
                        sticky='nsew')
        self.historybox.config(yscrollcommand=self.scrollbar.set)
        self.statusLabel = tk.Label(mainframe,text="Waiting for connect...")
        self.statusLabel.grid(row=3,columnspan=3,sticky='w')

if __name__=="__main__":
    print("I'm main!")
    app = ChatterBox()
    app.mainloop()
