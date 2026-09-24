# VideoSDR

A real-time video link build from scratch with two ADALM-Pluto software-defined radios.

https://github.com/user-attachments/assets/678ff8e4-6ee0-4368-9925-67906f4079f6

[Download the executables](https://github.com/antonio-pas/cosmos-lab-2026/releases)

## Quick start

You will need:
- Python 3
- Two ADALM-Pluto SDRs (a transmitter and a receiver) and a webcam
- Python packages: `numpy`, `scipy`, `matplotlib`, `Pillow`, `imageio`, etc.

You can [download the the executables from the releases](https://github.com/antonio-pas/cosmos-lab-2026/releases),
and follow the instructions in the README to run TX.exe on the transmitter and RX.exe on the receiver.

You can also download the source code. If you would like to adjust image size, compression, and modulation, you can do so it in `common.py`. Update the Pluto device URIs in `main_tx.py` and `main_rx.py` for your hardware, then start the transmitter before the receiver:
```bash
python main_tx.py # on the trasmitter
python main_rx.py # on the receiver
```

## Features

- 24bit to 8bit RGB compression
- 16-QAM symbols
- Almost realtime 😅
