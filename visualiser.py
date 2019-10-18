from audioobject import AudioObject
import numpy as np
from PIL import Image
import cv2
import random

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
        self.freq_bands = [40, 100, 200, 350, 550, 800, 1100]     # user requested frequency bands
        self.total_bands = len(self.freq_bands)
        self.bands = []                                             # band positions in FFT data
        self.set_freq_bands(self.freq_bands)
        self.style = style
        self.meter_sensitivity = 5

    def set_freq_bands(self, freq_bands):
        """Takes in a list of frequencies and calculates their positions in the FFT data.
        Sets class attributes accordingly"""
        final_bands = []
        for band in freq_bands:
            if band > self.rate / 2:
                print(band, "is higher than half the sample rate ({})".format(self.rate))
            percentage = (band / self.rate)
            fft_index = self.chunk_size * percentage
            if fft_index - int(fft_index) > 0.5:
                fft_index += 1
            final_bands.append(int(fft_index))
        self.bands = final_bands
        self.total_bands = len(final_bands)
        self.cursor_size = self.display_size_y // (self.total_bands + 1)
        return final_bands

    def draw_vis(self, spec_data):
        if self.style == 1:
            self.draw_style_1(spec_data)
        elif self.style == 2:
            self.draw_style_2(spec_data)
        elif self.style == 3:
            self.draw_style_3(spec_data)
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
            cursor_value = max(band_values) if len(band_values) > 0 else 1
            if cursor_value < 1:
                cursor_value = 1
            else:
                cursor_value = int(self.get_meter_value(cursor_value, self.meter_sensitivity, self.display_size_x))

            display_image[-cursor_value:-1, display_cursor:display_cursor + self.cursor_size] = 255.0
            display_cursor += self.cursor_size
            band_index += 1
        output_image = Image.fromarray(display_image.astype(np.uint8), "L")
        output_image = output_image.resize((self.display_size_y * self.display_zoom,
                                            self.display_size_x * self.display_zoom))
        output_image = np.array(output_image)
        cv2.imshow("output", output_image)
        cv2.waitKey(1)

    def draw_style_2(self, data):
        values = []
        band_index = 0
        while band_index <= self.total_bands:
            start_band = 0 if band_index == 0 else self.bands[band_index - 1]
            end_band = self.bands[band_index] if band_index < self.total_bands else len(data) - 1
            band_values = [val for val in data[start_band:end_band]]
            cursor_value = max(band_values) if len(band_values) > 0 else 1
            if cursor_value < 1:
                cursor_value = 1
            else:
                cursor_value = int(self.get_meter_value(cursor_value, self.meter_sensitivity, 70))
            values.append(cursor_value)
            band_index += 1

        bar_angle = 360 / len(values)
        angle = 0
        display_np = np.zeros((200, 200))
        for v in values:
            bar = np.zeros((200, 200))
            if v != 1:
                v = (v + 130) * -1
                bar[v:-130, 85:115] = 225.0
            else:
                bar[-135:-130, 85:115] = 225.0
            if angle > 0:
                bar = np.array(Image.fromarray(bar).rotate(angle=angle, center=(100, 100)))
            display_np += bar
            angle += bar_angle
        display_np = display_np.clip(0.0, 255.0)
        cv2.imshow("output", display_np)
        cv2.waitKey(1)

    def draw_style_3(self, data):
        left_arm_lower = np.zeros((21, 11))
        left_arm_lower[10:, -1] = 255.0
        left_arm_lower = Image.fromarray(left_arm_lower)

        right_arm_lower = np.zeros((21, 11))
        right_arm_lower[10:, 0] = 255.0
        right_arm_lower = Image.fromarray(right_arm_lower)

        left_leg_upper = np.zeros((11, 11))
        left_leg_upper[:, -1] = 255.0
        left_leg_upper = Image.fromarray(left_leg_upper)

        right_leg_upper = np.zeros((11, 11))
        right_leg_upper[:, 0] = 255.0
        right_leg_upper = Image.fromarray(right_leg_upper)

        leg_lower = np.zeros((11, 1))
        leg_lower[:, :] = 255.0

        display_np = np.zeros((50, 50))
        # draw base body
        display_np[10:25, 24] = 255.0
        # hips
        display_np[25, 20:29] = 255.0
        # upper arms
        display_np[15, 10:20] = 255.0
        display_np[15, -21:-11] = 255.0

        # left arm
        band_values = [val for val in data[:self.bands[1]]]
        cursor_value = self.get_meter_value(max(band_values), self.meter_sensitivity, 180)
        if cursor_value > 2:
            cursor_value += random.randrange(int(-cursor_value / 2), int(cursor_value / 2))
        cursor_value = 0 if cursor_value < 0 else cursor_value
        cursor_value = 180 if cursor_value > 180 else cursor_value
        left_arm_lower = left_arm_lower.rotate(-cursor_value, center=(10, 10))
        display_np[5:26, 0:11] += np.array(left_arm_lower)

        # right arm
