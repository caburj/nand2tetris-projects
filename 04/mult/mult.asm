// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

// Set R2 to zero
@R2
M=0

// JUMP to end if R0 is zero
@R0
D=M
@END
D;JEQ

// Iterate if R0 is not zero,
// then jump to end if it becomes zero
(LOOP)
@R0
D=M
M=D-1

@R1
D=M

@R2
M=M+D

@R0
D=M

@LOOP
D;JNE

(END)
@END
0;JMP