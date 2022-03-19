#!/usr/bin/env python

import time

import mido
from pythonosc import udp_client

host = 'localhost'
port = 37339

HOSTS = [
    '10.0.0.109',
    '10.0.0.105'
]

CLIENTS = [udp_client.SimpleUDPClient(host, port, allow_broadcast=True) for host in HOSTS]

PORTS = [
    'IAC Driver IAC Bus 2',
    'nanoKONTROL SLIDER/KNOB'
]

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


def send_message(*args):
    for client in CLIENTS:
        client.send_message(*args)


def send_button(message: mido.Message):
    i = message.control - 23
    x = (i % 5) + 1
    y = i // 5
    send_message(f"/mode/{x}/{y}", 1.0)


def send_slider(message: mido.Message):
    param = sliders[message.control]
    send_message(f"/hydra/{param}", message.value / 127.0)


def send_note_on(message: mido.Message):
    send_message("/midi/note", [message.channel, message.note, message.velocity])


def send_knob(message: mido.Message):
    i = message.control - 23
    x = (i % 5) + 1
    y = i // 5
    send_message(f"/mode/{x}/{y}", 1.0)


def handle(message: mido.Message):
    print(message)
    if message.type == 'sysex':
        return

    if message.type == 'control_change' and message.channel == 0:  # nanokontrol
        if message.control in buttons:
            send_button(message)

        elif message.control in sliders:
            send_slider(message)

        elif message.control in knobs:
            send_knob(message)

    if message.type == 'note_on':
        send_note_on(message)


if __name__ == '__main__':
    ports = [mido.open_input(p, callback=handle) for p in PORTS]

    time.sleep(10**6)