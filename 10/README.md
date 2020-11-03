# break  
This challenge is a very hard one. You have a Linux ELF file that uses many anti-debugging techniques that don’t let you debug and analyze it easily.  
The file is x86 ELF and when you run it, shows you a prompt to enter a password.  
OK, when you open it in the IDAPro, you see in the main function is a password check routine that checks the input buffer with the string ```sunsh1n3_4nd_r41nb0ws@flare-on.com```. But when you enter this string as a password, t shows you ```sorry, but 'sorry I stole your input :)```.  
So what happened there? You decide to debug it in the gdb. But when you open it in the gdb, you see that program exited.  
Ok continue analyzing the file statically and you see that the program uses an ```ini``` function that is interesting for us.  
The ```init``` function is used in the ELF files for does some initialization before the main function is run.  
When you see the init function you see it has a loop that in it, calculates an address, and calls it.  
[1.png] 
Now we should find out what is the targets of this call. Ok because this part of the program is before the main, so we sure that the anti-debug protection isn’t enabled. To start the program in gdb and set a bp at the init function and debug it until this loop. If you see the function that is called in this loop you find out two functions. This is because the loop runs just 2 times.  
One of those functions is a function that seems doesn’t perform a special thing.  
[2.png] 
Another function is an important function. When you search the address of this function in the IDAPro, you find out the function is a function that uses ```Fork()``` system call to create a child of the current process.  
[3.png]     
[4.png]   
After the fork, the child process starts its job. When you see the child functionality, you find out that this function uses some system calls of the Linux for detecting debugging and defeat from debugging.    
[5-.png]
### Tip: you could use IDA symbolic constant feature, to make easy your job. It could detect the Ptraces requests and flags and also the signals.
The most used function is ```PTRACE```, which is used to attach to the parent process and checks the state of it. the child process uses ```ATACH``` method of PTRACE, to attach to its parent and then control it. if you see more the child function, you find out that when it couldn’t attach to its parent, it finds out that another process, attaches to the parent. So it detects that a debugger comes in and then, terminate the parent process with signal 9.  
[5.png] 
### TIP:A process can only be attached by another process at a time.  
The child process also monitors the system calls of its parent. when a parent wants to call a function, a signal is generated and the child finds out that the parent wants to call a system call. So the child will decide, how the parent continues its functionality. 
There are just some PTRACE tricks that malware use for anti-debugging and if you read the PTRACE documents, you could find the behavior of the child process.  
So the child is a watchdog of its parent. Also, it checks the functionality of the parent at the same time, such as system calls, which performs this with ```PTRACE_SYSEMU```.  
[pic6.png]

There are some tricks that the child is using, which is important and I explain their: 
If you look at the child carefully, you see it uses another call to fork. This time it creates another child of itself.  
[pic7.png] 
This time the second child is as the first child. But the child1 is watching the parent process, but the child2 watches its parent (the child1). This is due, you could attach the debugger to the child1 and debug it. But now you cannot do this. Because the child1 is watching with child2. The big picture of this program is like this picture:  
[8.png] 
So with this scenario, we just could attach to the child2 and debug it. But no. there is another Ptrace call that the child1 uses to monitor the child2 :D. So, debugging is hard work and we cannot do it easily. We can do it if we patch some calls but the functionality of the program will corrupt.  
Another trick that the child1 is used is at the ```08049120```. The child1, uses the ```PTRACE_POKEDATA``` request, to change the value of an address in the parent. the address is ``` 8048CDB``` and the value that uses to write to this address is ``` 0B0F```.  
[9.png] 
If you see the ```8048CDB```, it is the address of the function that checks the ```Sunshine``` string with the input buffer in the main function. This call uses Ptrace to change the first 2 bytes of the ```check_sunshine``` function to ```0B0F```. So the beginning of the function will change from ```55 89``` to ```0B0F``` and the new value hasn’t any special meaning in the assembly.  
[10.png]

