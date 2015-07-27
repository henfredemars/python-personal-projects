#!/usr/bin/python3
# Maintain a database of email messages that were seen in an account folder

import imaplib
import time
import re
import Database
import Config

class PyArchive:

  def __init__(self):
    self.db = Database.Database()
    self.id_begin_re = re.compile("Message-ID:\s<", re.IGNORECASE)
    self.id_end_re = re.compile(">")
    self.logfile = open(Config.log,'a')
    self.log("PyArchive executing")

  def update(self):
    self.log("Updating archives...")
    M = imaplib.IMAP4_SSL(host=Config.server,port=Config.port)
    M.login(Config.email,Config.password)
    insert_count = 0
    dup_count = 0
    got_emails = []
    for folder in Config.folders:
      M.select(mailbox=folder,readonly=True)
      typ, data = M.search(None,"ALL")
      if typ=="NO":
        self.log("Server rejected our request to search {}.".format(folder))
      for num in data[0].split():
        _, data = M.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
        idstr = str(data[0][1], encoding="ASCII")
        start = self.id_begin_re.search(idstr)
        end = self.id_end_re.search(idstr)
        if not start or not end:
          self.log("Failed to locate the message-id field")
        else:
          start = start.end()
          end = end.start()
          idstr = idstr[start:end]
                    if not self.db.in_database(idstr):
            _, full_message = M.fetch(num, '(RFC822)')
            full_message = str(full_message[0][1],encoding='UTF-8',errors='replace')
            got_emails.append(full_message)
            insert_count += 1
            self.log("Got new message {}".format(idstr))
          else:
            dup_count += 1
    self.db.insert_emails(got_emails)
    M.close()
    M.logout()
    self.log("Got {} new messages, observed {} already in database.".format(insert_count,dup_count))
    self.log("{} emails in the database.".format(self.db.count_emails()))
    self.log("Update complete.")

  def log(self,msg):
    header = "PyArchive " + time.strftime("%m-%d-%Y %H:%M:%S") + ": "
    msg = header + msg
    print(msg)
    self.logfile.write(msg + "\n")

  def close(self):
    self.log("Shutting down...")
    self.logfile.close()
    self.db.close()

if __name__=="__main__":
  print("Initializing...")
  try:
    arch = PyArchive()
    arch.update()
    arch.close()
  except Exception as err:
    arch.log(err)
