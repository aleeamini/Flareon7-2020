# 9- crackstaller  
## First section:  
The hard challenges starts at the moment. This file is a executable file that at the first glance, we see the ```.data``` section is encrypted. So we have a file that probably is packed. Ok let’s run it in a VM to locate its behavior. I use a Windows7-x64 as guest OS and a Windows10-x64 as host.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/encrypted-data.png)  
When you run the file, it doesn’t do any special thing, So we start analysis it in a debugger. When you run the program in the debugger and stepping over until reach at the main function, you see that, at the ``` 000000013FF03118```, before the main function, the program, throws an exception.   
So dive in this function to see what happened there. When you step into it, you see a loop that does some operation and make an address and moves it to ```rax``` and calls it (```013FF65B51```).  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/second-round.png)  

If you look at this function, at the second round, it goes to a suspicious function that does, ```runtime loading```.   
For example, in my case at ``` 013FBA1CD8``` you see the function is used from ```LoadLibraryA``` and ```GetProcAddress``` APIs.  
But before the call to the ```LoadLibraryA``` you see a function (``` 013FBA1D14```), this function gets an encoded string and decode it, which decoded string is the library name.  I named this function: ```data_decoder()```  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/decrypt-libname.png)  
  
Now you see some interesting names in this function that used in ```Loadlibrary``` and ```GetprocAddr``` such as:   ```CreateService, OpenService, CloseService, StartService, ControlService, DeleteService, OpenSCManager and CreateFile```  
After load this functions, the program goes to another function and does some functionally and then goes to ``` 013FBA2575```  
This function, does some decryption operations and, decrypt a ```PE``` file in the memory.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/decode-pefile.png)  
  
