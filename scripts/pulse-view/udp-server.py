import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 37340

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
while True:
    for i in range(0,256):
        MESSAGE = bytes([i])
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        time.sleep(.1)
