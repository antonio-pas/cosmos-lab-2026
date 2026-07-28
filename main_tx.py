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
accumulated_frames = []

for frame in iio.imiter('<video0>'):
    new_image = Image.fromarray(frame).resize((width,height))
    values = np.asarray(new_image, dtype=np.uint8)
    print("accumulating an image..")
    accumulated_frames.append(values)
    if (len(accumulated_frames) < frames_per_transmission):
        time.sleep(seconds_per_frame)
        continue

    tx_values = np.array(accumulated_frames)
    payload = tx_values.tobytes()
    # encoded_payload = bytes(rsc.encode(payload))
    # bits = bytes_to_bits(encoded_payload)
    bits = bytes_to_bits(payload)

    tx_symbols = np.real(bits_to_pam_symbols(bits, M))
    # print("transmitting", len(encoded_payload), "bytes, ", len(tx_symbols), "symbols")
    print("transmitting", len(payload), "bytes, ", len(tx_symbols), "symbols")
    tx.stop_transmission()
    tx.transmit(tx_symbols)
    accumulated_frames.clear()
    time.sleep(seconds_per_frame)
