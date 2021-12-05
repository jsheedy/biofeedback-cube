import alsaaudio
import sounddevice as sd
import soundfile as sf


def set_gain(val):
    m = alsaaudio.Mixer('PCM')
    m.setvolume(int(val * 100))


def play_sample(fname):
    data, fs = sf.read(fname, dtype='float32')
    sd.play(data, fs, device='default')
    status = sd.wait()
    # sd.default.samplerate = fs
    # python3 -m sounddevice
    # sd.default.device = 'digital output'
    # sd.play(myarray)
    # sd.stop()


def main():
    fname = '/home/pi/Downloads/Shpongle - Nothing Is Something Worth Doing-2tVs_R8-WT0.wav'
    play_sample(fname)


if __name__ == '__main__':
    main()
