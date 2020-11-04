# break  
## First Section: Static Analysis  
This challenge is a very hard one. You have a Linux ELF file that uses many anti-debugging techniques that don’t let you debug and analyze it easily.  
The file is x86 ELF and when you run it, shows you a prompt to enter a password.  
OK, when you open it in the IDAPro, you see in the main function is a password check routine that checks the input buffer with the string ```sunsh1n3_4nd_r41nb0ws@flare-on.com```. But when you enter this string as a password, t shows you ```sorry, but 'sorry I stole your input :)```.  
So what happened there? You decide to debug it in the gdb. But when you open it in the gdb, you see that program exited.  
Ok continue analyzing the file statically and you see that the program uses an ```ini``` function that is interesting for us.  
The ```init``` function is used in the ELF files for does some initialization before the main function is run.  
When you see the init function you see it has a loop that in it, calculates an address, and calls it.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/1.png)  
Now we should find out what is the targets of this call. Ok because this part of the program is before the main, so we sure that the anti-debug protection isn’t enabled. To start the program in gdb and set a bp at the init function and debug it until this loop. If you see the function that is called in this loop you find out two functions. This is because the loop runs just 2 times.  
One of those functions is a function that seems doesn’t perform a special thing.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/2.png)    
Another function is an important function. When you search the address of this function in the IDAPro, you find out the function is a function that uses ```Fork()``` system call to create a child of the current process.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/3.png)       
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/4.png)    
After the fork, the child process starts its job. When you see the child functionality, you find out that this function uses some system calls of the Linux for detecting debugging and defeat from debugging.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/5-.png)  
### Tip: you could use IDA symbolic constant feature, to make easy your job. It could detect the Ptraces requests and flags and also the signals.
The most used function is ```PTRACE```, which is used to attach to the parent process and checks the state of it. the child process uses ```ATACH``` method of PTRACE, to attach to its parent and then control it. if you see more the child function, you find out that when it couldn’t attach to its parent, it finds out that another process, attaches to the parent. So it detects that a debugger comes in and then, terminate the parent process with signal 9.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/5.png)  
### TIP:A process can only be attached by another process at a time.  
The child process also monitors the system calls of its parent. when a parent wants to call a function, a signal is generated and the child finds out that the parent wants to call a system call. So the child will decide, how the parent continues its functionality. 
There are just some PTRACE tricks that malware use for anti-debugging and if you read the PTRACE documents, you could find the behavior of the child process.  
So the child is a watchdog of its parent. Also, it checks the functionality of the parent at the same time, such as system calls, which performs this with ```PTRACE_SYSEMU```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/6.png)    

There are some tricks that the child is using, which is important and I explain their: 
If you look at the child carefully, you see it uses another call to fork. This time it creates another child of itself.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/7.png)    
This time the second child is as the first child. But the child1 is watching the parent process, but the child2 watches its parent (the child1). This is due, you could attach the debugger to the child1 and debug it. But now you cannot do this. Because the child1 is watching with child2. The big picture of this program is like this picture:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/8.png)  
So with this scenario, we just could attach to the child2 and debug it. But no. there is another Ptrace call that the child1 uses to monitor the child2 :D. So, debugging is hard work and we cannot do it easily. We can do it if we patch some calls but the functionality of the program will corrupt.  
Another trick that the child1 is used is at the ```08049120```. The child1, uses the ```PTRACE_POKEDATA``` request, to change the value of an address in the parent. the address is ``` 8048CDB``` and the value that uses to write to this address is ``` 0B0F```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/9.png)  
If you see the ```8048CDB```, it is the address of the function that checks the ```Sunshine``` string with the input buffer in the main function. This call uses Ptrace to change the first 2 bytes of the ```check_sunshine``` function to ```0B0F```. So the beginning of the function will change from ```55 89``` to ```0B0F``` and the new value hasn’t any special meaning in the assembly.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/10.png)  

