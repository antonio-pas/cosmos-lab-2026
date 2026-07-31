# Wireless Image Transmission

A real-time image link built with two ADALM-Pluto software-defined radios. The transmitter captures webcam frames, compresses each RGB pixel to 8 bits, maps the data to 16-QAM symbols, and sends it over a 915 MHz channel. 
The receiver synchronizes and equalizes the signal, then reconstructs and displays the image alongside the received constellation.

## Requirements

- Python 3
- Two ADALM-Pluto SDRs and a webcam
- Python packages: `numpy`, `scipy`, `matplotlib`, `Pillow`, `imageio`, etc.

## Run

Configure image size, compression, and modulation in `common.py`. Update the Pluto device URIs in `main_tx.py` and `main_rx.py` for your hardware, then start the transmitter before the receiver:

```bash
python main_rx.py
python main_tx.py
```
