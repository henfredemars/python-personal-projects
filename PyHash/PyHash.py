#!/usr/bin/python3

#Program to watch the contents of a directory for changes

import hashlib
import pickle
import os

rootPath = """C:\Program Files\WatchDirectory"""

def hash_file(fname):
  fd = open(fname,'rb')
  md5 = hashlib.md5()
  while True:
    d = f.read(65536)
    if not d: break
    md5.update(d)
  fd.close()
  return md5.hexdigest()

def getFiles(rootPath):
  for dirPath, dirNames, fileNames in os.walk(rootPath):
    for fileName in fileNames:
      yeild os.path.join(dirPath, fileName)

def saveMD5s(hashes):
  fd = open("hashes.dat",'wb')
  pickle.dump(hashes,fd)
  fd.close()

def hash_dir(root):
  hashes = {}
  for file in getFiles(rootPath):
    hashes[file] = hash_file(file)
    print(file + ' ' + hashes[file])
  return hashes

def loadMD5s():
  try:
    fd = open("hashes.dat",'rb')
  except IOError:
    return None
  else:
    hashes = pickle.load(fd)
    fd.close()
    return hashes

def main():
  print("Welcome! Scanning the rootPath and computing hashes...")
  hashes = hash_dir(rootPath)
  print("Looking for changes...")
  oldHashes = loadMD5s()
  if not oldHashes:
    print("No hash data file found: Nothing to compare!")
  else:
    if hashes.keys() != oldHashes.keys():
      print("A file has been added or a file is missing!")
      for file in set(hashes.keys()).difference(set(oldHashes.keys())):
        print("Inconsistency: " + file)
    for file in hashes.keys():
      try:
        if hashes[file]!=oldHashes[file]:
          print(file + " was changed! {}->{}".format(hashes[file],oldHashes[file]))
      except IndexError:
        pass
  saveMD5s(hashes)
  print("Done!")

