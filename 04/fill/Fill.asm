// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// variable to keep track of screen status
@black
M = 0

// set SCREEN_END
@SCREEN
D = A
@8192
D = D + A
@SCREEN_END
M = D

// main LOOP
(LOOP)
@KBD
D = M // read KBD input
@clear_screen
D; JEQ // jump to clear screen if no kbd input

(blacken_screen) //else blacken screen
@black // is the screen already black?
D = M
@LOOP
D; JNE // yes, loop
// else no, set black to -1 and do the job
@black
M = -1
@color_screen
0; JMP

(clear_screen)
@black
D = M
@LOOP
D; JEQ // already clear
// else no, set black to 0 and do the job
@black
M = 0

(color_screen)
@SCREEN
D = A
@curr_address
M = D

(CLR_LOOP)
@black
D = M // color to write
@curr_address
// write color at mem pointed by curr_address
A = M
M = D
// increment curr
@curr_address
M = M + 1
// check end
@SCREEN_END
D = M
@curr_address
D = D - M // cmp SCREEN_END with current address
@CLR_LOOP
D; JNE // not done color loop

@LOOP
0; JMP