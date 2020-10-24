#3-wednesday

This is a score game and you must get a specific score at this game to shows you the flag.  
When i debuged it, i saw strings ```Score``` and ```HighScore``` in the screen of game. searched them in the memory of the file and find the address of them.  
![alt text]

I set some breakpoints in this function and traced the game,I found that the game checks some rules and increase the score or restart the game.  
In the game we have two types of block: M blocks and F blocks. we should pass from under the M blocks and jump from F blocks. so we can get one score.  
And at every success pass, the game checks the score with value ```0x128 or 256```.  
At the first i decided to change the increament value from 1 to 16 or a higher number. but nothing happend. Because the game has an Anti-Cheat function.  
The Anti-Cheat mechanisem check some values and not depends just on score value. and if we can get the 0x128 score with changing the increament function, it just shows us a  Winner windows, not the flag.  
After some checking the functions and static analysis in IDAPro, i found two intersting functions.: ```OnCollide()```.  
I set bp in these functions to find when they are called. and found that when the frog collides to blocks, these functions is called. one of is for M blocks and another for F.  
So i patched the game in a way that bypass the collides and continueing the game.  

##Patches:
collide1:(for M blocks) at address `0x43222a`: chnage the ```JNE``` to ```JMP``` to continue the game after collide to M blocks.  
collide1:(for F blocks) at address `0x432358`: chnage the ```JE``` to ```JMP``` to continue the game after collide to F blocks.  

after that i saved the file and ran it and let it to go until it reaches the 296 of score.  
And we have the flag:  
![alt text]
