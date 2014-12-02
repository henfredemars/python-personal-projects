#A simple AI chatbot, to be expanded upon

import random, os, sys
from Snapshot import Snapshot
from Database import Database
from time import sleep

class ChatBot:

    def __init__(self):
        self.intros = {"Hello.","Hi!","Hey.","What's up?",
                       "Nice to see you.","Greetings.","...",
                       "Get on with it.","I haven't got all day.",
                       "*Sigh*","What a life..."}
        self.database = Database()
        self.database.readDatabase()
        self.exits = {"Bye.","Goodbye.","Good bye.","Have a nice day.",
                      "See you.","See you again soon.",
                      "Nice talking with you."}
##        self.setExit(self.shutdown)
##
##    def setExit(self,f):
##        if os.name == "nt":
##            try:
##                import win32api
##            except ImportError:
##                pass
##            else:
##                win32api.SetConsoleCtrlHandler(f,True)              
##        else: #Assume unix-like
##            import signal
##            signal.signal(signal.SIGTERM,f)
            
    def shutdown(self,frame=None):
        res = random.sample(self.exits,1)
        print(res[0])
        self.database.writeDatabase()
        input()
        
    def run(self):
        print("Running ChatBot...\n")
        res = random.sample(self.intros,1)
        res = res[0]
        lines = []
        lines.append(res)
        try: 
            while True:
                sleep(0.6)
                userResponse = input("ChatBot: " + res + '\nYou: ')
                lines.append(userResponse)
                if len(lines) is 4: #Must be even
                    ss = Snapshot()
                    [ss.append(l) for l in lines]
                    self.database.addSnapshot(ss)
                    lines = lines[2:] #Chop off oldest exchange
                res = self.database.getFinale(userResponse)                        
                lines.append(res)
        except (KeyboardInterrupt, EOFError):
            try:
                sleep(2) #Get remaining interrupts
            except:
                pass
            res = random.sample(self.exits,1)
            print(res[0])
            self.database.writeDatabase()
        

if __name__=="__main__":
    bot = ChatBot()
    bot.run()
    input("Press ENTER to continue...")