Another trick that child1 is using to detects debugging, is a check for 0xCC byte. You know when a debugger wants to set a breakpoint at an address, it writes a 0xCC at the beginning of that address (INT 3).  
[11.png] 
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
You know that in Linux’s syscalls, the number of the syscall, will put in EAX, so the child1 read RAX and xor it with ```DEADBEEF``` then multiple it by ```1337CAFE``` then, compare the result with some value.  
[12.png]   
Every branch goes to a special function and if you look, there is a hooking system that changes the functionality of a syscall. For example, if the parent calls the ```execve``` syscall, the tracer will notice that the parent calls a syscall. It gets the syscall number that stored in EAX register. 0x0b is the syscall number of the ```execve``` in x86:  
0x0b XOR 0xDEADBEEF = 0xDEADBEE4  
0xDEADBEE4 * 0x1337CAFE= 10B76D10F7FF4E38 convert to int = 0xF7FF4E38 
Now if you look at the code of child1 you see that if the result is 0xF7FF4E38, it goes to address ```0x0804948B```.   
[13.png]  
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
Ok, you could analyze every branch of the hooking system and find out what happens when a syscall was called in the parent.  
But where should we search for the flag? Ok in the ``` 0804993A``` is a check that checks the signal of the parent program with ```SIGILL or 0x4```. This signal is generating when the parent process encounters an invalid instruction. Do you remember when this happens? If you remember the child overwrite the first 2 bytes of that function which checks the input buffer with sunshine string, with two invalid bytes. So, when the parent process goes to check the password, it will throw a SIGILL signal due to those invalid bytes and the child process finds out that the user entered the input and the parent process now wants to checks it.
[14.png]  
Ok now when the SGILL occurs, the child, reads the password buffer from the parent (in function ``` 08049975```) and also reads the registers of the parent and changes EIP to ``` 08048DCB```. So, when the parent continues after the SIGILL, it goes to ``` 08048DCB``` function. I named this function as ```pass_func```.  
[15.png]  
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

Ok now we have the first part of the password. Continue this function until find out the second part. The password has 3 parts and you should find every part from a special function.  
Now after the first 16 bytes of the password was correct; the second 16 bytes of the password go to another function for checking. I named this function ```pass2_func```.  
[16.png]    

