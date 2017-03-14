#!/usr/bin/env python3
import socket
import sys
import hashlib
from function import *
if len(sys.argv) == 3:
    HOST = sys.argv[1]
    PORT = 69
    file = sys.argv[2]
else:
    HOST = 'localhost'
    PORT = 12345+1
    file =  sys.argv[1]

# path = "/Users/jakubtasiemski/Desktop/Sieci/TFTP/"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.5)

def prq_mess():
    mes = bytearray(PRQ) + b_s(file) +  b_zero + b_s('octet') + b_zero + b_16 + b_zero
    return mes

def md5(i, s):
    md_5 = hashlib.md5()
    for k in range (i):
        md_5.update(s[k])
    return md_5.hexdigest()

def join_file(s, i):
    res = b''
    for k in range(i):
        res += s[k]
    return res

def decode_file_txt(s, i):
    res = ""
    for k in range(i):
        res += str(s[k], 'utf-8')
    return res

def next_bl_t_save(x, i):
    if (block(x) == i):
        i = block(x)+1
        if (i == 2**16):
            i = 0
    return i

prqmss = prq_mess()
i, i2, s, save_file, next_block_to_save, wsize, kill = 1, 0, {}, True, 1, 0, False
send_to = prqmss, (HOST, PORT)
f = open(file, 'wb')
sock.sendto(*send_to)

while True:
    try:
        msg, addr = sock.recvfrom(516)
        if (msg[:2] == bytearray(NEG)):
            wsize = int(str(msg[2:-1], 'utf-8'))
            send_to = bytearray(ACK) + bytearray([0, 0]), addr
            sock.sendto(*send_to)
            break
    except socket.timeout:
        sock.sendto(*send_to)
        continue


while True:
    try:
        msg, addr = sock.recvfrom(516)
    except socket.timeout:
        sock.sendto(*send_to)
        continue
    if opcode(msg) == ERROR:
        save_file = False
        print(error_code(msg))
        break
    if block(msg) == next_block_to_save:
        f.write(msg[4:])
        if (len(msg[4:]) != 512):
            kill = True
            break
        next_block_to_save = next_bl_t_save(msg, next_block_to_save)
        for k in range (wsize-1):
            try:
                msg, addr = sock.recvfrom(516)
                if (next_block_to_save == block(msg)):
                    next_block_to_save = next_bl_t_save(msg, next_block_to_save)
                    f.write(msg[4:])
                    if (len(msg[4:]) != 512):
                        kill = True
                        break
                else:
                    break
            except:
                break
        send_to = (ack_block(next_block_to_save - 1), addr)
        if (kill):
            break
        if (next_block_to_save == 0):
            send_to = (ack_block(2 ** 16 - 1), addr)
        sock.sendto(*send_to)
    else:
        if (block(msg) > next_block_to_save or (next_block_to_save > 2**16 - 16 and block(msg) < 16)):
            sock.sendto(*send_to)