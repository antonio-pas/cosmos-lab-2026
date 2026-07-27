import imageio.v3 as iio
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import time
import sys
import time

from cosmos import *
from digicomm import *

import adi
import io

from common import *

from bits_and_pam_skeleton import bits_to_pam_symbols
from bytes_and_bits_skeleton import bytes_to_bits, bits_to_bytes
from PIL import Image

# Directory for saving plots
dir_plots = 'plots/'

# ---------------------------------------------------------------
# Setup.
# --------------------------------------3-------------------------
sdr_tx = adi.Pluto("usb:0.1.5")

tx = PlutoTransmitter()
tx.set_sdr(sdr_tx)
tx.set_channel(1)
tx.set_power_level(100)

# ---------------------------------------------------------------
# Generate random symbols.
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Transmit.
# ---------------------------------------------------------------
number = 0
accumulated_frames = []

for frame in iio.imiter('<video0>'):
    number += 1
    new_image = Image.fromarray(frame).resize((width,height))
    values = np.asarray(new_image, dtype=np.uint8)
    print("accumulating an image..")
    accumulated_frames.append(values)
    if (len(accumulated_frames) < frames_per_transmission):
        time.sleep(seconds_per_frame) # TODO: change this
        continue

    tx_values = np.array(accumulated_frames)
    # print(values)
    print(tx_values.shape)
    bytes = tx_values.tobytes()
    print("transmitting n bytes:", len(bytes))
    bits = bytes_to_bits(bytes)
    tx_symbols = np.real(bits_to_pam_symbols(bits, M))
    print(len(tx_symbols), "symbols")
    tx.stop_transmission()
    tx.transmit(tx_symbols)
    # print("transmitting frame", number, "...")
    accumulated_frames.clear()
    time.sleep(seconds_per_frame)
