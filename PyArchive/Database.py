# Database of archived email messages

import sqlite3
import email.utils as utils
from email.parser import Parser
import Config

class Database:

  def __init__(self):
    self.path = Config.database
    self.parser = Parser()
    self.conn = sqlite3.connect(self.path)
    self.create_tableb = ("create table if not exists email " + 
      "(mid text primary key,src text,dst text,ts integer not null)")
    self.create_tablet = ("create virtual table if not exists email_text using fts4 " +
      "(mid text primary key,raw text not null)")
    c = self.conn.cursor()
    c.execute(self.create_tableb)
    c.execute(self.create_tablet)
    self.conn.commit()
    c.close()

  def insert_emails(self,email_list):
    c = self.conn.cursor()
    for raw in email_list:
      m = self.parser.parsestr(raw,headersonly=True)
      mid = m['Message-ID'][1:-1]
      fr = utils.parseaddr(m['From'])[1]
      to = utils.parseaddr(m['To'])[1]
      ts = int(utils.mktime_tz(utils.parsedate_tz(m['Date'])))
      args = (mid,fr,to,ts,raw)      
      c.execute("insert into email values (?,?,?,?)", args[:-1])
      c.execute("insert into email_text values (?,?)", (args[0],args[-1]))
    self.conn.commit()
    c.close()

  def count_emails(self):
    c = self.conn.cursor()
    c.execute("select count(*) from email")
    count = c.fetchone()[0]
    return count

  def in_database(self,mid):
    c = self.conn.cursor()
    c.execute("select mid from email where mid=?", (mid,))
    if c.fetchone():
      c.close()
      return True
    c.close()
    return False

  def close(self):
    self.conn.commit()
    self.conn.close()
    