Another trick that child1 is using to detects debugging, is a check for 0xCC byte. You know when a debugger wants to set a breakpoint at an address, it writes a 0xCC at the beginning of that address (INT 3).  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/11.png)  
OK, now it’s time to talk about a clever trick that Child1 uses to fool the analyzer.  
At the address ``` 080491D7```, the child1 calls Ptrace with ```PTRACE_SYSEMU or 13``` request. This means that if the parent process calls a system call, it will throw an exception or signal, and the tracer(child1) will know that the tracee(parent), is calling a system call. So, if tracee (parent) calls a syscall, the child1 will notice and performs some actions. It gets the register’s values of the parent with ```PTRACE_GETREGS``` request. This request sends a free buffer and the ptrace fills it with the parent’s registers the buffer is a user_reg_struct data structure.  
```C
struct user_regs_struct
{
long int ebx;
long int ecx;
long int edx;
long int esi;
long int edi;
long int ebp;
long int eax;
long int xds;
long int xes;
long int xfs;
long int xgs;
long int orig_eax;
long int eip;
long int xcs;
long int eflags;
long int esp;
long int xss;
};
``` 
You know that in Linux’s syscalls, the number of the syscall, will put in EAX, so the child1 read RAX and xor it with ```DEADBEEF``` then multiple it by ```1337CAFE``` then, compare the result with some value. [Linux_Syscalls](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#x86-32_bit)  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/12.png)  
Every branch goes to a special function and if you look, there is a hooking system that changes the functionality of a syscall. For example, if the parent calls the ```execve``` syscall, the tracer will notice that the parent calls a syscall. It gets the syscall number that stored in EAX register. 0x0b is the syscall number of the ```execve``` in x86:  
```
0x0b XOR 0xDEADBEEF = 0xDEADBEE4  
0xDEADBEE4 * 0x1337CAFE= 10B76D10F7FF4E38 convert to int = 0xF7FF4E38
```  

Now if you look at the code of child1 you see that if the result is 0xF7FF4E38, it goes to address ```0x0804948B```.   
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/13.png)  
And you see that when the parent calls the execve, actually the real execve doesn’t run and the child just does some malloc and another function, and after that continue that program. There are other syscalls that the child bypasses them and performs another functionality.  
I wrote a code to generates these magic numbers of the syscalls:  
```C
int main()
{
    int i = 0;
    for (i = 0; i < 0x180; i++)
    {
        std::cout << std::hex << i << " :0x" << std::hex << (i ^ 0xdeadbeef) * 0x1337cafe<<std::endl;
    }   
}
```  
## Second Section: Password-Part1  
Ok, you could analyze every branch of the hooking system and find out what happens when a syscall was called in the parent.  
But where should we search for the flag? Ok in the ``` 0804993A``` is a check that checks the signal of the parent program with ```SIGILL or 0x4```. This signal is generating when the parent process encounters an invalid instruction. Do you remember when this happens? If you remember the child overwrite the first 2 bytes of that function which checks the input buffer with sunshine string, with two invalid bytes. So, when the parent process goes to check the password, it will throw a SIGILL signal due to those invalid bytes and the child process finds out that the user entered the input and the parent process now wants to checks it.
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/14.png)  
Ok now when the SGILL occurs, the child, reads the password buffer from the parent (in function ``` 08049975```) and also reads the registers of the parent and changes EIP to ``` 08048DCB```. So, when the parent continues after the SIGILL, it goes to ``` 08048DCB``` function. I named this function as ```pass_func```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/15.png)  
Now let’s analyze this function. The function performs some calls to functions and also you see some strings there. For example, ```rm -r``` etc. and passes these strings to ```execve``` function. But we saw that the syscalls are hooked with child1 and do another functionality. So these strings are useless and just are used for fooling the analyzer.  
Ok, there is a check for the first part of the password. 
You could reverse all these functions and find out what happens there and find out the password. But there is another easy way. If you look at the end of this function, you see a ```memcmp``` that compares our entered password, with a 16 byte buffer and if there was equal, it continues, otherwise, it goes to the end of the function. What we can do is that hook the ```memcmp``` and checks the arguments. Ok I used ```LD_PRELOAD``` hooking method in Linux.  
```C
#include <stdlib.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

int (*orig_memcmp)(const void*,const void*,size_t);
int memcmp(const void* s1,const void* s2,size_t n)
{
	printf("memcmp:%d\n",n);
	size_t i;
	for (i = 0; i < n; i++)	
	{
    		printf("%c", *(char*)(s2+i));
	}
	printf("\n");
	if(!orig_memcmp)
		orig_memcmp=dlsym(RTLD_NEXT,"memcmp");

	int result=orig_memcmp(s1,s2,n);
	return result;
}
```
After compile it as a Library and run the file:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/hook.png)  
#### ```Password_Part1: w3lc0mE_t0_Th3_l```  
Ok now we have the first part of the password. Continue this function until find out the second part. The password has 3 parts and you should find every part from a special function.  
## Third Section: Password-Part2
Now after the first 16 bytes of the password was correct; the second 16 bytes of the password go to another function for checking. I named this function ```pass2_func```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/16.png)  

