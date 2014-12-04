*	Test program for Multiplication


	LDAA	VALUE1
	STAR	D
	LDAA	VALUE2
	MULT
	STAA OUT	*Low byte of OUT contains high byte of mult
	LDAD
	STAA OUT+1

LOOP:
	CLRC
	BCCA LOOP	*Infinite loop

OUT:	ds.b	2
VALUE1: dc.b	9
VALUE2: dc.b	7
