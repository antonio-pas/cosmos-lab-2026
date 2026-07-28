import numpy as np
def compress_24_to_8(image):
    array = np.asarray(image, dtype=np.uint8)
    r = array[:, :, 0]
    g = array[:, :, 1]
    b = array[:, :, 2]
    r_3bit = (r >> 5) & 0x07
    g_3bit = (g >> 5) & 0x07
    b_2bit = (b >> 6) & 0x03
    packed_8bit = (r_3bit << 5) | (g_3bit << 2) | b_2bit
    return packed_8bit

###############
def decompress_8_to_24(recieved):
    r_3bit = (recieved >> 5) & 0x07
    g_3bit = (recieved >> 2) & 0x07
    b_2bit = recieved & 0x03
    r_8bit = (r_3bit.astype(np.uint16) * 255 // 7).astype(np.uint8)
    g_8bit = (g_3bit.astype(np.uint16) * 255 // 7).astype(np.uint8)
    b_8bit = (b_2bit.astype(np.uint16) * 255 // 3).astype(np.uint8)
    return np.stack([r_8bit, g_8bit, b_8bit], axis=-1)
