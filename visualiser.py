from audioobject import AudioObject
import numpy as np
from PIL import Image
import cv2


class AudioVisualizer:
    """Takes waveform spectrum data (specifically FFT data returned from scipy.fftpack and displays
    this data in a graphical way. If using my AudioObject class to get the data, your instance can
    be passed to this class during instancing and set related attributes accordingly. Mainly the
    audio sample rate and chunk size which are needed for certain calculations. Otherwise these
    attributes must be set manually"""
    def __init__(self, style=1, audio_object=None):
        self.display_size_y = 200
        self.display_size_x = 80
        self.display_zoom = 3
        self.rate = audio_object.RATE if audio_object is not None else 44100
        self.chunk_size = audio_object.CHUNK if audio_object is not None else 4096
        self.cursor_size = 0
        self.freq_bands = [50, 100, 250, 500, 750, 1000, 2000]     # user requested frequency bands
        self.total_bands = len(self.freq_bands)
        self.bands = []                                             # band positions in FFT data
        self.set_freq_bands(self.freq_bands)
        self.style = style

    def set_freq_bands(self, freq_bands):
        """Takes in a list of frequencies and calculates their positions in the FFT data.
        Sets class attributes accordingly"""
        final_bands = []
        for band in freq_bands:
            percentage = (band / self.rate)
            converted_band = self.chunk_size * percentage
            final_bands.append(int(converted_band))
        self.bands = final_bands
        self.total_bands = len(final_bands)
        self.cursor_size = self.display_size_y // (self.total_bands + 1)
        return final_bands

    def draw_vis(self, spec_data):
        if self.style == 1:
            self.draw_style_1(spec_data)
        else:
            print("you need to specify a valid draw style")
            raise ValueError

    def draw_style_1(self, data):
        display_cursor = 0
        display_image = np.zeros((self.display_size_x, self.display_size_y))
        band_index = 0
        while display_cursor < self.display_size_y and band_index <= self.total_bands:
            start_band = 0 if band_index == 0 else self.bands[band_index - 1]
            end_band = self.bands[band_index] if band_index < self.total_bands else len(data) - 1
            band_values = [val for val in data[start_band:end_band]]
            cursor_value = max(band_values)
            if cursor_value < 1:
                cursor_value = 1
            else:
                cursor_value = int(cursor_value)

            display_image[-cursor_value:-1, display_cursor:display_cursor + self.cursor_size] = 255.0
            display_cursor += self.cursor_size
            band_index += 1
        output_image = Image.fromarray(display_image.astype(np.uint8), "L")
        output_image = output_image.resize((self.display_size_y * self.display_zoom,
                                            self.display_size_x * self.display_zoom))
        output_image = np.array(output_image)
        cv2.imshow("output", output_image)
        cv2.waitKey(1)


if __name__ == "__main__":
    # audio = AudioObject(filename="freq_test.opus", create_plot=False)
    audio = AudioObject(create_plot=False)
    visualizer = AudioVisualizer(style=1, audio_object=audio)
    while not audio.file_finished:
        audio_data = audio.get_next_chunk()
        if not audio.file_finished:
            audio.process_data(audio_data)
        spectrum_data = audio.spectrum_data[:len(audio.spectrum_data) // 2]
        visualizer.draw_vis(spectrum_data)
