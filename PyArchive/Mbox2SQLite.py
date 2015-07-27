# Parse MBOX format into a SQLite3 Database

import mailbox
import sqlite3
import hashlib
import email.utils as utils

mb = mailbox.mbox('tmail.mbox')

conn = sqlite3.connect('all_mail.db')
conn.execute("create table if not exists email " + 
      "(mid text primary key,src text,dst text,ts " +
             "integer not null,raw text not null)")

discarded = 0
for m in mb:
    try:
        body = str(m)
        if 'X-Gmail-Labels: Chat' in body:
            continue # Exclude chats and junk
        else:
            mid = m['Message-Id'][1:-1]
        try:
            src = utils.parseaddr(m['From'])[1]
        except: #Not an email
            src = None
        try:
            dst = utils.parseaddr(m['To'])[1]
        except:
            dst = None
        ext_date = utils.parsedate_tz(m['Date'])
        ts = int(utils.mktime_tz(ext_date))
        conn.execute('insert into email values(?,?,?,?,?)',
                     (mid,src,dst,ts,body))
        print("Inserted {}".format(mid))
    except Exception as e:
        discarded += 1

conn.commit();
print("Discarded {} messages that did not parse".format(discarded))
input('Press ENTER to continue...')
