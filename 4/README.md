# 4-report  
## First Section:
This is a VisualBasic Macro that sored in a excel file.  
When opening the vbs script in VisaulBasic, I see it has a form(F) which stores two long strings value in a textbox and a label object.  
Also the script has a ```Sheet1``` file that in it, is the code of the malware.  
The start function is ```Sheet1.folderol```. this function is the main function and at the first uses ```Split()``` to split the ```F.L```(Label of the main Form), and save in  
```onzo``` array and after that sends this array to ```rigmarole()```.  
I decided to run the script and debug it. But there is some problems that cause script doesn't run.  
The VB debugger get stuck at the declaring the API functions. so i removed these declarations from up of code and also every API calls in the code, just for debugging.  
After debugging, we have these decoded values:  
```onzo(0):"AppData"
onzo(1):"\Microsoft\stomp.mp3"
onzo(2):"play"
onzo(3):"FLARE-ON"
onzo(4):"Sorry This machine doesnt support"
onzo(5):"FLARE-ON"
onzo(6):"Error"
onzo(7):"winmgmts:\\.\root\CIMV2"
onzo(8):"SELECT Name FROM Win32_Process"
onzo(9):"vbox"
onzo(10):"WScript.Network"
onzo(11):"\Microsoft\v.png"
```
The script has a mechanism for detecting VirrtualMachine. it runs the ```SELECT Name FROM Win32_Process``` query to get the machine processor and search in it, the ```vmw,wmt``` strings.  
## Second Section:
After checking the VM and InternetConection, now the script sends the textbox's string (```F.T```) to ```canoodle()``` function and after that writes the output in a file in ```AppData\Microsoft\stomp.mp3```.  
Continue debugging to find what is this mp3 file?  
The ```canoodle()``` is a decoder. it takes a buffer of encoded bytes and xor them with ```xertz``` array and returns the result.  
The mp3 file is a dummy file. and there isn't any useful info. But I saw in ```onzo(11)``` a png filename ```v.png``` so I guessed that there is another encoded file.  
If you look at the ```F.T``` string, it's length is 1142916 bytes, while the script just sends 168667 bytes of it in the ```canoodle()``` function. So the rest of the bytes is another file.  
## Third Section:
If we look at ```canoodle()``` function, it iterates over the ```F.T``` and does some calculation for select one byte from the string and xor it with one of element of the ```xertz``` array. but there is a significant command. the loop incremented by 4 and start at 1. in this case one byte is left out. so the png file's bytes is between the mp3's bytes.  
ok until now we found that the bytes of png file start at index 2 and our step should be 4 (for left out the mp3 bytes. so the loop start with 3). but there is another problem.  the data is xored with an array(```xertz```) and we should find correct array for png file?  
OK at this moment I used a png file and look at the it's header. so we have the header of png file and also the encoded data of the header in the ```F.T``` so we just find the key with xoring the encoded data and the header bytes.
```89 50 4E 47 0D 0A 1A 0A``` : PNG header
XOR With:
```c7 1f 63 02 5f 4b 56 4c``` : 8 first bytes of F.T (the mp3's bytes is left out)

KEY= ```4E 4F 2D 45 52 41 4C 46```

replace the new KEY in ```xertz``` array and change the start of loop in ```canoodle()``` to 3 and run the script and you see the png file. if you don't change the size of the file from 168667 to a bigger number, the png is imperfect. you could change this value until you see the complete png.  
The final script is in ```final-script.txt``` file.      
```VB
Function rigmarole(es As String) As String
    Dim furphy As String
    Dim c As Integer
    Dim s As String
    Dim cc As Integer
    furphy = ""
    For i = 1 To Len(es) Step 4
        c = CDec("&H" & Mid(es, i, 2))
        s = CDec("&H" & Mid(es, i + 2, 2))
        cc = c - s
        furphy = furphy + Chr(cc)
    Next i
    rigmarole = furphy
End Function

Function folderol()
    Dim wabbit() As Byte
    Dim fn As Integer: fn = FreeFile
    Dim onzo() As String
    Dim mf As String
    Dim xertz As Variant
    
    onzo = Split(F.L, ".")
    Set fudgel = GetObject(rigmarole(onzo(7)))
    Set twattling = fudgel.ExecQuery(rigmarole(onzo(8)), , 48)
    For Each p In twattling
        Dim pos As Integer
        pos = InStr(LCase(p.Name), "vmw") + InStr(LCase(p.Name), "vmt") + InStr(LCase(p.Name), rigmarole(onzo(9)))
        If pos > 0 Then
            MsgBox rigmarole(onzo(4)), vbCritical, rigmarole(onzo(6))
            End
        End If
    Next
        
    'xertz = Array(&H11, &H22, &H33, &H44, &H55, &H66, &H77, &H88, &H99, &HAA, &HBB, &HCC, &HDD, &HEE)
    xertz = Array(&H4E, &H4F, &H2D, &H45, &H52, &H41, &H4C, &H46)
    wabbit = canoodle(F.T.Text, 0, 168667, xertz)
    mf = Environ(rigmarole(onzo(0))) & rigmarole(onzo(11))
    Open mf For Binary Lock Read Write As #fn
      Put #fn, , wabbit
    Close #fn
    
    
    
End Function

Function canoodle(panjandrum As String, ardylo As Long, s As Long, bibble As Variant) As Byte()
    Dim quean As Long
    Dim cattywampus As Long
    Dim kerfuffle() As Byte
    Dim subs As String
    Dim bb As Byte
    Dim upbi As Long
    Dim modq As Long
    ReDim kerfuffle(s)
    quean = 0
    Dim L As Long
    L = Len(panjandrum)
    For cattywampus = 3 To L Step 4 
        subs = Mid(panjandrum, cattywampus + ardylo, 2)
        bb = CByte("&H" & subs)
        modq = quean Mod (UBound(bibble) + 1)
        upbi = bibble(modq)
        bb = bb Xor upbi
        quean = quean + 1
        kerfuffle(quean) = bb
        If quean = UBound(kerfuffle) Then
            Exit For
        End If
    Next cattywampus
    canoodle = kerfuffle
End Function
```
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/4/v.png)  

### ```Flag:thi5_cou1d_h4v3_b33n_b4d@flare-on.com```
