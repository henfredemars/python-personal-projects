#!/usr/bin/python3

#A simple script to assemble Small8 ASM files into MIF binary files

#The Small8 CPU is a two-register multicycle microprocessor core consisting of an accumulator
#	and a data register as primary components. It contains an 8-bit data bus with 16-bit addressing.
#	This core for which this program assembles is designed to minimize the number
#	of discreet components to fit on small FPGAs. This simple processor does not
#	provide interrupts by design, as these would be added into the HDL and memory-mapped
#	for the desired application. The architecture is small and intuitive, but not
#	necessarily the most efficient in other aspects.

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