#        band_values = [val for val in data[self.bands[2]:self.bands[3]]]
        band_values = [val for val in data[:self.bands[1]]]
        cursor_value = self.get_meter_value(max(band_values), self.meter_sensitivity, 180)
        if cursor_value > 2:
            cursor_value += random.randrange(int(-cursor_value / 2), int(cursor_value / 2))
        cursor_value = 0 if cursor_value < 0 else cursor_value
        cursor_value = 180 if cursor_value > 180 else cursor_value
        right_arm_lower = right_arm_lower.rotate(cursor_value, center=(1, 10))
        display_np[5:26, -12:-1] += np.array(right_arm_lower)

        # left leg
        angle_limit = 80
#        band_values = [val for val in data[self.bands[4]:self.bands[5]]]
        band_values = [val for val in data[:self.bands[1]]]
        cursor_value = self.get_meter_value(max(band_values), self.meter_sensitivity, angle_limit)
        if cursor_value > 2:
            cursor_value += random.randrange(int(-cursor_value / 2), int(cursor_value / 2))
        cursor_value = 0 if cursor_value < 0 else cursor_value
        cursor_value = angle_limit if cursor_value > angle_limit else cursor_value
        left_leg_upper = left_leg_upper.rotate(-cursor_value, center=(10, 0))
        left_leg_upper = np.array(left_leg_upper)
        display_np[25:36, 10:21] += left_leg_upper
        l_pos_x = -1
        l_pos_y = -1
        counter = len(left_leg_upper) - 1
        while counter >= 0:
            if sum(left_leg_upper[counter]) > 0:
                l_pos_x = counter
                for iy, y in enumerate(left_leg_upper[counter]):
                    if y > 0:
                        l_pos_y = iy
                        break
                if l_pos_y >= 0:
                    break
            counter -= 1
            if counter == -1:
                print("could not find left leg knee position")
        display_np[25+l_pos_x:25+l_pos_x+11, 10+l_pos_y:10+l_pos_y+1] += leg_lower

        # right leg
        angle_limit = 80
#        band_values = [val for val in data[self.bands[6]:]]
        band_values = [val for val in data[:self.bands[1]]]
        cursor_value = self.get_meter_value(max(band_values), self.meter_sensitivity, angle_limit)
        if cursor_value > 2:
            cursor_value += random.randrange(int(-cursor_value / 2), int(cursor_value / 2))
        cursor_value = 0 if cursor_value < 0 else cursor_value
        cursor_value = angle_limit if cursor_value > angle_limit else cursor_value
        right_leg_upper = right_leg_upper.rotate(cursor_value, center=(1, 0))
        right_leg_upper = np.array(right_leg_upper)
        display_np[25:36, 28:39] += right_leg_upper
        l_pos_x = -1
        l_pos_y = -1
        counter = len(right_leg_upper) - 1
        while counter >= 0:
            if sum(right_leg_upper[counter]) > 0:
                l_pos_x = counter
                for iy, y in enumerate(right_leg_upper[counter]):
                    if y > 0:
                        l_pos_y = iy
                if l_pos_y >= 0:
                    break
            counter -= 1
            if counter == -1:
                print("could not find right leg knee position")
        display_np[25+l_pos_x:25+l_pos_x+11, 28+l_pos_y:28+l_pos_y+1] += leg_lower

        output_image = Image.fromarray(display_np.astype(np.uint8))
        output_image = output_image.resize((len(display_np[0]) * self.display_zoom,
                                            len(display_np) * self.display_zoom))
        cv2.imshow("output", np.array(output_image))
        cv2.waitKey(1)

    @staticmethod
    def get_meter_value(value, sensitivity, limit):
        v = (value * sensitivity) / limit
        v = np.tanh(v)
        v = v * limit
        return v if v < limit else limit


if __name__ == "__main__":
    # audio = AudioObject(filename="freq_test.opus", create_plot=False)
    audio = AudioObject(chunk=2048, create_plot=False)
    visualizer = AudioVisualizer(style=3, audio_object=audio)
    while not audio.file_finished:
        audio_data = audio.get_next_chunk()
        if not audio.file_finished:
            audio.process_data(audio_data)
        spectrum_data = audio.spectrum_data[:len(audio.spectrum_data) // 2]
        visualizer.draw_vis(spectrum_data)
