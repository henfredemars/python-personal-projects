*	Test program for calling subroutine


OUT0	EQU	$FFFE

	CALL BEGIN	* Call subroutine
	CLRC		* Clear carry flag
	BCCA LOOP	* Enter infinite loop

BEGIN:
	LDAA	VALUE1
	STAR	D
	LDAA	VALUE2
	ORR	D
	BEQA	LABEL * Not taken
	NOP	* No-op, not part of the standard
LABEL:
	ORR	D
	STAA	OUT0
        RET
LOOP:
	CLRC
	BCCA	LOOP

VALUE1:	dc.b	$23
VALUE2:	dc.b	$19

