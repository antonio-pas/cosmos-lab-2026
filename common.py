from reedsolo import RSCodec
import sys
rsc = RSCodec(128)

compression = False
# 3 for 24 bit, 1 for 8 bit
bytes_per_pixel = 1 if compression else 3
frames_per_transmission = 1
seconds_per_transmission = 1.0
seconds_per_frame = seconds_per_transmission / frames_per_transmission
width = 80
height = 80
M = 16
