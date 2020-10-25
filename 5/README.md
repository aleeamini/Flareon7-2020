# 5-TKApp
This is very very simple. Just you don't fooling with it's name.  
The file is a TPK file that is a zip file which contains some dlls that unpack and run under a linux with .NetFramework().like apk files.    
The platform is a popular OS for smart watchs and wearable devices.  You can download the emulator and run the TKAPP in it. the emulater software is ```Tizen```.  But you don't need it for solving this challenge. you could do it with just some static analysis in ```dbSpy```.  
## First Section:  
Unzip the file and we see some dll files. open ```TKApp.dll``` in ```dnspy``` .  
The app at the first asks a password, the password is an encoded value in the app that xor with ```83``` :```mullethat``` is password.  
after that the app collect some info from exif metadata of pictures that included in img directory like lat and long,get the list of ```todo notes``` and the ```steps``` that submitted in the watch  
and does some encryption and decryption.  
there is a function that decrypt a file ```Runtime.dll``` this is the target file.  if the app meets some rules, this file will decryptred.  
What you need to solve this challange is that copy the whole code fron dnspy and copy it to a C# project and run it to find the flag.  
My decryptor program is in ConsoleApp2. just run it. The ```Runtime.dll``` file is a jpg file and flag is in it.  
You need ```ExifLibrary``` to run it.

![alt text]
