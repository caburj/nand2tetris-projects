// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


(LOOP)
    @KBD
    D=M

    @R0
    M=0

    @NOFILL
    D;JEQ

    @FILL
    0;JMP

(NOFILL)
    @R0
    M=M+1
    D=M
    @KBD
    A=A-D
    M=0 // Fill register
    D=A
    @SCREEN
    D=D-A
    @NOFILL
    D;JNE

    @LOOP
    0;JMP

(FILL)
    @R0
    M=M+1
    D=M
    @KBD
    A=A-D
    M=-1 // Fill register
    D=A
    @SCREEN
    D=D-A
    @FILL
    D;JNE

    @LOOP
    0;JMP