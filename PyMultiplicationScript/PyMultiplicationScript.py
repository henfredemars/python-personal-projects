#!/usr/bin/python3
#Script to practice multiplication

#Parameters
upperDigitsMax = 2
lowerDigitsMax = 1
numProblems = 10
spacesFromLeft = 10

#Configurable strings
correctStrings = {
  "Correct!",
  "Nice work!",
  "Yeah!",
  "Yes, sir.",
  "Nice.",
  "The answer is correct.",
  "You are absolutely right!"
}

incorrectStrings = {
  "Incorrect!",
  "Nice try, but that is wrong.",
  "Nope.",
  "No.",
  "No, sir!",
  "Sorry, that's not correct.",
  "The answer is not correct."
}

nextStrings = {
  "Moving along...",
  "Next question.",
  "Next!",
  "But can you HANDLE THISS!!!?",
  "Time for the next question.",
  "Did you ever notice that it's just in the last place you look?",
  "Let's do this.",
  "And then..."
}

#Internal Use
numberCorrect = 0
numberAttempted = 0

from random import randint
from random import sample

def ask(x,y):
  global numberAttempted
  print("\nWhat is?:\n\n{})".format(numberCorrect+1))
  pos = spacesFromLeft - len(str(x))
  print((pos * ' ') + str(x))
  pos2 = -1 + spacesFromLeft - len(str(y))
  print('X' + (pos2 * ' ') + str(y))
  print('-'*spacesFromLeft*2)
  try:
    num = int(input(' ' * (spacesFromLeft - len(str(x*y)))).replace(',',''))
    print()
    return num
  except ValueError:
    print("Invalid answer format!")
    numberAttempted -= 1 #Don't count against bad formatting
    return None

def genUpper():
  result = ""
  for i in range(0,upperDigitsMax):
    result += str(randint(0,9))
  return int(result)

def genLower():
  result = ""
  for i in range(0,lowerDigitsMax):
    result += str(randint(0,9))
  return int(result)

def sayCorrect():
  s = sample(correctStrings,1)
  print(s[0])

def sayNext():
  s = sample(nextStrings,1)
  print(s[0])

def sayIncorrect():
  s = sample(incorrectStrings,1)
  print(s[0])

def checkAnswer(res,up,lo):
  global numberCorrect
  global numberAttempted
  numberAttempted += 1
  if res == up*lo:
    sayCorrect()
    numberCorrect += 1
    return True
  else:
    sayIncorrect()
    return False

def main():
  print("Let's do {} problems this session!".format(numProblems))
  for i in range(0,numProblems):
    up = genUpper()
    lo = genLower()
    res = ask(up,lo)
    while not checkAnswer(res,up,lo):
      res = ask(up,lo)
    if i != numProblems-1:
      sayNext()
    print("So far, you have answered {} correctly!".format(numberCorrect))
    print("{} attempted, {} incorrect attempts.".format(
            numberAttempted, numberAttempted-numberCorrect))

if __name__=='__main__':
  print("I'm main!")
  main()
