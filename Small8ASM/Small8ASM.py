#!/usr/bin/python3

#A simple script to assemble Small8 ASM files into MIF binary files

#The Small8 CPU is a two-register multicycle microprocessor core consisting of an accumulator
#	and a data register as primary components. It contains an 8-bit data bus with 16-bit addressing.
#	This core for which this program assembles is designed to minimize the number
#	of discreet components to fit on small FPGAs. This simple processor does not
#	provide interrupts by design, as these would be added into the HDL and memory-mapped
#	for the desired application. The architecture is small and intuitive, but not
#	necessarily the most efficient in other aspects.

infile = "TestCase3.asm"
outfile = "TestCase3.mif"

INS_SET = {'LDAI':(2,'84'), #Name, length, opcode
	'LDAA':(3,'88'), #Load A Addr
	'LDAD':(1,'81'), #A<-D
	'STAA':(3,'F6'), #Store A Addr
	'STAR':(1,'F1'), #D<-A
	'ADCR':(1,'01'), #Add with carry, store in A
	'SBCR':(1,'11'), #Subtract with borrow
	'CMPR':(1,'91'), #Compare
	'ANDR':(1,'21'), #AND
	'ORR':(1,'31'), #OR
	'XORR':(1,'41'), #XOR
	'SLRL':(1,'51'), #Shift left logical
	'SRRL':(1,'61'), #Shift right logical
	'ROLC':(1,'52'), #Rotate left through carry
	'RORC':(1,'62'), #Rotate right through carry
	'BCCA':(3,'B0'), #Branch on NOT C (SREG=CVSZ,Carry,oVerflow,Sign,Zero)
	'BCSA':(3,'B1'), #Branch on C
	'BEQA':(3,'B2'), #Branch on Z
	'BMIA':(3,'B3'), #Branch on negative
	'BNEA':(3,'B4'), #Branch on NOT Z
	'BPLA':(3,'B5'), #Branch on positive
	'BVCA':(3,'B6'), #Branch on no overflow
	'BVSA':(3,'B7'), #Branch on overflow
	'DECA':(1,'FB'), #Decrement A
	'INCA':(1,'FA'), #Increment A
	'SETC':(1,'F8'), #Set carry flag
	'CLRC':(1,'F9'), #Clear carry flag
	'LDSI':(3,'89'), #Load the stack pointer (SP)
	'CALL':(3,'C8'), #Call into subroutine
	'RET':(1,'C0'), #Return from subroutine
	'LDXI':(3,'8A'), #Load index register
	'LDAA_with_index':(2,'BC'), #Load A with data pointed to by index register
	'STAA_with_index':(2,'EC'), #Store A to index (STAA v,X)
	'INCX':(1,'FC'), #Increment index register
	'DECX':(1,'FD'), #Decrement index register
        'EQU':(0,''), #Equate, not really an instruction
	'dc.b':(1,''), #Declare constant byte, not really an instruction
        'ds.b':(1,'')} #Declare storage byte, not really an instruction, lengh is dynamic

def isInstruction(s):
  return s in INS_SET.keys()

def loadFile():
  fd = open(infile,'r')
  lines = [line.strip() for line in fd]
  lines = [line.split() for line in lines if line] #No blank lines
  for i in range(len(lines)):
    line = lines[i]
    if isInstruction(line[0]):
      line.insert(0,None) #Always have slot for label
    line.insert(0,None) #Slot for address
  fd.close()
  for line in lines:
    while len(line) < 4:
      line.append(None)
  return lines

def stripComments(lines):
  for line in lines:
    for i in range(len(line)):
      if not line[i]: continue
      if line[i][0]=='*':
        del line[i:]
        break
  lines = [line for line in lines if line and not (len(line)==1 and line[0] is None)]
  for line in lines:
    while len(line) < 4:
      line.append(None)
  return lines