At the beginning of this function we see a call to ```nice``` syscall with the ```A4``` argument. The syscall number of the nice is 0x22 and its magic number will be ``` 3DFC1166``` and we could find it in the hooking area.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/17.png)  
And        
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/18.png)    
After the call to nice, it negative the EAX value and moves it to s buffer and then sends the s to ```strlen```. But what is the s? for knowing this, we should find out what happens when the nice is calls. Long story short. If you debug the process(I will tell you how we can debug the process), you find out that the nice branch is never executed. This is because the nice syscall is a classic syscall that is removed from the new Linux OS and the new syscalls ```SetPriority and GetPriority``` have replaced with it. And when you call nice in the new Linux OS, the OS calls the SetPrioirty syscall and then GetPriority. So we should trace these two syscalls and if you find the number of these two syscalls you see their branches:  
```  
GetPrioirty magic number: 0x60 xor 0xDEADBEEF * 0x1337CAFE = 0x9678E7E2    
SetPrioirty magic number: 0x61 xor 0xDEADBEEF * 0x1337CAFE = 0x 83411CE4    
```  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/19.png)    
If you see, the var_c4 goes to ```EAX``` and a function calls and has just an argument that is the value of var_c4. Var_c4, actually is the EAX value of the parent. Var_c4 is a member of the ```user_reg_struct``` that is described in the previous section. And we know that the EAX value is ```0xA4``` from pass2_func. But if you look at this ``` sub_804C438``` function, you find out that this is a decoding function. You could reverse it and find out its result or you could debug the code. Because I am too lazy to reverse it, I choose the second way. But for debugging we have some limitations. 
We said that due the Ptrace calls that childs are used, we cannot debug the process. But there is a way for finding the output of the decoding function we need to debug the child1. So, we should disable the child2. One way is to debug the program and let it go until the call to fork for the creation of the child2. Then change the EIP to the address of ```SetPriority``` branch. In this way, the child2 never runs and we could just find out what is the output of the decoding function.  
OK for this job run the program with gdb and set a bp on the ```08049152``` and start the program.  
### Tip: after the fork, the gdb switches to the forked process by default. So when we run the program under gdb, it goes automatically to child1.  
Ok now when we reach this point, we could change the ```EIP``` to ```0x08049554``` where is the address of the setpriority branch. Then we change the value of the EAX to ```0xA4``` and run the decoding function.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/20.png)        
Now change the eip:    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/21.png)     
And after the call we see the output string in eax :  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/22.png)       
Now we find out the output of the SetPriority (or Nice) . this is the string that used in pass2_func and goes to strlen function.    
```nice(0xa4): This string has no purpose and is merely here to waste your time.```      
Ok return to analyze the pass2_func. Now we find out that the output of the nice call goes to the strlen function and then we see a call to a function.    
```C
unsigned __int64 __cdecl CRC64(unsigned __int64 a1, int a2, unsigned __int64 a3)
{
  int v3; // eax
  unsigned __int64 v5; // [esp+8h] [ebp-20h]
  unsigned __int64 i; // [esp+18h] [ebp-10h]

  v5 = a1;
  for ( i = 0LL; i < a3; ++i )
  {
    v3 = (unsigned __int8)(*(_BYTE *)(i + a2) ^ v5);
    LODWORD(v5) = (v5 >> 8) ^ byte_8056960[2 * v3];
    HIDWORD(v5) = (HIDWORD(v5) >> 8) ^ dword_8056964[2 * v3];
  }
  return v5;
}
```
This function is like the crc functions. If you search and find some crc functions you see this is exactly a crc function. Also I found the code that the author of this file is used. [CRC64](https://github.com/srned/baselib/blob/master/crc64.c)   
After that the crc of the string is calculated, we see that the 32 bytes of the password (the second part) copy to the begging of the file buffer with ```memcpy``` and then the crc value, file buffer, and another buffer goes to a function ```sub_804C369```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/23.png)  
In this function, we see another function. These functions are to perform some encryption-decryption operations. But there are some tricks for making the analysis hard.  
You have to reverse these functions and rewrite them in python or any other languages to find the second part of the password. But let’s look at the ``` 0804C217``` function. I named this function as ```KeyInit``` function because there is an initialization of a key buffer that will use in the encryption. The algorithm used in this section is tiny encryption but it is customized. Now if you look at this [TinyEnc](https://github.com/0x000000AC/Tiny-Encryption-Algorithm/blob/master/tea64.c) you could find out what happens in this function.  
Ok if we go to the ```KeyInit``` function, we see some syscalls that exist in the syscall hooking area. For example, we see ```pivot_root, mlockall, uname``` these syscalls is replaced with other operation. For example, the ```pivot_root``` just moves the value in ecx to ebx. Let’s look at it for a better understanding.  
At first, let’s look at the pivot_root document.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/25.png)    
The first argument of every syscall in the Linux goes to ```EBX```, the second argument to ```ECX``` and go on. So in the ```KEYInit``` function, we see that the first argument is in eax and second is in ecx. And then when the syscall wants to execute, the first argument (eax) moves to ebx and the second one (ecx) moves to ecx and the number of syscall(in this case 0xd9 or 217) moves to eax. Ok so we could analyze every syscall in this way. Now we should find the branch of thepivot_root.  
The pivot_root syscall number is 0xd9 and its magic number becomes ```0E8135594``` so we could find its branch.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/24.png)    
Now you see that the pivot_root branch, uses var_c8 (the ecx value of parent in ```user_reg_struct```) and var_cc (the ebx value of parent in ```user_reg_struct```) and then writes the value in var_c8 (ecx) to var_cc address in the parent memory with ```POKE_DATA``` request. If I want to simplify it for you, it just does a mov function. You could remove it from code and replace it with a mov instruction:  
```asm
MOV [ebx], ecx  
```   
So you could continue analyzing in this way for other syscalls like uname and mlockall.  
Now here we have another trick that has used in this program for makes the analysis harder.  
Do you remember that we are in the parent process? The pass2_func is in the child1, but if you remember, when the parent process makes the SIGILL signal, the child changes its EIP to the pass_func. So we are in the parent process and the parent process is running the pass2_func. 
Ok let’s look at a piece of KEYInit code.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/26.png)  
You see that the offset of location ```804c257``` is 
pushes and The var_38 moved to eax and then calls the eax. If you look at the code, you see that the var_38 is zero. So when the call, throws an exception with SIGSEGV signal because the address of the call is invalid. Now because the child1 is monitoring the parent process, it finds out that the parent throws an exception SIGSEGV and what happens? Look at the peace of code of the child1:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/27.png)    
The child1 checks the signal of the parent and if it was, SIGSEGV, performs some operations. At the end of these codes, you find out that it reads the registers of the parent process and change the eip address ```loc_804c257``` that pushed to stack and increase the value in var_38 by 1. So it just makes a loop in the KEYInit function. The KEYInit function looks like this image:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/28.png)    
Ok now, this trick is used another time in ``` sub_804C369``` function. I reverse these functions and rewrite them in Python:  
```Python
def KEYINT(k):
    num = 0x9C40
    for i in range(0, num // 4, 2):
        key = 0x674a1dea4b695809 ## the crc64 value
        for j in range(16):
            kk1, k0 = (key & 0xffffffff00000000) >> 32, key & 0xffffffff
            idx = (j * 8 * 32) - j * 8
            k[idx + 7] = k0
            k[idx + 19] = kk1

            cnt = 0
            key2 = key
            while key2:
                if key2 & 1:
                    cnt += 1

                key2 >>= 1

            k[idx + 41] = (cnt + (cnt & 1)) // 2
            odd = False
            if key & 1:
                odd = True
            key = (key >> 1) & 0xffffffffffffffff
            if odd:
                key = key ^ ((0x9E3779B9 << 32) | 0xC6EF3720) 
                
```    
Ok there is another trick that used in this program. If you locate the ```chmod``` syscall in the syscall hook area, you find out in performs a function for reading a buffer from the parent (which is the a peace of the KEY value) the uses a function that in that function you see some numbers that pushed in the stack before calls to eax. What is these numbers? Ok when the chmod function is called from parent process, the child1 alter that the parent is calling a syscall and so on. So the chmod function is running in child1 process. If you look at the function that chmod uses it and there are some magic numbers, you see that the value that moves to eax, is a zero value.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/29.png)  
So when it calls a zero value, the child1 throw an exception with signal SIGSEGV. But this time, the child2 is alerted that its parent, has a problem. So we should go to child2 code to find out what happens when the child1 generates a SIGSEGV.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/30.png)  
Ok so if you continue analyzing the child2, you see that when its parent generates a SIGSEGV, it read all register of the child1 and then looking for the magic number that pushed to stack before the SIGSEGV.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/31.png)    
For example for this magic number, it read the values that is pushed in the stack before the ```call eax``` and add them together and moves the result in the eax.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/32.png)    
After that the child2, change the value of EIP register with the value of esp register (the esp register, is pointing to return address. That is the address of next instruction after the call eax), to force the child1 to continue from after the ```call eax```.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/33.png)    
This the final trick. Long story short, you could analyze the chmod in this way and find out what does it. This is my script for encryption function:  
```Python  
def enc(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(16):
        idx = (j * 8 * 32) - j * 8
        var6 = v1 ^ a4[idx + 19]
        var3 = (v2 + a4[idx + 7]) & 0xffffffff
        var4 = ((var3 >> (a4[idx + 41] & 0x1F)) | (var3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        var6 = var6 ^ var4 
        v1 = v2
        v2 = var6

    data[0] = v2
    data[1] = v1
```
Now we should find the second part of the password. if you look at the pass2_func, after that encryption loop, the function calls the ```truncate()``` function and sends the file buffer that had went to the encryption function. The first 32 bytes are the second part of the password that we entered. But now are encrypted. Like as other function, the ```truncate()``` function also is the rabbit hole. We should find out its branch in the hooking area and find out what does the truncate syscall.  
Base on the syscalls in Linux, the first argument moves in the EBX and the second in ECX, so the file buffe is in ebx and 32 is in ecx. Now let’s and look at the branch of the truncate in hooking area.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/34.png)  
This function, reads the ebx register from parent (which in this case ebx contains the encrypted file buffer) and then call a function ```sub_804BBF8```. This function is used in this program many times and if you analyze it, you find out that is used for reading data from the parent. So, in this case this function reads 40000 of bytes from the file buffer offset in parent and save it in a buffer in child1 process. Then it compares the first 32 bytes of the file buffer which is the encrypted second part of user inputted password, with a buffer at address ```81A5100```.    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/35.png)  
So we could find out that this new 32 buffer is the second part of the password but is encrypted. So we should decrypt it to find the second part of the password. We have the encryption function and we know that this is tiny encryption, so we could reverse it and writes its decryptor function. This is my python decryptor:  
 ```Python
def dec(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(15, -1, -1):
        idx = (j * 8 * 32) - j * 8
        var6 = v1 ^ a4[idx + 19]
        var3 = (v2 + a4[idx + 7]) & 0xffffffff
        var4 = ((var3 >> (a4[idx + 41] & 0x1F)) | (var3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        var6 = var6 ^ var4 
        v1 = v2
        v2 = var6

    data[0] = v2
    data[1] = v1
```  
Know we should run the decryptor and decrypt the ```81A5100``` buffer.  
```Python
def KEYINT(k):
    num = 0x9C40
    for i in range(0, num // 4, 2):
        key = 0x674a1dea4b695809 ## the crc64 value
        for j in range(16):
            kk1, k0 = (key & 0xffffffff00000000) >> 32, key & 0xffffffff
            idx = (j * 8 * 32) - j * 8
            k[idx + 7]  = k0
            k[idx + 19] = kk1

            cnt = 0
            key2 = key
            while key2:
                if key2 & 1:
                    cnt += 1

                key2 >>= 1

            k[idx + 41] = (cnt + (cnt & 1)) // 2
            odd = False
            if key & 1:
                odd = True
            key = (key >> 1) & 0xffffffffffffffff
            if odd:
                key = key ^ ((0x9E3779B9 << 32) | 0xC6EF3720)

def dec(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(15, -1, -1):
        idx = (j * 8 * 32) - j * 8
        var6 = v1 ^ a4[idx + 19]
        var3 = (v2 + a4[idx + 7]) & 0xffffffff
        var4 = ((var3 >> (a4[idx + 41] & 0x1F)) | (var3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        var6 = var6 ^ var4 
        v1 = v2
        v2 = var6

    data[0] = v2
    data[1] = v1
    

key=[0]*3968;
v=[0]*2
f=[0]*10000
se=[0]*8
j=0
KEYINT(key)

for i in range(0,8,2):
    v[0]=ida_bytes.get_dword(0x081A5100+i*4)
    v[1]=ida_bytes.get_dword(0x081A5100 +(i+1)*4)
    dec(v,key)
    se[j]=v[0]
    se[j+1]=v[1]
    print(hex(v[0]))
    print(hex(v[1]))
    j=j+2
    
fd = open("pass","wb")
for st in se:
    fd.write(struct.pack('<I', st))
fd.close()
```  
I ran this script in the IDAPro and when it finishes, the result writes in the ```pass``` file.  
The second part is:  
#### ```Password_Part2: 4nD_0f_De4th_4nd_d3strUct1oN_4nd```    

