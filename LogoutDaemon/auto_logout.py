#!/usr/bin/python3

#Automatically log out my idle shells sooner than the system terminates them by default
#  I would use the environment variable, but the sysadmin set it read-only :(
#  Sessions should time out faster to prevent users getting locked out when working on
#  projects on unreliable connections.
#
#This script has a few specializations to minimize system impact:
#  1) This script runs with good niceness and almost no CPU usage
#  2) This script (should) run only when I expect to be using the system
#  3) This script will never run for longer than one hour
#
#If user has more than one shell, choose the one with the least idle time

from time import time
from time import sleep
import subprocess, os, signal, sys

#Configuration
username = 'henfredemars'
maxIdleSeconds = 300
maxMonitorTime = 1*60*60
checkInterval = 10

#Extra protection to prevent accidental fork bomb (eek!)
__forkProtectorHasForked = False


def getMyShells():
  ps_out = subprocess.check_output(['ps','-u',username],universal_newlines=True).split('\n')
  shells = {}
  for i in range(len(ps_out)):
    line = ps_out[i].split()
    if not line: continue
    pname = line[3]
    pts = line[1]
    pid = line[0]
    if pname=="tcsh" or pname=="bash" or pname=="csh" or pname=="dash":
      if pts != '?':
        shells[pts] = pid
  return shells

def parseIdleString(idleString):
  if 'days' in idleString:
    return int(idleString.replace('days',''))*24*60*60
  elif 's' in idleString:
    return float(idleString.replace('s',''))
  elif 'm' in idleString:
    clock = idleString.replace('m','').split(':')
    return int(clock[0])*60*60+int(clock[1])*60
  else:
    clock = idleString.split(':')
    return int(clock[0])*60+int(clock[1])

def getIdleTimes():
  w_out = subprocess.check_output(['w','-u','-h',username],universal_newlines=True).split('\n')
  idleVals = {}
  for i in range(len(w_out)):
    line = w_out[i]
    if not line: continue
    line = line.split()
    idleVals[line[1]] = parseIdleString(line[4])
  return idleVals

def fork():
  global __forkProtectorHasForked
  if __forkProtectorHasForked:
    raise RuntimeError("Extra fork blocked!")
    quit() #Cant catch this
  print('Forking...')
  __forkProtectorHasForked = True
  sys.stdin.close()
  sys.stdout.close()
  if os.fork():
    os._exit(0) #Save cleanup for daemon
  os.setsid()
  if os.fork(): #Double fork
    os._exit(0)
  os.nice(5)
  signal.signal(signal.SIGHUP, signalHandler)
  os.chdir('/') #Dont prevent unmount

def signalHandler(sig,frame):
  pass

def main():
  fork() #Be careful!
  start_time = time()
  while time()-start_time < maxMonitorTime:
    shells = getMyShells()
    idleTimes = getIdleTimes()
    print(shells)
    print(idleTimes)
    for pts in shells:
      if idleTimes[pts] > maxIdleSeconds:
        os.system('kill -HUP ' + shells[pts])
    sleep(checkInterval)

if __name__=='__main__':
  main()

