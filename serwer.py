import socket
import sys
import threading
from function import *

if len(sys.argv) == 3:
    PORT = sys.argv[1]
    path_file = sys.argv[2]

else:
    PORT = 12345+1
    path_file = "/Users/jakubtasiemski/Desktop/Sieci/TFTP/testy/"
    path_file = "/Users/jakubtasiemski/Downloads/"

def extract_file_name(x):
    return str(x[2:].split(b'\00')[0], 'utf-8')

class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((host, port))
        self.set = {}

    def run(self):
        while True:
            try:
                msg, addr = self.server.recvfrom(516)
                if msg in self.set:
                    if addr not in self.set[msg]:
                        self.set[msg][addr] = "true"
                        client = Client(msg, addr)
                        client.start()
                else:
                    self.set[msg] = {}
                    self.set[msg][addr] = "true"
                    client = Client(msg, addr)
                    client.start()
            except:
                print(sys.exc_info()[0])
                break
        self.server.close()


class Client(threading.Thread):


    def __init__(self, msg, addr):
        super().__init__(daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 0))
        self.addr = addr
        self.windowsize = self.select_windowszie(msg)
        self.error_code = None
        self.socket.settimeout(0.25)
        self.i = 0
        self.send_to = None
        self.block_number = 1
        self.count = 0
        self.send_to = (bytearray(NEG) + b_s(str(self.windowsize)) + b_zero, self.addr)
        try:
            self.load_file(msg)
            self.filelen = len(self.file)
        except FileNotFoundError:
            self.error_code = file_not_found
        while True:
            try:
                self.socket.sendto(*(self.send_to))
                msg, self.addr = self.socket.recvfrom(516)
                if msg == bytearray(ACK)+bytearray([0, 0]):
                    break
            except:
                pass

    def select_windowszie(self, msg):
        return min(int(str(msg[2:].split(b'\00')[2], 'utf-8')), 16)

    def load_file(self, msg):
        print(path_file+extract_file_name(msg))
        my_file = open(path_file + extract_file_name(msg), "rb")
        self.file = []
        file_read = my_file.read(512)
        while (file_read != b''):
            self.file.append(file_read)
            file_read = my_file.read(512)
        if  (len(self.file[len(self.file)-1])) == 512:
            self.file.append(b'')

    def create_block_message(self, blocknr, i):
        blocknr2 = blocknr
        if (blocknr > 2**16-1):
            blocknr2 -= 2**16
        return bytearray(DATA) + bytearray([blocknr2 >> 8, blocknr2 & 0xFF]) + self.file[blocknr+i-1]

    def run(self):
        while True:
            try:
                if self.count > 5:
                    break
                if self.error_code is None:
                    self.send_to = (self.create_block_message(self.block_number, self.i), self.addr)
                else:
                    self.socket.sendto(bytearray(ERROR) + bytearray(self.error_code), self.addr)
                    break
                for k in range (self.windowsize):
                    if (self.block_number+k+self.i > self.filelen):
                        break
                    self.send_to = (self.create_block_message(self.block_number+k, self.i), self.addr)
                    self.socket.sendto(*(self.send_to))
                    if (len(self.send_to[0]) != 516):
                        break
                while True:
                    try:
                        msg, self.addr = self.socket.recvfrom(516)
                        self.count = 0
                        if (self.block_number < block(msg) and block(msg) < self.block_number + self.windowsize):
                                self.block_number = block(msg)+1
                                if (self.block_number == 2**16):
                                    self.block_number = 0
                                    self.i += 2**16
                                break
                        if (block(msg) < self.windowsize and self.block_number > 2**16-self.windowsize):
                            self.block_number = block(msg)+1
                            self.i += 2**16
                            print((self.block_number + self.i) / self.filelen * 100)
                            break
                        print((self.block_number+self.i)/self.filelen*100)
                    except:
                        self.count += 1
                        break
            except:
                print(sys.exc_info()[0])
        self.socket.close()

server = Server('', PORT)
server.run()