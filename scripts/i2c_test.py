# from smbus import SMBus
# from smbus2_asyncio import SMBusAsyncio
import struct
import time

# from smbus import SMBus
from smbus2 import SMBus

from utils import bytes_to_str


addr = 0x9 # bus address
bus = SMBus(1) # indicates /dev/ic2-1

bus.write_byte(addr, 0)
bus.write_byte(addr, 0)

time.sleep(.1)
estimated_value = 1

while True:
	# data = bus.read_word_data(addr,0)
	data = bus.read_i2c_block_data(addr, 1, 2)

	b1 = bus.read_byte(addr)
	b2 = bus.read_byte(addr)

	# val = struct.unpack('h', b1 + b2)[0]
	val = b2 + (b1 << 8)
	s = bytes_to_str(b1, b2)

	print(s + " | " + str(val) + " | " + str(estimated_value))
	assert(estimated_value == val)
	estimated_value += 1
	# data = bus.read_i2c_block_data(addr, 0, 1)
	time.sleep(.01)

# bus.write_byte(addr, 0x1) # switch it on
# input("Press return to exit")
# bus.write_byte(addr, 0x0) # switch it on





