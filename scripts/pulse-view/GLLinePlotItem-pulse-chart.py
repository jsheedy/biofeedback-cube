# -*- coding: utf-8 -*-
"""
Demonstrate use of GLLinePlotItem to draw cross-sections of a surface.

"""
## Add path to library (just for examples; you do not need this)
import initExample
from collections import deque
import sys
import threading
import time

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.showMaximized()

pos = QtGui.QVector3D(5,0,-4)
distance = 6
azim = -90
elev = 0
w.setCameraPosition(pos, distance, azim, elev)
# w.opts['distance'] = 40
w.orbit(azim, elev)
w.show()
w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

# make XYZ backing grid panels
gx = gl.GLGridItem()
gx.rotate(90, 0, 1, 0)
gx.translate(-10, 0, 0)
w.addItem(gx)
gy = gl.GLGridItem()
gy.rotate(90, 1, 0, 0)
gy.translate(0, -10, 0)
w.addItem(gy)
gz = gl.GLGridItem()
gz.translate(0, 0, -10)
w.addItem(gz)

def fn(x, y):
    return np.cos((x**2 + y**2)**0.5)

n = 51
x = np.linspace(-10,10,100)
y = np.linspace(-10,10,n)
for i in range(n):
    yi = np.array([y[i]]*100)
    d = (x**2 + yi**2)**0.5
    z = 10 * np.cos(d) / (d+1)
    pts = np.vstack([x,yi,z]).transpose()
    plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
    w.addItem(plt)


trace = None

BUF_LEN = 200
X = np.linspace(0, 10, num=BUF_LEN)
Y = np.sin(X*10)
Z = np.linspace(0, 0, num=BUF_LEN)

pts = np.vstack((X, Y, Z)).T

# buffer = deque([0]*BUF_LEN, BUF_LEN)
buffer = np.zeros(BUF_LEN)
i = 0
trace = gl.GLLinePlotItem(
    pos=pts,
    color=(0,1,0,1),
    width=3,
    antialias=True
)
w.addItem(trace)

def update():
    pass

def pulse_handler(addr, val):
    update_buffer(val)

def update_buffer(val):
    global i
    buffer[i] = val

    pts[:, 1] = 6*buffer - 3
    i += 1
    if i >= BUF_LEN:
        i = 0
        buffer[:] = 0
    # buffer.append(val)
    # pts[:, 1] = 6*np.array(buffer) - 3
    trace.setData(pos=pts, color=(0,1,0,1), width=8)

def udp_server():
    import socket

    UDP_IP = "0.0.0.0"
    UDP_PORT = 37340

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP2
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64)

    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1)
        update_buffer(ord(data)/255)

def udp_serve_main():
    thread = threading.Thread(target=udp_server, daemon=True)
    thread.start()

def osc_boot_main():
    dispatcher = Dispatcher()
    dispatcher.map("/pulse", pulse_handler)
    server = osc_server.ThreadingOSCUDPServer( ('0.0.0.0', 37339), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    # timer = QtCore.QTimer()
    # timer.timeout.connect(update)
    # timer.start(50)

    # osc_boot_main()
    udp_serve_main()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
