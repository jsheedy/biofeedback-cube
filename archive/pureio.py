from Adafruit_PureIO.smbus import SMBus
import struct
import time

from utils import bytes_to_str

HEART_ADDR = 0x09

bus = SMBus(1)

estimated_value = 127
errors = []
n = 0
bus.write_bytes(HEART_ADDR, b'\x7f\x00')
time.sleep(.1)

for n in range(2**32):
    raw_data = bus.read_bytes(HEART_ADDR, 2)

    val = struct.unpack('h', raw_data)[0]
    s = bytes_to_str(raw_data[0], raw_data[1])
    print(s + " | " + str(val) + " | " + str(estimated_value) + " [ " + str(len(errors)) + " / " + str(n) + " ]" + str(errors))
    if estimated_value != val:
        errors.append(estimated_value)
    estimated_value += 1
    if estimated_value == 1024:
        estimated_value = 0
    # data = bus.read_word_data(HEART_ADDR, 1)
    # input('press a key')
    time.sleep(.03)  # timing here is super sensitive