#Old,new,lines
def replaceLabels(nextLabel,label,lines):
  for i in range(len(lines)):
    for j in range(4):
      line = lines[i]
      if j<len(line):
        part = line[j]
        if part==nextLabel:
          line[j]=label
  return lines

def handleEquates(lines):
  i = 0
  while i<len(lines):
    line = lines[i]
    if line[2]=="EQU":
      lines = replaceLabels(line[1],line[3],lines)
      del lines[i]
    else:
      i += 1
  return lines

def resolveDuplicateLabels(lines):
  i = 0
  line = lines[i]
  nextLine = lines[i+1]
  label = line[1]
  nextLabel = nextLine[1]
  nextIns = nextLine[2]
  while i<len(lines)-1:
    while label and nextLabel and not nextIns:
      replaceLabels(nextLabel,label,lines)
      del lines[i]
      line = lines[i]
      nextLine = lines[i+1]
      label = line[1]
      nextLabel = nextLine[1]
      nextIns = nextLine[2]
    i += 1
    if i>=len(lines)-1: return lines
    line = lines[i]
    nextLine = lines[i+1]
    label = line[1]
    nextLabel = nextLine[1]
    nextIns = nextLine[2]
  return lines

def alignLabels(lines):
  i = 0
  while i < len(lines)-1:
    line = lines[i]
    iIsNext = False
    if line[1] and not line[2]:
      lines[i+1][1]=line[1]
      del lines[i]
      iIsNext = True
    if not iIsNext:
      i += 1
  return lines

def assignAddresses(lines):
  counter = 0
  for line in lines:
    line[0] = '$' + hex(counter)[2:].zfill(4)
    counter += INS_SET[line[2]][0]
    if line[2]=='ds.b':
      counter += int(line[3])-1
    if line[1]:
      lines = replaceLabels(line[1][:-1],line[0],lines)
    del line[1] #Label information no longer needed
  for line in lines:
    if line[2]=='D' or line[2] is None:
      del line[2]
  return lines

def handleDuplicateInsrNames(lines):
  for line in lines:
    if line[3] is None: continue
    if ',' in line[3]:
      if line[2]=='LDAA':
        line[2]='LDAA_with_index'
        line[3]=line[3].split(',')[0]
      elif line[2]=='STAA':
        line[2]='STAA_with_index'
        line[3]=line[3].split(',')[0]
      else:
        raise RuntimeError('Unexpected comma')
  return lines

def convertToBinary(lines):
  binaryString = []
  for line in lines:
    binaryOp = INS_SET[line[1]][1] #Assuming addresses resolved
    try:
      argument = line[2]
    except IndexError:
      argument = ''
    if len(argument)>0 and argument[0]=='$':
      argument = argument[1:]
    elif argument=='':
      pass
    else:
      argument = hex(int(argument))[2:].zfill(2)
    if len(argument)==4:
      argument = argument[2:] + argument[:2]
    binaryString.append(binaryOp + argument)
  return ''.join(binaryString)

def writeMif(binaryString):
  binaryChunks = [binaryString[i:i+2] for i in range(0,len(binaryString),2)]
  fileString = []
  header = "Depth = 4096;\nWidth = 8;\nAddress_radix = hex;\nData_radix = hex;\nContent\n  Begin\n"
  footer = "End;"
  fileString.append(header)
  counter = 0
  for chunk in binaryChunks:
    fileString.append(hex(counter)[2:].zfill(4) + " : " + chunk + '\n')
    counter += 1
  fileString.append(footer)
  fd = open(outfile,'w')
  fd.write(''.join(fileString))
  fd.close()

def main():
  lines = loadFile()
  lines = stripComments(lines)
  lines = handleEquates(lines)
  lines = resolveDuplicateLabels(lines)
  lines = alignLabels(lines)
  lines = handleDuplicateInsrNames(lines)
  lines = assignAddresses(lines)
  binaryString = convertToBinary(lines)
  writeMif(binaryString)

if __name__=='__main__':
  print("I'm main!")
  main()
  print("Processing completed.")
