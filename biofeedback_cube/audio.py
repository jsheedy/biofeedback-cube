import sounddevice as sd
import soundfile as sf


def main():
    fname = '/home/pi/Downloads/Shpongle - Nothing Is Something Worth Doing-2tVs_R8-WT0.wav'
    data, fs = sf.read(fname, dtype='float32')
    # sd.default.samplerate = fs
    sd.play(data, fs, device='default')
    status = sd.wait()
    print(status)
    # python3 -m sounddevice
    # sd.default.device = 'digital output'

    # sd.play(myarray)
    # sd.stop()


if __name__ == '__main__':
    main()
