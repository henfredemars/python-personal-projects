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
	'LDAA_with_index':(1,'BC'), #Load A with data pointed to by index register
	'STAA_with_index':(1,'EC'), #Store A to index (STAA v,X)
	'INCX':(1,'FC'), #Increment index register
	'DECX':(1,'FD')} #Decrement index register

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
  return lines

def stripComments(lines):
  for line in lines:
    if line[-1][0]=='*':
    del line[-1]
  return lines

#Old,new,lines
def replaceLables(nextLabel,label,lines):
  for i in range(len(lines)):
    for j in range(4):
      line = lines[i]
      if j<len(line):
        part = line[j]
        if part==nextLabel:
          line[j]=label
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
    if i>=len(lines): return lines
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

def assignAddresses(lines):
  counter = 0
  for line in lines:
    line[0] = '$' + hex(counter)[2:].zfill(4)
    counter += INS_SET[line[1]][0]
    if line[1]:
      lines = replaceLabels(line[1],line[0],lines)
    del line[1] #Label information no longer needed

def handleDuplicateInsrNames(lines):
  for line in lines:
    if ',' in line[2]: #Assuming addresses have already been resolved
      if line[1]=='LDAA':
        line[1]='LDAA_with_index'
      elif line[1]=='STAA':
        line[1]='STAA_with_index'
      else"
        raise RuntimeError('Unexpected comma')

def convertToBinary(lines):
  for line in lines:
    binaryOp = INS_SET[line[1]] #Assuming addresses resolved
    argument = line[2]
    if argument[0]=='$':
      argument = argument[1:]
    else:
      argument = hex(argument)[2:].zfill(2)
    line[1] = binaryOp + argument
  binaryString = ''.join([''.join(line[1:]) for line in lines])
  return binaryString

def writeMif(binaryString):
  header = "
