import queue
import threading
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import time
import sys
import io
import adi
from PIL import Image
from bytes_and_bits_skeleton import bits_to_bytes
from bits_and_pam_skeleton import pam_symbols_to_bits
from cosmos import *
from digicomm import *
from detection_skeleton import pam_detect
from common import *

sdr_rx = adi.Pluto("usb:1.1.5")
rx = PlutoReceiver()
rx.set_sdr(sdr_rx)
rx.set_buffer_size(1e6)
rx.set_channel(1)
rx.set_gain_level(80)
rx.desired_transmit_symbols_real = True
bits_per_symbol = int(np.log2(M))
rx.num_transmit_symbols = frames_per_transmission * 3 * width * height * 8 // bits_per_symbol

should_stop_event = threading.Event()
image_queue = queue.Queue()


previous_transmission_times = []
def avg_transmission_time():
    if len(previous_transmission_times) == 0:
        return 2 # generous
    return sum(previous_transmission_times) / len(previous_transmission_times)


# TODO: have a running count of the number of recieved transmission and create an average time
def push_image(image):
    image_queue.put(image)

def recieve_worker():
    while not should_stop_event.is_set():
        try:
            now = time.perf_counter()
            #
            rx_symbols = rx.receive()
            detected_symbols = pam_detect(rx_symbols, M)
            bits = pam_symbols_to_bits(detected_symbols, M)
            bytes = bits_to_bytes(bits)
            array = np.frombuffer(bytes, dtype=np.uint8)
            #
            later = time.perf_counter()
            time_elapsed = later - now
            previous_transmission_times.append(time_elapsed)
            if array.size != frames_per_transmission * width * height * 3:
                print("Invalid frame size of ", array.size)
                continue

            images = array.reshape((frames_per_transmission, height, width, 3))
            print("Pushing images...", len(images))
            for image in images:
                push_image(image)
        except Exception as error:
            print("Error during image reception:", error)


plt.ion()

figure, axis = plt.subplots()
image_plot = axis.imshow(
    np.zeros((height, width, 3), dtype=np.uint8)
)
axis.set_title("Live image")
axis.axis("off")



reciever_thread = threading.Thread(target=recieve_worker, daemon=True)
reciever_thread.start()
while plt.fignum_exists(figure.number):
    image = None

    try:
        image = image_queue.get_nowait()
    except queue.Empty:
        plt.pause(0.01)
        continue

    # print("sleeping for", avg_transmission_time(), "/", qs, "seconds: ", avg_transmission_time() / qs)
    image_plot.set_data(image)
    figure.canvas.draw_idle()

    plt.pause(seconds_per_frame)

should_stop_event.set()

