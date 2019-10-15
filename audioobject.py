import struct
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from tkinter import TclError
import audioread


class AudioObject:
    # noinspection SpellCheckingInspection
    def __init__(self, filename=None, chunk=2048 * 2, audio_format=pyaudio.paInt16, channels=1, rate=44100):
        # constants
        self.CHUNK = chunk             # samples per frame
        self.FORMAT = audio_format     # audio format (bytes per sample?)
        self.CHANNELS = channels       # single channel for microphone
        self.RATE = rate               # samples per second
        self.fig = None
        self.fig_size = (8, 6)
        self.ax1 = None
        self.ax2 = None
        self.filename = filename
        self.file_finished = False

        if self.filename is None:
            # pyaudio class instance
            live_audio = pyaudio.PyAudio()

            # stream object to get data from microphone
            self.live_stream = live_audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=False,
                frames_per_buffer=self.CHUNK
            )
        else:
            self.file_stream = []
            with audioread.audio_open(self.filename) as f:
                self.CHANNELS = f.channels
                self.RATE = f.samplerate
                print("using file {} channels={}, samplerate={}, duration={} second(s)".format(
                    self.filename, f.channels, f.samplerate, round(f.duration, 1))
                )
                for buf in f:
                    self.file_stream.append(buf)
            self.file_data = self.file_data_reader()

        print('stream started')

        # create matplotlib figure and axes
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, figsize=self.fig_size)

        # variable for plotting
        x = np.arange(0, self.CHUNK, 1)
        xf = np.linspace(0, self.RATE, self.CHUNK)     # frequencies (spectrum)

        # create a line object with random data
        self.ax1_line, = self.ax1.plot(x, np.random.rand(self.CHUNK), '-', lw=2)

        # create semilogx line for spectrum
        self.ax2_line, = self.ax2.semilogx(xf, np.random.rand(self.CHUNK), '-', lw=2)

        # formatting waveform axes
        self.ax1.set_title('AUDIO WAVEFORM')
        self.ax1.set_xlabel('samples')
        self.ax1.set_ylabel('volume')
        self.ax1.set_ylim(-40000, 40000)
        self.ax1.set_xlim(0, self.CHUNK)
        plt.setp(self.ax1, xticks=np.linspace(0, self.CHUNK, 5), yticks=np.linspace(-40000, 40000, 7))

        # format spectrum axes
        self.ax2.set_ylim(0, 80)
        self.ax2.set_xlim(10, int(self.RATE / 2))

        # show the plot
        plt.show(block=False)

        print('plot started')

    def file_data_reader(self):
        for i in self.file_stream:
            yield i
        return None

    def get_next_chunk(self):
        if self.filename is None:
            data = self.live_stream.read(self.CHUNK)
        else:
            data = bytes()
            while not self.file_finished and len(data) < self.CHUNK * 2:
                try:
                    data += next(self.file_data)
                except StopIteration:
                    self.file_finished = True
                    print("reached end of file")
        return data

    def populate_graph(self, data):
        # convert data to integers
        data_np = struct.unpack(str(self.CHUNK) + 'h', data)
        self.ax1_line.set_ydata(data_np)

        # compute FFT and update line
        yf = fft(data_np)
        self.ax2_line.set_ydata(np.abs(yf) / (128 * self.CHUNK))

    def redraw_graph(self):
        # update figure canvas
        try:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        except TclError:
            print("graph windows closed")
            exit()


if __name__ == "__main__":
    audio = AudioObject()
    # audio = AudioObject(filename="freq_test.opus")
    while True:
        audio_data = audio.get_next_chunk()
        if audio_data is None or audio.file_finished or len(audio_data) < audio.CHUNK * 2:
            print("out of audio data")
            plt.show(block=True)
            break
        audio.populate_graph(audio_data)
        audio.redraw_graph()
