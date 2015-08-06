#!/usr/bin/python3
# Tool to help searching the database

import argparse 
import sqlite3

# Arguments
parser = argparse.ArgumentParser(description='Interactive SQLite3 Search Tool')
parser.add_argument('fname',action='store',nargs=1,help='Database file',
  metavar='FILE')
args = vars(parser.parse_args())

conn = sqlite3.connect(args['fname'][0])
src = input('List of allowed src: ').split()
forbidden_src = input('List of forbidden src: ').split()
dst = input('List of allowed dst: ').split()
forbidden_dst = input('List of forbidden dst: ').split()
search_term = input('Search string: ')

#src
query = 'select raw from email inner join email_text on email.mid=email_text.mid where ('
for item in src:
  query += "src='"+item+"' or "
if len(src):
  query = query[0:-4]
  query += ") and ("
for item in forbidden_src:
  query += "not src='"+item+"' and "
if len(forbidden_src):
  query = query[0:-5]
  query += ") and ("

#dst
for item in dst:
  query += "dst='"+item+"' or "
if len(dst):
  query = query[0:-3]
  query += ") and ("
for item in forbidden_dst:
  query += "not dst='"+item+"' and "
if len(forbidden_dst):
  query = query[0:-5]
  query += ") and ("

#match
query += "raw match '" + search_term + "')"

print(query)
for item in conn.execute(query):
  print(item)

conn.close()
