# 2-garbage
## First Phase:
When we want run the exe file, we will see a error message from windows, that this file is invalid or something else.  
When we open file in the hex-editor, at the end of file we see that the ```Manifest.xml``` which windows uses for run the program, is corrupted.  
The file is packed with UPX. So i tried to unpack it with ```UPX3.96``` , but it said that file is corrupted. I thought it is due for corrupted Manifest.    
I used from a valid exe file and try to copy it's ```Manifest.xml``` to ```garbage.exe``` file.  
![alt text]  

## Second Phase  
Ok now we have a valid file. but when we run it, it seems doesn't run correctlly. so let's unpack it. but ```UPX``` still says that file is incrorrect.  
Now we have to unpack it manualy. the unpacker stub is a long jump at ```0x0041891C```. but when we start debugging it in the debugger, at some calls and lea or mov instructions, the program  
crashes because it can't resolve some addresses due the end of file is a list of the dlls that packed file is used for it's import table and unpacker needs to it for resolving the IAT and we don't have these valid libraries names.  
So we can bypass these instructions. (Like call,lea and any other instructions that throw an exeption in the program).    
I used x64dbg for debug it and patched every instruction that didn't get resolved, and throw INVALID Instruction Execption to a nop instruction.  
![alt text]  
Do this job until arrive at a function at address ```0x4013e6```. step into this function and if continue to debugging will see some encoded chars are going to a function(0x401000).  
And when this function is finished, we see a valid string. so we can assume that this function is the decoder.  
Continue debugging and bypass every instruction that throw exeption and see another call to ```0x401000```. step over and a ```MsgBox``` string appears.  
We will see the flag in it.  



