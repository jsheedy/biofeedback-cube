#!/usr/bin/env python

import itertools
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

client = udp_client.SimpleUDPClient('localhost', 37339)

vals = itertools.chain(range(300,600,5), range(600,300,-5))

for i in vals:
	# msg = osc_message_builder.OscMessageBuilder(address='/pulse')
	# msg.add_arg(i)
	# client.send(msg.build())
	client.send_message("/pulse", i)
	print(i)
	time.sleep(0.100)

