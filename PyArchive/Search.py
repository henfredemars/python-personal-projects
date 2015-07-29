#!/usr/bin/python3
# Tool to help searching the database

import argparse
import sqlite3
import re

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
regexs = []
try:
  while True:
    regexs.append(re.compile(input('Email regex {} [CTRL-D]: '.format(len(regexs)))))
except EOFError:
  print()

#src
query = 'select raw from email where ('
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

#trim
if query[-1]=='(':
  query = query[:-2]
  query += ';'
else:
  query += ');'
if query[-3:]=='and':
  query = query[:-4]
  query += ';'
if query[-4:-1]=='and':
  query = query[0:-4]
  query += ';'
if query[-6:-1]=='where':
  query = query[0:-6]
  query += ';'

print(query)
reqMatchCount = len(regexs)
for row in conn.execute(query):
  raw = row[0]
  matchCount = 0
  for regex in regexs:
    if regex.search(raw):
      matchCount += 1
      if matchCount==reqMatchCount:
        if len(raw)>14001:
          print(raw[0:14000])
        else:
          print(raw)


conn.close()