I short the story. If you see, this function is called 2 times and if you trace it, you find that it decrypt two PE files in the memory.  
You should dump these files, and when open them in the IDAPro, you find out that you found two driver file.  
OK so interesting. After that the program decrypt those PE files, it goes to a function at ``` 013FBA25B6``` which decode strings and convert it to Unicode. And if you look at this function you see it decodes the string, ```C:\Windows\System32\cfs.dll```.  
This dll isn’t in the ```system32``` so maybe the program wants to writes one of those decrypted files, as cfs.dll in the system32.  
Ok when you continue debugging, you find out that the function uses ```CreateFileW``` and ``` CreateFileMappingA```, to write one of those decrypted files, in ```CFS.dll```.  
After that you see it uses ``` 013FBA25B6``` again, but this time you see the string ```\\.\Htsysm72FB``` .  
If you continue debugging the code, you see that the program uses ```OpenSCManger, CreateService and …``` to create a service with ```cfs``` name. and when created the service successfully, uses the ```CreateFile``` API to creates a file with ```\\.\Htsysm72FB``` name. This isn’t a regular file. It is a device name which drivers usually creates for communication with kernel.   
So until now, we found that the executable uses a function to load some services and drivers related functions, then decrypt two drivers and loads them in memory, write one of them in the system32 as ```cfs.dll``` and creates a service with this dll. So we have a new service in our windows with ```cfs``` name. There is a tip: how the executable file could load its driver in windows while driver signature checking is enabled in the windows?  
OK I dumped these files. I named one of the ```cfs-driver.sys``` and the other, ```bb-driver.sys```.  
Now if you open the cfs-driver.sys in the IDAPro, you will see this is a little driver with just 8 functions.  If you search about ```\\.\Htsysm72FB```, you find out this a famous driver, ```Capcomm``` and it is a signed driver. The driver provides ring0 code execution as a service! It's only function is to take a user-land pointer, disable SMEP, execute code at the pointer address and re-enable SMEP. For more info read this article (https://fuzzysecurity.com/tutorials/28.html).  
Ok now we know that ```Capcomm Driver``` is used for load a unsigned driver or executing user-mode code from kernel mode.  
If we continue debugging, in the ```13F912697``` function, we see a string is generated ```DriverBootStrap``` and after that if you debug carefully the program, you see that the second PE file which decrypted from previous section, now is used here.  
If you look at the second driver that dumped it in previous section, you see it has a function with ```DriverBootStrap``` name that does some functionality.  
If you continue debugging the code, you find out that, the program tries to find the address of this function (DriverBootStrap) and after that calls the ```DeviceIoControl```. Ok let’s look at the function:  
```
BOOL DeviceIoControl(
  HANDLE       hDevice,
  DWORD        dwIoControlCode,
  LPVOID       lpInBuffer,
  DWORD        nInBufferSize,
  LPVOID       lpOutBuffer,
  DWORD        nOutBufferSize,
  LPDWORD      lpBytesReturned,
  LPOVERLAPPED lpOverlapped
);
```
DeviceIoControl(handle of Htsysm72FB device,0xAA013044, shellcode address, so on …);  
The third argument is a pointer to a shellcode’s address and it is just a jump to the ```DriverBootstrap``` function.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/addr_shellcode.png)  
If you see the shellcode in the disassembler it is a little code like this:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/jump_at_bootstarp.png)    
If you follow the jump address, you see it is start of a function in the ```crackinstaller.exe``` .  
OK But what happen when the DeviceIoControl is called? The DeviceIoControl is use for communication between user-mode and kernel-mode (Driver). The user-mode program sends a code to the driver, and driver performs the corresponding operation to that code.   So now we should debug the Driver (cfs) to find out what will happen in the kernel space, after ```DeviceIoControl``` is called.  
Until now we find out that the program decrypt two driver file in memory, write one of them to ```System32``` as ```CFS.dll``` and after that uses ```OpenSCManger,CreateService and etc.``` to creates a service and ```CreateFile``` to creates a device for communication between driver and executable and then calls ``` DeviceIoControl``` and pass the address of a shellcode that jumps to a function in the ```Crackinstaller.exe```.  
Now if you continue debugging you see that the function, deletes the service, closes the handle of file and does a cleanup. But at the end of the function you see the function uses two times of ```CloseHandle()``` function. At the first time, closes the handle of the ```cfs.dll``` file which has been opened with ```CreateFile()``` and then uses again from ```CloseHandle()``` to close previous handle that closed recently. What happens here is that CloseHandle tries to close an invalid handle and the program throw an exception.  
You could patch the function to continue. After that this function returns, now the program continue until reaches at the ```main()``` function.   
I short the story. In the main function of the program you see that program decrypt another ```MZ``` file and then save it in the ```%appdata%\ Microsoft\Credentials\Credhelper.dll``` and after that load this dll with ```LoadLibraryA()``` and then calls ```DllRegisterServer()``` function of this dll. This function just registers the dll in the Registry and then creates two registry keys: Config and InprcServer32 and creates two value in the ```Config``` key, the ```Flag and Password```.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/regedit.png)    
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/regeditvals.png)    
In the flag and Password values, aren’t anything so what should we do?  
OK before we go to debugging the kernel and cfs driver, let’s look at the ```credHelper32.dll```.  
If you look at the functions of ```CredHelper32.dll``` you see two functions are used ```Flag``` one of them is ``` DllRegisterServer``` and another is ``` sub_1800016D8```:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/enc_flag.png)    
Maybe this is the encrypted password. But what is decryption key? And how we should decrypt it? The answer is in the driver.  So let’s debug the driver. For this section you need to prepare your Lab for kernel debugging. Read (this)[https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-kernel-mode-debugging-in-windbg--cdb--or-ntsd] to make a lab for kernel debugging.  
We know that the ```Crackinstaller.exe``` creates a service and start it. When the service is started, the ```CFS.dll``` loads into the kernel as a service. So we should catch the driver when loads into the kernel and then debug it.  
When we set a bp at ```DeviceIoControl``` in ```crackinstaller.exe```, we know that the driver is loaded in the kernel. We can find the driver and get its ```Driver_Object``` : ![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/drvobj.png)    
Now we should find which function of the driver will run, when ``` DeviceIoControl()``` is called. As you know every request has a unique number and the drive has a ```MajorTable``` that assign a request number to a function. To find which function is assigned to handle the ``` IRP_MJ_DEVICE_CONTROL``` that is the ``` DeviceIoControl()``` request, we should use the major table of the driver and find the ```0xe``` index.  
```
kd> dt nt!_DRIVER_OBJECT fffffa801a9ebd50
   +0x000 Type             : 0n4
   +0x002 Size             : 0n336
   +0x008 DeviceObject     : 0xfffffa80`1ab02240 _DEVICE_OBJECT
   +0x010 Flags            : 0x12
   +0x018 DriverStart      : 0xfffff880`04e2a000 Void
   +0x020 DriverSize       : 0xc00
   +0x028 DriverSection    : 0xfffffa80`1a995df0 Void
   +0x030 DriverExtension  : 0xfffffa80`1a9ebea0 _DRIVER_EXTENSION
   +0x038 DriverName       : _UNICODE_STRING "\Driver\cfs"
   +0x048 HardwareDatabase : 0xfffff800`02f8e568 _UNICODE_STRING "\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM"
   +0x050 FastIoDispatch   : (null) 
   +0x058 DriverInit       : 0xfffff880`04e2a63c     long  +0
   +0x060 DriverStartIo    : (null) 
   +0x068 DriverUnload     : 0xfffff880`04e2a47c     void  +0
   +0x070 MajorFunction    : [28] 0xfffff880`04e2a4e4     long  +0
kd> dq fffffa801a9ebd50+0x70+8*0xe l 1
fffffa80`1a9ebe30  fffff880`04e2a590
```
The major table is located at 0x70 index of ```Driver_OBJECT``` and we could find the ``` IRP_MJ_DEVICE_CONTROL``` with this command:  
``` kd> dq fffffa801a9ebd50+0x70+8*0xe L 1```  
The ``` fffff880`04e2a590``` is the address of the function that handle the ``` IRP_MJ_DEVICE_CONTROL``` request. So we set a bp at this address to can catch it when the ``` DeviceIoControl()``` is called.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/set_bp_at_major.png)  
Now press ```F8``` to continue the crackinstaller and you see the Windbg breaks at the ``` fffff880`04e2a590```.  
If you continue debugging in the Windbg, you see a call to a function (look at the function of cfs.dll in the IDAPro, you see a ```call sub 10524``` this is where the shellcode is run) :  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/func_in_driver.png)  
Now step into this function and continue until reach at the call that loads the shellcode:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/call_shellcode.png)  
Step into the function and we see the shellcode that in previous section talked about. It jumps back to crackinstaller.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/shellcode_in_windbg.png)  
Now continue to find what happens in this function of crackinstaller.exe. This function is at address ```140002A10``` of crackinstaller.exe.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/target_func_in_carck.png)  
I short the story. This function does some pool allocations and then use a call at address ```140002C26``` to create a thread with `` PsCreateSystemThread``` .    
```
NTSTATUS PsCreateSystemThread(
  PHANDLE            ThreadHandle,
  ULONG              DesiredAccess,
  POBJECT_ATTRIBUTES ObjectAttributes,
  HANDLE             ProcessHandle,
  PCLIENT_ID         ClientId,
  PKSTART_ROUTINE    StartRoutine,
  PVOID              StartContext
);
```
Now continue debugging until reach at this call and if you examine the value of ```RAX``` (the value of the start routine), you see this is a function that is familiar (address of Bootstrap). Set a bp on this address and press ```g``` to continue debugging until the thread reaches at this address.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/create_thread.png)  
Now we are in Bootstrap function and if you continue debugging this function, you find out it creates a driver using an undocumented API, ```IOCreateDriver``` .  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/io_create_driver.png)  
If you search about this undocumented function, you find out the arguments of this function:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/iodriver.PNG)  
The second parameter of this function is address of Driver_Entry.  You could find this address at the RDX in this case. This address is the Driver_Entry of the second Driver that the crackinstaller, decrypted at the first section.  
So this function creates a driver. The driver is created because the SMEP is disabled. Ok now we could set a bp on the address that is in rdx, which is the Driver_Entry of the new driver.  
So until now we find out that, the cfs driver is loaded in the kernel, when the crackinstaller calls the ```Startservie``` function and after that makes a call to DeviceIOControl() function. After that the driver handle this request with a function and runs the shellcode that sends to it. The shellcode jumps to a function of crackinstaller and then uses some functions to create a Thread in the kernel-space and runs the Bootstrap function of the second driver. the Bootstrap function of second driver calls IOCreateDriver function to create a new driver. Now we have a new driver in the kernel.  
So let’s analyze the ```Driver_Entry``` of the new driver and see what happens there. You should load the second driver in IDAPro and look at Driver_Entry. If you see there is a call to a function at ```14000918B```. We go to this function and see that there some functions.  But one of them is important for us.   
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/cmreg.png)    
  
The cmRegisterCallbackEx, registers a routine to monitor,block or modify a registry operation. What is this mean? If you look at the above picture, you see this function, uses the ``` sub_140004570``` to register it as a RegistryCallback. So when everywhere in the windows, wants to creates a key or delete or modify in the Registry, this function is called before the action is taken.  
So we could find that what will happened. This driver register a callback routine for registry, and after that if you remember the crackinstaller goes to create some keys in the registry. So this driver can monitor and modify those values and keys. Ok continue debugging in windbg until you reach at this call to cmRegisterCallbackEx and set a bp on the routine that used (```sub_140004570```). Now delete all previous breakpoints and press g. now in the guest windows you could continue debugging until reach at main function of carckinstaller.exe and where it used the ```CredHelper.dll``` to creates registry keys.  
### Tip: remember if you didn’t patch the program to bypass the second CloseHandle function that cause the exception, you couldn't continue.  
I short the story of this section. The registered function in the second driver, is called when every request to modify the Registry is comes to kernel. This function checks the address of the key that the caller wants to modify it and if this address, includes the ```Config``` string it does some operation otherwise it let them to go as normal way. This point is where that this check is taken.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/9/pics/wcsstr.png)    
So you could set a bp at this point and continue the debugging until the targeted key will come. When you continue this routine after some functions, you see that a string is generated ```H@n $h0t First!```. This is the password and also we have the encrypted flag. The algorithm is used is a RC4 and you can decrypt the flag with this password.
