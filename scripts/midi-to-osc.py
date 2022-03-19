#!/usr/bin/env python

import mido
from pythonosc import udp_client

host = 'localhost'
# host = '10.0.0.105'
port = 37339
client = udp_client.SimpleUDPClient(host, port, allow_broadcast=True)

s = 'IAC Driver IAC Bus 2'
# s = 'nanoKONTROL SLIDER/KNOB'

print(f'opening {s}')

buttons = [
    23, 24, 25, 26, 27, 28, 29, 30, 31,
    33, 34, 35, 36, 37, 38, 39, 40, 41
]

sliders = {
    2: 'a',
    3: 'b',
    4: 'c',
    5: 'd',
    6: 'e',
    8: 'f',
    9: 'g',
    12: 'h',
    13: 'i',
}

knobs = [
    14, 15, 16, 17, 18, 19, 20, 21, 22
]


def send_button(message: mido.Message):
    i = message.control - 23
    x = (i % 5) + 1
    y = i // 5
    client.send_message(f"/mode/{x}/{y}", 1.0)


def send_slider(message: mido.Message):
    param = sliders[message.control]
    client.send_message(f"/hydra/{param}", message.value / 127.0)


def send_note_on(message: mido.Message):
    client.send_message("/midi/note", [message.note, message.velocity])


def send_knob(message: mido.Message):
    i = message.control - 23
    x = (i % 5) + 1
    y = i // 5
    client.send_message(f"/mode/{x}/{y}", 1.0)


def handle(message: mido.Message):
    print(message)
    if message.type == 'sysex':
        return

    if message.type == 'control_change':
        if message.control in buttons:
            send_button(message)

        elif message.control in sliders:
            send_slider(message)

        elif message.control in knobs:
            send_knob(message)

    if message.type == 'note_on':
        send_note_on(message)


with mido.open_input(s) as inport:
    print(f'opened {s}')
    for message in inport:
        handle(message)
