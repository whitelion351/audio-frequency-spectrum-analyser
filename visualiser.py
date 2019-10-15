from audioobject import AudioObject
import numpy as np
from PIL import Image
import cv2

audio = AudioObject(filename="freq_test.opus", create_plot=False)
# audio = AudioObject(create_plot=False)
display_size_y = 200
display_size_x = 80
display_zoom = 1
freq_bands = [50, 200, 500, 1000, 2500, 5000, 12000]

bands = []
for band in freq_bands:
    percentage = (band / audio.RATE)
    converted_band = audio.CHUNK * percentage
    bands.append(int(converted_band))
total_bands = len(bands)
cursor_size = display_size_y // (total_bands + 1)
while audio.file_finished is False:
    audio_data = audio.get_next_chunk()
    if not audio.file_finished:
        audio.process_data(audio_data)
    spectrum_data = audio.spectrum_data[:len(audio.spectrum_data) // 2]
    display_cursor = 0
    display_image = np.zeros((display_size_x, display_size_y))
    band_index = 0
    while display_cursor < display_size_y and band_index <= len(bands):
        start_band = 0 if band_index == 0 else bands[band_index-1]
        end_band = bands[band_index] if band_index < len(bands) else len(spectrum_data)-1
        band_values = [val for val in spectrum_data[start_band:end_band]]
        cursor_value = max(band_values)
        if cursor_value < 1:
            cursor_value = 1
        else:
            cursor_value = int(cursor_value)
        #     cursor_value = int(cursor_value // 2)

        display_image[-cursor_value:-1, display_cursor:display_cursor+cursor_size] = 255.0
        display_cursor += cursor_size
        band_index += 1
    output_image = Image.fromarray(display_image.astype(np.uint8), "L").resize((display_size_y * display_zoom,
                                                                               display_size_x * display_zoom))
    output_image = np.array(output_image)
    cv2.imshow("output", output_image)
    cv2.waitKey(1)
