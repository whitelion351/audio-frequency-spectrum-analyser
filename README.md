# audio-frequency-spectrum-analyser
Read audio from file or sound card input and display waveform and FFT

Based on a tutorial by Youtube user Mark Jay. Credit goes to him for the original code.

I made some modifications, bundled it up into a class and added the ability to take in any audio file that your operating system is capable of playing. I stuck with using matplotlib instead of PyQTGraph just to keeps things a little simpler and so that everything needed is installable with pip.

# requirements
- pip install pyaudio

if on linux you will also need to install the portaudiov19-dev package with apt or apt-get

- pip install matplotlib
- pip install numpy
- pip install audioread

if running this module as the main file in your project there is some example code at the bottom.
