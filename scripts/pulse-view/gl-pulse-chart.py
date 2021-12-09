# import asyncio
from collections import deque
import sys
import time
import threading

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server


trace = None

X = np.linspace(0, 100, num=100)
Y = np.sin(X*10)
Z = np.linspace(0, 0, num=100)
pts = np.vstack((X, Y, Z)).T

BUF_LEN = 100
buffer = deque([0]*BUF_LEN, BUF_LEN)


def update():
    print('update')
    global trace

    pts[:, 1] = np.sin(X + 2*time.time())
    trace.setData(pos=pts, color=(0,1,0,1), width=8)


def main():
    global trace
    app = QtGui.QApplication(sys.argv)
    w = gl.GLViewWidget()
    w.opts['distance'] = 10
    w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
    w.setGeometry(0, 0, 800, 600)
    w.resize(800, 600)
    pg.setConfigOptions(antialias=True)

    trace = gl.GLLinePlotItem(
        pos=pts,
        color=(0,1,0,1),
        width=3,
        antialias=True
    )

    w.addItem(trace)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(10)
    QtGui.QApplication.instance().exec_()


def pulse_handler(addr, val):
    buffer.append(val)
    print(val)
    # plot()


def osc_boot_main():
    dispatcher = Dispatcher()
    dispatcher.map("/pulse", pulse_handler)
    server = osc_server.ThreadingOSCUDPServer( ('0.0.0.0', 37339), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()


if __name__ == '__main__':
    osc_boot_main()
    main()