At the beginning of this function we see a call to ```nice``` syscall with the ```A4``` argument. The syscall number of the nice is 0x22 and its magic number will be ``` 3DFC1166``` and we could find it in the hooking area.  
[17.png]    
And        
[18.png]        
After the call to nice, it negative the EAX value and moves it to s buffer and then sends the s to ```strlen```. But what is the s? for knowing this, we should find out what happens when the nice is calls. Long story short. If you debug the process(I will tell you how we can debug the process), you find out that the nice branch is never executed. This is because the nice syscall is a classic syscall that is removed from the new Linux OS and the new syscalls ```SetPriority and GetPriority``` have replaced with it. And when you call nice in the new Linux OS, the OS calls the SetPrioirty syscall and then GetPriority. So we should trace these two syscalls and if you find the number of these two syscalls you see their branches:  
GetPrioirty magic number: 0x60 xor 0xDEADBEEF * 0x1337CAFE = 0x9678E7E2    
SetPrioirty magic number: 0x61 xor 0xDEADBEEF * 0x1337CAFE = 0x 83411CE4    
[19.png]      
If you see, the var_c4 goes to ```EAX``` and a function calls and has just an argument that is the value of var_c4. Var_c4, actually is the EAX value of the parent. Var_c4 is a member of the ```user_reg_struct``` that is described in the previous section. And we know that the EAX value is ```0xA4``` from pass2_func. But if you look at this ``` sub_804C438``` function, you find out that this is a decoding function. You could reverse it and find out its result or you could debug the code. Because I am too lazy to reverse it, I choose the second way. But for debugging we have some limitations. 
We said that due the Ptrace calls that childs are used, we cannot debug the process. But there is a way for finding the output of the decoding function we need to debug the child1. So, we should disable the child2. One way is to debug the program and let it go until the call to fork for the creation of the child2. Then change the EIP to the address of ```SetPriority``` branch. In this way, the child2 never runs and we could just find out what is the output of the decoding function.  
OK for this job run the program with gdb and set a bp on the ```08049152``` and start the program.  
### Tip: after the fork, the gdb switches to the forked process by default. So when we run the program under gdb, it goes automatically to child1.  
Ok now when we reach this point, we could change the ```EIP``` to ```0x08049554``` where is the address of the setpriority branch. Then we change the value of the EAX to ```0xA4``` and run the decoding function. 
[pic20.png]  
Now change the eip:  
[pic21.png]  
And after the call we see the output string in eax :  
[pic22.png]    
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
This function is like the crc functions. If you search and find some crc functions you see this is exactly a crc function. Also I found the code that the author of this file is used. (look at this repo)[https://github.com/srned/baselib/blob/master/crc64.c]   
After that the crc of the string is calculated, we see that the 32 bytes of the password (the second part) copy to the begging of the file buffer with ```memcpy``` and then the crc value, file buffer, and another buffer goes to a function ```sub_804C369```.  
[pic23.png]    
In this function, we see another function. These functions are to perform some encryption-decryption operations. But there are some tricks for making the analysis hard.  
You have to reverse these functions and rewrite them in python or any other languages to find the second part of the password. But let’s look at the ``` 0804C217``` function. I named this function as ```KeyInit``` function because there is an initialization of a key buffer that will use in the encryption. The algorithm used in this section is tiny encryption but it is customized. Now if you look at this (repo)[ https://github.com/0x000000AC/Tiny-Encryption-Algorithm/blob/master/tea64.c] you could find out what happens in this function.  
Ok if we go to the ```KeyInit``` function, we see some syscalls that exist in the syscall hooking area. For example, we see ```pivot_root, mlockall, uname``` these syscalls is replaced with other operation. For example, the ```pivot_root``` just moves the value in ecx to ebx. Let’s look at it for a better understanding.  
At first, let’s look at the pivot_root document.    
[pic25.png]  
The first argument of every syscall in the Linux goes to ```EBX```, the second argument to ```ECX``` and go on. So in the ```KEYInit``` function, we see that the first argument is in eax and second is in ecx. And then when the syscall wants to execute, the first argument (eax) moves to ebx and the second one (ecx) moves to ecx and the number of syscall(in this case 0xd9 or 217) moves to eax. Ok so we could analyze every syscall in this way. Now we should find the branch of thepivot_root.  
The pivot_root syscall number is 0xd9 and its magic number becomes ```0E8135594``` so we could find its branch.    
[24.png]  
Now you see that the pivot_root branch, uses var_c8 (the ecx value of parent in ```user_reg_struct```) and var_cc (the ebx value of parent in ```user_reg_struct```) and then writes the value in var_c8 (ecx) to var_cc address in the parent memory with ```POKE_DATA``` request. If I want to simplify it for you, it just does a mov function. You could remove it from code and replace it with a mov instruction:  
```asm
MOV [ebx], ecx  
```   
So you could continue analyzing in this way for other syscalls like uname and mlockall.  
Now here we have another trick that has used in this program for makes the analysis harder.  
Do you remember that we are in the parent process? The pass2_func is in the child1, but if you remember, when the parent process makes the SIGILL signal, the child changes its EIP to the pass_func. So we are in the parent process and the parent process is running the pass2_func. 
Ok let’s look at a piece of KEYInit code.  
[pic 26.png]  
You see that the offset of location ```804c257``` is 
pushes and The var_38 moved to eax and then calls the eax. If you look at the code, you see that the var_38 is zero. So when the call, throws an exception with SIGSEGV signal because the address of the call is invalid. Now because the child1 is monitoring the parent process, it finds out that the parent throws an exception SIGSEGV and what happens? Look at the peace of code of the child1:  
[pic 27.png]  
The child1 checks the signal of the parent and if it was, SIGSEGV, performs some operations. At the end of these codes, you find out that it reads the registers of the parent process and change the eip address ```loc_804c257``` that pushed to stack and increase the value in var_38 by 1. So it just makes a loop in the KEYInit function. The KEYInit function looks like this image:  
[pic28.png]  
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
If 
I told that the algorithm used in this program is tiny encryption. 


