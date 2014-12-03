#!/usr/bin/python3

#A simple script to assemble Small8 ASM files into MIF binary files

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
