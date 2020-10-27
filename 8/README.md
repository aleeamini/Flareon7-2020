# 8-ttt2  
This is special challenge which is use the new future of Windows 10, WSL. The WSL is an embedded Linux OS in the windows that lets you to run the Linux files in it. For more info read [this]( https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux)  
  
OK at first, I run the ```ttt2.exe``` file and it shows me an error message :``` CoCreateInstance failed```  
When I traced the exe file, I found out that the executable, does some checks about OS version. And I found out that, should use one the below version of Windows 10 version:   
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/winver.jpg)  

OK after googling the error message, I realized that, should enable the WSL feature. Read [here]( https://docs.microsoft.com/en-us/windows/wsl/install-win10)  
Now you can run the executable and see this is a tic-tac-toe game. I played it and found out that I can’t never ever win the game.  
Let’s do some analysis. When you open the file in the ```Resource Hacker``` you see an ELF file is included in the executable file. Extract it and open it in the ```IDAPro```, you see this is the game engine. The game has 2 section:  
1. The UI that runs in the Windows  
2. The engine that runs in the Linux at background  
Ok I thought, I must the winner, to get the flag. If you look at the engine's code, you see a branch which used for checking the winner:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/check_the_winner.png)  
The idea is to patch the file and change the ```X``` for ```O``` and vice versa. But how we can patch the file? It’s simple.  
The engine file is embedded in the main executable, so you can use a Hex-editor to find these instruction and patch them statically. For example ```3C 58```, compare the ```al``` with ``` 0x58 or X```. I search the ```3C58``` in the Hex Editor and change the ```0x58``` to ```0x4F or O```.  
 ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/swapxo.png)  
Now run the game and let the X to wins the game. Ok now we see a string like the flag. But it isn’t the correct flag.  
Let’s look at the function that generates the flag. At the ```0f27``` we see a ```xor``` instruction in a loop that iterates an array.  
And it xors the elements of the array with ```AL``` register.  
What is the ```AL```? OK we see a call that probably ```AL``` is the return value of this call. So we should debug it to find out the return value. But how we can debug it?  
When you run the WSL Linux(in this case I used the ubuntu). You can find the engine is running in the Linux. And we can attach the debugger to it and set a bp at this call and continue the game until the debugger breaks at this point.  
 ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/ps.png)  

I used the ```pwndbg``` for debugging in the Linux. Ok as you see in the picture, when the function is called, the eax changed to ```0x58``` that is the ```X```. So this function returns the character of the winner. So I patched this call and changed it with a ```Mov eax, 0x4F```.  
 ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/patchcall.png)  
Now the executable file is something like this:  
 ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/pathced.png)  
Now run the game and let the ```X``` wins the game and now we have the flag. The flag is a unusual one but this the rabbit’s hole and you may think this is not the correct flag and try for find it. But the correct flag is it.  
 ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/8/flag.png) 

