import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# Converting between bits and bytes.
# You may find the following helpful:
# np.frombuffer()
# np.unpackbits()
# np.packbits()
# .tobytes()

def bytes_to_bits(byte_data):
    buffer = np.frombuffer(byte_data, dtype=np.uint8)
    bits = np.unpackbits(buffer)
    return bits

def bits_to_bytes(bits):
    buffer = np.packbits(bits)
    bytes = buffer.tobytes()
    # Add your conversion code here.
    return bytes

# Here are some basic tests for your functions, feel free to add your own
# for debugging as you see fit.

def main():
    test_bytes = bytes.fromhex("123456")
    bits = bytes_to_bits(test_bytes)
    recovered_bytes = bits_to_bytes(bits)

    assert(recovered_bytes == test_bytes)

if __name__ == "__main__":
    main()