## Forth Section(maybe final :D): Password-Part3
OK we need another part of password. The whole file have analyzed and there isn’t any special trick or tip. But where should we search for third part of the password? There is only one thing. The 40K encrypted buffer. We should find out what is these bytes. We have 2 ways to extract the encrypted buffer (I say encrypted because the algorithm is used for encryption is a tiny which doesn’t matter you use its encrypt function or decrypt function, both of them could use for encryption or decryption. but it depends which of them is used.) Now we reverse the encryption and could use it to encrypt the file buffer and then find out what are these data.  
```Python
def KEYINT(k):
    num = 0x9C40
    for i in range(0, num // 4, 2):
        key = 0x674a1dea4b695809 ## the crc64 value
        for j in range(16):
            kk1, k0 = (key & 0xffffffff00000000) >> 32, key & 0xffffffff
            idx = (j * 8 * 32) - j * 8
            k[idx + 7]  = k0
            k[idx + 19] = kk1

            cnt = 0
            key2 = key
            while key2:
                if key2 & 1:
                    cnt += 1

                key2 >>= 1

            k[idx + 41] = (cnt + (cnt & 1)) // 2
            odd = False
            if key & 1:
                odd = True
            key = (key >> 1) & 0xffffffffffffffff
            if odd:
                key = key ^ ((0x9E3779B9 << 32) | 0xC6EF3720)

def enc(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(16):
        idx = (j * 8 * 32) - j * 8
        var6 = v1 ^ a4[idx + 19]
        var3 = (v2 + a4[idx + 7]) & 0xffffffff
        var4 = ((var3 >> (a4[idx + 41] & 0x1F)) | (var3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        var6 = var6 ^ var4 
        v1 = v2
        v2 = var6

    data[0] = v2
    data[1] = v1    

key=[0]*3968;
v=[0]*2
f=[0]*10000
j=0
KEYINT(key)    
for i in range(0,10000,2):
    v[0]=ida_bytes.get_dword(0x804C640+i*4)
    v[1]=ida_bytes.get_dword(0x804C640 +(i+1)*4)
    enc(v,key)
    f[j]=v[0]
    f[j+1]=v[1]
    j=j+2

fd = open("shellcode","wb")
for st in f:
    fd.write(struct.pack('<I', st))
fd.close()  
```    
I ran this script in IDAPro and we have the 40K buffer in the shellcode file.  
When open the shellcode file in a hex-editor you see that this file is a text file. But you see some unreadable bytes between these strings. If you open the file in the IDAPro, it could detects functions and codes of this file. But where is the start point of the file and where should we start our analyzing?  Let’s change our question. How this shellcode is run in the code?  
Maybe there is another trick that we should find it. The shellcode decrypted and went to the truncate function. Then truncate, checks the first 32 bytes of it and…? We should analyze it deeper.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/36.png)  
This image is from `truncate` branch. There is a smart trick, and you should find it cleverly. There is a loop that iterate the file buffer and moves bytes of file buffer to another buffer with ``` var_3F4C``` name (in 2), and every time checks the value of file buffer with zero (in 1). The file buffer has 40K of bytes and the ``` var_3F4C``` just has 13360 of bytes. Also there isn’t a check for the size in this loop.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/37.png)  
So if the moving continue until the end of file buffer, we have an overflow.  So find out when the loop breaks. For this we should find the first zero byte in the shellcode or file buffer that have extracted from the IDA.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/38.png)  
Ok so the first zero byte is at offset ```3F20```. So 16160 bytes of file buffer, will copy to ```var_3F4C```. But this buffer has 13360 of bytes length!! So we have an overflow. Ok let’s continue. For example the loop reaches at the first zero byte and breaks. Now the buffer of password pushes to stack and the value of ```var_28``` that is zero goes to eax and the child1 calls the eax. But wait a minute. Are you sure the value of ```var_28``` is zero?  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/39.png)  
We have an overflow and if you do some calculation you find out that the var_28 is affected with the overflow.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/40.png)  

