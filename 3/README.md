# 3-Wednesday

This is a score game and you must get a specific score at this game so that it shows you the flag.  
After debugging the code, I saw that strings ```Score``` and ```High Score``` in the screen of game. Searched them in the memory of the file and find the address of them.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/3/find_hotspot.png)  

I set some breakpoints in this function and traced the game, I found that the game checks some rules and increase the score or restart the game.  
In the game we have two types of block: M blocks and F blocks. We should pass from under the M blocks and jump from F blocks. so we can get one score.  
And at every success pass, the game checks the score with value ```0x128 or 296```.  
At the first i decided to change the increment value from 1 to 16 or a higher number. but nothing happened. Because the game has an Anti-Cheat function.  
The Anti-Cheat mechanism checks some values and does not depend just on score value. And if we can get the 0x128 score by changing the increment function, it just shows us a  Winner window, not the flag.  
After some checking the functions and static analysis in IDAPro, I found two interesting functions. ```OnCollide()```.  
I set bp in these functions to find when they are called. And found that when the frog collides to blocks, these functions is called. One of is for M blocks and another for F.  
So I patched the game in a way that bypass the collides and continuing the game.  

## Patches:
collide1: (for M blocks) at address `0x43222a`: chnage the ```JNE``` to ```JMP``` to continue the game after collide to M blocks.  
collide1: (for F blocks) at address `0x432358`: chnage the ```JE``` to ```JMP``` to continue the game after collide to F blocks.  

After that I saved the file and ran it and let it to go until it reaches the 296 of score.  
And we have the flag:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/3/flag.png)  
