# 6-codeit  

At first glance it is a UPX packed exe file. Unpack it with UPX and we see that file doesn't run.  
This is a trick for Anti-unpacking. The malware author used some Hardcoded address in the malware code which if you unpack the malware, the unpacked version overwrite those addresses  
and the unpacked malware doesn't run.
## Fisrt Section:  
the file is packed with UPX but it is not a regular exe file. if we look at it's strings we see ```AutoIt``` string.  
AutoIt v3 is a freeware BASIC-like scripting language designed for automating the Windows GUI and general scripting.  
You can write your GUI script in AutoIt and convert it to an Exe file. also the Autoit software has a option for packing the exe with upx. so here we have a script that converted  
to a packet exe file.  
the executable file is just a loader of that script. it is like ```Pyinstaller``` that runs the python scripts as a exe file.  
We can use some tools for extract the main AutoIt script from the exe file. I used from ```Exe2Aut```. this is a simple exe file and you should drop the exe file in it and it shows you the script.  
After that save the script file. Now we have a big problem. :( the script is obfuscated heavily. so we must deobfuscate it to understand what happens.  
There is not any automate tools for deobfuscate it and you have to get your hands dirty :D.  
## Second Section:  

there is two type of obfuscation in this script. if you look at the file, you see many junk variables that filled with ```Number()``` function. this function converts a char number to a intiger value.  
and after that the script used these junk value in it's functions parameters. so we have to convert this hunk variables to their int values.  
I wrote a ```Regex``` script for replace them with their values, and run this ```Regex``` in the ```Notepad++``` find and replace menu.  
I used from a special format of ```Regex```, ```Dictionary Regex```. i make a dict from those junk variables,, with their value and use it in my regex query.  
This is Regex1 query and it is for replacing the junk variables with their numbers. before run this query, remove all junk variables from the script:  
![alt text](remove_junks)  
  
  
```(?sx)\b(\w+)\b(?=.*:\1=(\w+)\b)```  
while you are using this query for replacing the junk variabls, you must put the dictionary text at the end of your script file. the ```Dict1.txt``` file contains a dictionary of junk variables and their values. 
![alt text](run_regex1)  

Now we have this after runing ```Regex1```  

![alt text](after_run_regex1)  
as you see there is no junk variables in functions arguments and you should remove the junk variables from script. but we need a little cleaning. You see the ```$``` sign before numbers that must remove.

Regex2: ```\$([0-9]\])``` for remove all $ sign from before the numbers.  

## Third Section:  
there is another obfuscation that you can see in ```areihnvapwn()``` function. this function split a long byte array and write it in ```os``` global variable. and after that other functions calls a function(```arehdidxrgk```) and send an index of ```os``` to  
it and the this function, decode that array and sends back to the caller. so we should find what is these value.  
For this i wrote a python script that decode these bytes. but we should replace the decoded value with these calls to the ```arehdidxrgk()``` function.  
OK like the previous section i used a regex query. but we should run the pyhton script for decoding and put it's output as a dictionary(like previous section).  
Run the ```deobfuscate.py``` and it gives you a txt file contains a dict format of decoded value. copy it and paste at the end of your script and run the third regex query:  
Regex3: ```(?sx)(arehdidxrgk\(\$os\[.+?\]\))(?=.*:\1= \|([\$,\#,\!,\{,\},\[,\],\;a-z,A-Z,0-9, \\,\/,\.,\-,\(,\),\:,©,*]*))```  
![alt text](after_run_regex3)  

now we have a deobfuscated code. and now we could find what happend in the script.  