```
Size of var_3F4C buffer: 13360  
Copied bytes: 16160  
Diff var_3F4C and var_28 = 3f4c-28=16164  
```
Based on our calculations, the last 4 bytes is in the var_28. What is these bytes?  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/41.png)  
Ok so we find out that ```call eax``` is actually ```call 0x08053B70``` (the value of var_28 in little endian).  This is the entry point of the shellcode. :D  this address is an address at middle of file buffer. The child1 just change the program routine to an address in itself.  
Ok now we know the entrypoint of the shellcode. But we need just its offset because we analyze the shellcode file seprately in IDAPro. So the etrypoint offset is:  
``` the shellcode entrypoinnt - file buffer base addr = 0x08053B70 - 0x0804C640 = 0x7530```  
Now open the shellcode in IDAPro and go to 0x7530 offset:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/10/pics/42.png)  

This shellcode performs some calculations and at the end, compares 2 values and if they were equal, it writes the 32 value in eax register of parent and exit otherwise, write -1 in eax and exits.  So we should analyze this function and find out what happens there.  
At first, we see that the shellcode uses a ```call $5```, so it just push the address of the next instruction(```pop eax```) in the stack and goes to next instruction. So now when the ```pop eax``` executes, the address of itself is moves to eax. ```eax= 7530```.  
[sh2.png]
Subtracts ```0x0DCC``` from it and stores it in a variable that I named it ``` first_of_start_shellcode```.  
Ok after that we see a function is called three times and if you look at this function you find out that this function performs some operation like ```memset()``` and zeroes a buffer.    
[sh3.png]  
Now we see an adds operation , the ``` first_of_start_shellcode+12A6``` and passes the result to a function.  
[sh4.png]  
```0x7530+12A6= 0x87D6```  
[sh5.png]  
We see some big numbers in these address that is used. Ok if we look at the ```sub_7E07``` which I named it ``` bn_from_hex```, we see that this function makes hex number from a string number.  So we could guess that this is a Big Number calculation code. I searched in Google and saw some bignumbers codes in github. You could check this repo(https://github.com/ilia3101/Big-Integer-C/blob/master/BigInt.c) and find out every function what does in this shellcode.  
Long story short. This is an encryption function that uses a public key. The algorithm is used in the shellcode is a known algorithm , [EL-Gamal]( https://www.geeksforgeeks.org/elgamal-encryption-algorithm/).  
If you look at the code, you see that it encrypt the third part of entered password and then compare it with var_988 (bn_988). So we could find out that the var_988 is the  encrypted third part of the password. But how we can decrypt it to find the password? You need a [Multiplicative inverse] (https://en.wikipedia.org/wiki/Multiplicative_inverse#:~:text=In%20mathematics%2C%20a%20multiplicative%20inverse,%2Fb%20is%20b%2Fa.) to decrypt it.  
This is my script:  
```Python  
from Crypto.Util.number import long_to_bytes, inverse

p = 0xd1cc3447d5a9e1e6adae92faaea8770db1fab16b1568ea13c3715f2aeba9d84f
s = 0xc10357c7a53fa2f1ef4a5bf03a2d156039e7a57143000c8d8f45985aea41dd31
c2 = 0xd036c5d4e7eda23afceffbad4e087a48762840ebb18e3d51e4146f48c04697eb

p3 = long_to_bytes((c2 * inverse(s, p)) % p)[::-1]
print(p3)  

```




