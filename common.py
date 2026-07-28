from reedsolo import RSCodec
rsc = RSCodec(128)

# 3 for RGB, 1 for L
bytes_per_pixel = 1
frames_per_transmission = 1
seconds_per_transmission = 0.42
seconds_per_frame = seconds_per_transmission / frames_per_transmission
width = 100
height = 100
M = 16
