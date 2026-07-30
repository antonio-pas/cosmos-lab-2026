from compression import decompress_8_to_24
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
# from bits_and_pam_skeleton import pam_symbols_to_bits, get_pam_constellation
from cosmos import *
from digicomm import *
# from detection_skeleton import pam_detect
from common import *

sdr_rx = adi.Pluto("usb:1.1.5")
rx = PlutoReceiver()
rx.set_sdr(sdr_rx)
rx.set_buffer_size(2e6)
rx.set_channel(1)
rx.set_sample_rate(int(2e6))
rx.set_gain_level(80)
rx.desired_transmit_symbols_real = False

image_bytes = frames_per_transmission * bytes_per_pixel * width * height
# encoded_bytes = len(rsc.encode(bytes(image_bytes)))

bits_per_symbol = int(np.log2(M))
num_symbols = int(np.ceil(image_bytes * 8 / bits_per_symbol))
rx.num_transmit_symbols = num_symbols

def qam_symbols_to_bits(symbols, M):
    constellation = get_qam_constellation(M)
    symbols = np.asarray(symbols).flatten()

    symbol_indices = np.argmin(
        np.abs(symbols[:, None] - constellation[None, :]),
        axis=1,
    )

    bits_per_symbol = int(np.log2(M))
    shifts = np.arange(bits_per_symbol - 1, -1, -1)

    bits = (
        (symbol_indices[:, None] >> shifts) & 1
    ).astype(np.uint8)

    return bits.reshape(-1)

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
plt.ion()
figure, axis = plt.subplots(1, 2)

def recieve_worker():
    while not should_stop_event.is_set():
        try:
            now = time.perf_counter()
            #
            constellation = get_qam_constellation(M)
            rx_symbols = rx.receive()
            axis[1].clear()
            axis[1].scatter(
                np.real(rx_symbols),
                np.imag(rx_symbols),
                alpha=0.3,
                label="Received",
            )

            axis[1].scatter(
                np.real(constellation),
                np.imag(constellation),
                color="red",
                marker="x",
                label="Ideal",
            )

            axis[1].set_aspect("equal", adjustable="box")
            axis[1].set_title(f"{M}-QAM constellation")
            axis[1].grid(True)
            axis[1].legend()

            figure.canvas.draw_idle()
            # plt.pause(0.01)
            bits = qam_symbols_to_bits(rx_symbols, M)
            payload = bits_to_bytes(bits)
            # try:
            #     decoded_payload = bytes(rsc.decode(payload)[0])
            #     array = np.frombuffer(decoded_payload, dtype=np.uint8)
            # except ReedSolomonError:
            #     print("corrupted frame, skipping")
            #     continue
            array = np.frombuffer(payload, dtype=np.uint8)
            later = time.perf_counter()
            time_elapsed = later - now
            print("took",time_elapsed,"secs")
            previous_transmission_times.append(time_elapsed)
            if array.size != frames_per_transmission * width * height * bytes_per_pixel:
                print("Invalid frame size of ", array.size)
                continue

            if compression:
                images_array = decompress_8_to_24(array)
                images = images_array.reshape((frames_per_transmission, height, width, bytes_per_pixel*3))
            else:
                images_array = array
                images = images_array.reshape((frames_per_transmission, height, width, bytes_per_pixel))

            print("Pushing images...", len(images))
            for image in images:
                push_image(image)
        except Exception as error:
            print("Error during image reception:", error)
#
# cmap = "gray" if bytes_per_pixel == 1 else None
image_plot = axis[0].imshow(
    np.zeros((height, width, bytes_per_pixel), dtype=np.uint8),
    vmin=0,
    vmax=255,
    # cmap=cmap
)
axis[0].set_title("Live image")
axis[0].axis("off")



reciever_thread = threading.Thread(target=recieve_worker, daemon=True)
reciever_thread.start()
# recieve_worker()
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
