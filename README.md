# biofeedback-cube
This project began as an immersive cube of side 4 feet in which one would sit while hooked up to a heartrate monitor. 5 walls of the cubes were to be LED panels while the base was constructed of wood and contained a 12" JBL subwoofer and fullrange speakers. The heartbeat signal would modulate all light and sound reaching the user providing an immersive biofeedback loop.

[OSC](https://www.wikiwand.com/en/Open_Sound_Control) is used as a communications protocol between subsystems such as the heartrate monitor, [TouchOSC](https://hexler.net/touchosc), or Ableton Live.

I constructed 3 panels and the initial project has pivoted. Now the main usage is driving one of them which is mounted on a wall in a wood frame, controllable by TouchOSC and Ableton.
## development
While the target platform is a Rasbperry Pi to drive the LEDs, a simulator is included to enable developing on a mac.
```
pip install -e .
cube --simulator
```

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

This should result in a `cube` command.  Install the `systemd/cube.service` service in `/etc/systemd/system`, run `systemctl enable cube` and it should start on boot up.

Set any environment variables in /etc/cube_environment.

Logs at `sudo journalctl -u cube `

## Power
once pixels got enough voltage, rpi started displaying lightning bolt 
for an undervoltage condition and crashing.

Disable USB buspower:
https://stackoverflow.com/questions/59772765/how-to-turn-usb-port-power-on-and-off-in-raspberry-pi-4#:~:text=On%20a%20Raspberry%20PI%203B%2B,1%22%20to%20turn%20power%20on.
sudo sh -c "echo 0 > /sys/devices/platform/soc/3f980000.usb/buspower"
