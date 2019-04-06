# biofeedback-cube

## installation

installed on raspbian jesse: https://www.raspberrypi.org/downloads/raspbian/

Dotstar LED interface requires https://github.com/adafruit/Adafruit_DotStar_Pi (now deprecated)
It required patching for Python 3 via this thread:
https://github.com/adafruit/Adafruit_DotStar_Pi/issues/24#issuecomment-427452758

Development on Adafruit_DotStar_Pi moved to https://github.com/adafruit/Adafruit_CircuitPython_DotStar
Moving to this requires supporting [CircuitPython on rpi](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/circuitpython-raspi)

Numpy/scikit requirements are supplied by [BerryConda 3](https://github.com/jjhelmus/berryconda)
Install that, then

```
conda install conda-build
conda develop .
```

This should result in a `cube` command.  Install the systemd service with appropriate paths following `systemd/` and it should start on boot up. Set any environment variables in /etc/cube_environment. Logs at `sudo journalctl -u cube `

