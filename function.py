PRQ = [0, 1]
WRQ = [0, 2]
DATA = [0, 3]
ACK = [0, 4]
ERROR = [0, 5]
NEG = [0, 6]
file_not_found = [0, 1]
b_zero = bytearray([0])


ERROR_CODES = ["Not defined.", "File not found.", "Access violation.",
               "Disk full or allocation exceeded.",
               "Illegal TFTP operation.", "Unknown transfer ID.",
               "File already exists.", "No such user."]

def block(x):
    return ((x[2] << 8)+x[3])

def b_s(x):
    return bytearray(x.encode())

def opcode(x):
    return [x[0], x[1]]

def error_code(x):
    return ERROR_CODES[x[3]]

def ack_block(i):
    return bytearray(ACK + [i>>8, i &0xFF])

b_16 = b_s("16")