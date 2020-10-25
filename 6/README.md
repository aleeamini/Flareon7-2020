# 6-codeit  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/sprite.bmp)  
At first glance it is a UPX packed exe file. Unpack it with UPX and we see that file doesn't run.  
This is a trick for Anti-unpacking. The malware author used some Hardcoded address in the malware code which if you unpack the malware, the unpacked version overwrites those addresses  
and the unpacked malware doesn't run.
## Fisrt Section:  
The file is packed with UPX but it is not a regular exe file. If we look at its strings we see ```AutoIt``` string.  
AutoIt v3 is a freeware BASIC-like scripting language designed for automating the Windows GUI and general scripting.  
You can write your GUI script in AutoIt and convert it to an Exe file. also the Autoit software has a option for packing the exe with upx. So here we have a script that converted to a packet exe file.  
The executable file is just a loader of that script. It is like ```Pyinstaller``` that runs the python scripts as exe files.  
We can use some tools for extract the main AutoIt script from the exe file. I used ```Exe2Aut```. This is a simple exe file and you should drop the exe file in it and it shows you the script.  
After that save the script file. Now we have a big problem. :( the script is obfuscated heavily. So we must deobfuscate it to understand what happens.  
There is not any automated tools for deobfuscate it and you have to get your hands dirty :D.  
## Second Section:  

There is two type of obfuscation in this script. If you look at the file, you see many junk variables that filled with ```Number()``` function. This function converts a char number to an intiger value, and after that the script used these junk value in its functions parameters. So we have to convert this hunk variables to their int values.  
I wrote a ```Regex``` script to replace them with their values, and run this ```Regex``` in the ```Notepad++``` find and replace menu.  
I used a special format of ```Regex```, ```Dictionary Regex```. I make a dict from those junk variables, with their value and use it in my regex query.  
This is Regex1 query and it is for replacing the junk variables with their numbers.  
Before run this query, remove all junk variables from the script:  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/remove_junks.png)  
  
  
### Regex1: ```(?sx)\b(\w+)\b(?=.*:\1=(\w+)\b)```  
While you are using this query for replacing the junk variabls, you must put the dictionary text at the end of your script file. The ```Dict1.txt``` file contains a dictionary of junk variables and their values.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/run_regex1.png)   

Now we have this after runing ```Regex1```  

![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/after_run_regex1.png)  
As you see there is no junk variables in functions arguments and you should remove the junk variables from script. but we need a little cleaning. You see the ```$``` sign before numbers that must remove.  

### Regex2: ```\$([0-9])``` for remove all $ sign from before the numbers.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/after_regex2.png)  
## Third Section:  
There is another obfuscation that you can see in ```areihnvapwn()``` function. This function splits a long byte array and write it in ```os``` global variable, And after that other functions call a function(```arehdidxrgk```) and send an index of ```os``` to it and this function, decode that array and sends back to the caller.  
so we should find what are these value.  
For this i wrote a python script that decode these bytes. But we should replace the decoded value with these calls to the ```arehdidxrgk()``` function.  
OK like the previous section i used a regex query. But we should run the python script for decoding and putting its output as a dictionary(like previous section).  
Run the ```deobfuscate.py``` and it gives you a txt file contains a dict format of the decoded value. Copy it and paste at the end of your script and run the third regex query:  
### Regex3: ```(?sx)(arehdidxrgk\(\$os\[.+?\]\))(?=.*:\1= \|([\$,\#,\!,\{,\},\[,\],\;a-z,A-Z,0-9, \\,\/,\.,\-,\(,\),\:,©,*]*))```  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/after_regex3.png)  

Now we have a deobfuscated code, and now we could find what happend in the script.  
I short the story. The script gets a string from the user and does some calculation on it and make a QR code. But there is a function that i named it ```Get_ComputerName()```  
```
Func Get_ComputerName()
	Local $result = -1
	Local $locvar = DllStructCreate("struct;dword;char[1024];endstruct")
	DllStructSetData($locvar, 1, 1024)
	Local $locvar2 = DllCall("kernel32.dll", "int", "GetComputerNameA", "ptr", DllStructGetPtr($locvar, 2), "ptr", DllStructGetPtr($locvar, 1))
	If $locvar2[0] <> 0 Then
		$result = BinaryMid(DllStructGetData($locvar, 2), 1, DllStructGetData($locvar, 1))
	EndIf
	Return $result
EndFunc
```  
This function gets the computer name and after that the compyter name string is sends to another function that does some Xor. ```aregtfdcyni()```  
```
For $i = 1 To DllStructGetSize($arg1)
					Local $varloc6 = Number(DllStructGetData($arg1, 1, $i))
					For $j = 6 To 0 Step -1
						$varloc6 += BitShift(BitAND(Number(DllStructGetData($varloc5, 2, $varloc4)), 1), -1 * $j)
						$varloc4 += 1
					Next
					$varloc7 &= Chr(BitShift($varloc6, 1) + BitShift(BitAND($varloc6, 1), -7))
				Next```  
In this function in the nested loop, we see a ```local6``` that is ```Number(DllStructGetData($arg1, 1, $i))```. If you debug the code you see this is the computer name strings.  But after this, we see a value shifted ```$varloc6 += BitShift(BitAND(Number(DllStructGetData($varloc5, 2, $varloc4)), 1), -1 * $j)``` . This is a interting value. For find what is this value we should set the ```local6``` to 0.  

```For $i = 1 To DllStructGetSize($arg1)
					Local $varloc6 = 0
					For $j = 6 To 0 Step -1
						$varloc6 += BitShift(BitAND(Number(DllStructGetData($varloc5, 2, $varloc4)), 1), -1 * $j)
						$varloc4 += 1
					Next
          ConsoleWrite(Hex($varloc6) & @CRLF) 
					$varloc7 &= Chr(BitShift($varloc6, 1) + BitShift(BitAND($varloc6, 1), -7))
				Next```  
        
Now run the script in autoit and we see the string ```aut01tfan1999``` is printed. Now we should change the computername to this value and restart the windows and run the codeit.exe and it gives us a QRcode, scan it in an online qr decoder and it gives you the flag.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/6/finalFlag.bmp)  

Flag is: ```L00ks_L1k3_Y0u_D1dnt_Run_Aut0_Tim3_0n_Th1s_0ne!@flare-on.com```

