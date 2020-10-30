# 2-garbage
## First Section:
When we run the exe file, we see an error message from windows, that this file is invalid or something else.  
When we open file in a hex-editor, at the end of file we see that the ```Manifest.xml``` which windows uses to run the program, is corrupted.  
The file is packed with UPX. So I tried to unpack it with ```UPX3.96``` , but it said that file is corrupted. I thought it is due to corrupted Manifest.    
I used a valid exe file and tried to copy it's ```Manifest.xml``` to ```garbage.exe``` file.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/2/manifest-patched.png)  

## Second Section:  
Ok now we have a valid file. But when we run it, it seems that it doesn't run correctly. So let's unpack it. But ```UPX``` still says that file is incorrect.  
Now we have to unpack it manually. The unpacker stub is a long jump at ```0x0041891C```. But when we start debugging it in the debugger, at some calls and lea or mov instructions, the program crashes.  
It is because it can't resolve some addresses due the end of file is a list of dlls that unpacker is used for reconstruct import table and unpacker needs to it for resolving the IAT and we don't have these valid libraries names.    
So we can bypass these instructions. (Like call, lea and any other instructions that throw an exception in the program).    
I used x64dbg to debug it and patched every instructions that didn't get resolved and throw INVALID Instruction Exception, with nop instruction.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/2/invalid-addr.png)  
We should repeat this until we arrive at a function at address ```0x4013e6```. if we step into this function continue debugging will see some encoded chars are going to a function(0x401000).  
And when this function is finished, we see a valid string. so we can assume that this function is the decoder.  
Continue debugging and bypass every instruction that throw exception and see another call to ```0x401000```.  Step over and a ```MsgBox``` string appears.  
We will see the flag in it.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/2/flag.png)  


### ```Flag:C0rruptGarbag3@flare-on.com```
