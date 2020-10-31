# 1-Fidler
## First Part:
this is very simple.
When you run the fidler.exe file, it shows a password box. the password checker function is a simple function.  copy the ```password_check()``` in a new file and run it with python and print the 'key' value: "ghost".    
```python
def password_check(input):
    altered_key = 'hiptu'
    key = ''.join([chr(ord(x) - 1) for x in altered_key])
    print(key)
    return input == key

password_check("alee")
```

![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/1/pass.png)  

## Second phase:
We should earn 200000000000 coins from this game. evey time we click on the cat, it gives us one coin. so we should click on the cat 200000000000 times. :D  
If you look at the fidler.py code you see a function: ```cat_clicked()``` that increases coin at every run one time.  
so we should just change the 1 to 100000000000 and save the file.  
![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/1/change_counter.png)  
but for running the game we can't use the fidler.exe because it is a compiled exe python file. but we can install "pygame" package to run the game as a py file.  
so after running the changed fidler.py and clicking on the cat two times we have the flag.  

![alt text](https://github.com/aleeamini/Flareon7-2020/blob/main/1/flag.PNG)  


