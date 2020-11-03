import struct
import binascii

def KEYINT(k):
    #k = [0] * 3968
    num = 0x9C40
    for i in range(0, num // 4, 2): #range(0, len(buffer), 2): 
        key = 0x674a1dea4b695809
        for j in range(16):
            k1, k0 = (key & 0xffffffff00000000) >> 32, key & 0xffffffff
            idx = (j * 8 * 32) - j * 8
            k[idx + 7]  = k0
            k[idx + 19] = k1

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
                
def d1(s, len_s):
    c = 0
    for i in range(len_s):
        a = (ord(s[i]) ^ c) & 0xff
        v1 = ida_bytes.get_dword(0x8056960 + 8 * a)
        v2 = ida_bytes.get_dword(0x8056964 + 8 * a)

        c1 = (c >> 8) & 0xffffffff
        c2 = (c & 0xffffffff00000000) >> 32
        c2 = c2 >> 8

        c1 = c1 ^ v1
        c2 = c2 ^ v2
        c = (c2 << 32) | c1

    return c
    
def dec(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(15, -1, -1):
        idx = (j * 8 * 32) - j * 8
        v6 = v1 ^ a4[idx + 19]
        v3 = (v2 + a4[idx + 7]) & 0xffffffff
        v4 = ((v3 >> (a4[idx + 41] & 0x1F)) | (v3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        v6 = v6 ^ v4 
        v1 = v2
        v2 = v6

    data[0] = v2
    data[1] = v1
    
def enc(data,a4):
    
    v1 = data[0]
    v2 = data[1]
    for j in range(16):
        idx = (j * 8 * 32) - j * 8
        v6 = v1 ^ a4[idx + 19]
        v3 = (v2 + a4[idx + 7]) & 0xffffffff
        v4 = ((v3 >> (a4[idx + 41] & 0x1F)) | (v3 << (-(a4[idx + 41] & 0x1F) & 0x1F))) & 0xffffffff
        v6 = v6 ^ v4 
        v1 = v2
        v2 = v6

    data[0] = v2
    data[1] = v1
#crc=0x6dd9e42c2ce616b6 
#crc=0x674a1dea4b695809
key=[0]*3968;
v0 = [0x0260a064,0x7d878aea]
v1 = [ 0xE47CE96C,0x0C2D3F82]
v2 = [ 0xEBB5B78C,0x424F35CF]
v3 = [ 0x492BAD4F,0xE07C2820]


v=[0]*2
f=[0]*10000
se=[0]*8
j=0
KEYINT(key)

for i in range(0,8,2):
    #print(i)
    v[0]=ida_bytes.get_dword(0x081A5100+i*4)
    v[1]=ida_bytes.get_dword(0x081A5100 +(i+1)*4)
    dec(v,key)
    se[j]=v[0]
    se[j+1]=v[1]
    print(hex(v[0]))
    print(hex(v[1]))
    j=j+2
    
fd = open("pass","wb")
for st in se:
    fd.write(struct.pack('<I', st))
fd.close()
'''
for i in range(0,10000,2):
    #print(i)
    v[0]=ida_bytes.get_dword(0x804C640+i*4)
    v[1]=ida_bytes.get_dword(0x804C640 +(i+1)*4)
    enc(v,key)
    f[j]=v[0]
    f[j+1]=v[1]
    j=j+2


fd = open("shellcode","wb")
for st in f:
    fd.write(struct.pack('<I', st))
fd.close()
'''