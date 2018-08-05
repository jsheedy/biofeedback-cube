from datetime import datetime
import struct
import time

from Adafruit_PureIO.smbus import SMBus

from utils import bytes_to_str


HEART_ADDR = 0x09

bus = SMBus(1)

spinners = ("\\","|","/","-")
fname = "heartrate-" + datetime.now().isoformat()[:19] + ".txt"
i = 0

with open(fname, 'w') as f:
	print("collecting heartbeat data . . . ")
	while True:
		raw_data = bus.read_bytes(HEART_ADDR, 2)
		val = struct.unpack('h', raw_data)[0]
		s = bytes_to_str(raw_data[0], raw_data[1])
		# print(s + " | " + str(val))
		f.write(",".join([str(time.time()), str(val)]) + "\n")
		if i % 30 == 0:
			f.flush()
		time.sleep(33/1000)  # timing here is super sensitive

		char = spinners[i%4]
		print('\b'*3 + "["+char+"]",end='',flush=True)
		i += 1

