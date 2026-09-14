COSMOS TX / RX - Windows x64

Extract the ZIP before running. Python is bundled; no Python installation is needed.
TX.exe sends webcam images using a Pluto SDR. RX.exe receives and displays images
and the constellation using another Pluto SDR.

1. Connect the Pluto SDR and install Analog Devices' Pluto Windows drivers if needed:
   https://wiki.analog.com/university/tools/pluto/drivers/windows
2. Edit config.json beside the executables. Set tx_uri and rx_uri to the correct
   addresses. The defaults assume one Pluto at ip:192.168.2.1 on each of two PCs.
   If using both Plutos on one PC, give them distinct reachable IPs or USB URIs.
3. On the receiver PC, open RX.exe. On the transmitter PC, open TX.exe.
   Set camera to 1 (or another index) if the default webcam is not the right one.
4. Close the receiver plot to exit RX. Press Ctrl+C in the TX console to stop TX.

Command Prompt alternatives:
  TX.exe --uri ip:192.168.2.1 --camera 0
  RX.exe --uri ip:192.168.3.1
  TX.exe --self-test
  RX.exe --self-test

The self-test checks bundled libraries, native libiio, FFmpeg and Tk plots without
accessing a radio or webcam. Actual RF transmission requires testing with hardware.
The original radio/modulation/image settings in common.py are compiled into these
executables. Device URI and webcam index can be changed without rebuilding.

These executables are unsigned. The libiio v0.26 runtime is included from:
https://github.com/analogdevicesinc/libiio/releases/tag/v0.26
libiio is LGPL-2.1-or-later; source and license:
https://github.com/analogdevicesinc/libiio/tree/v0.26
Build scripts and source changes are on the repository's codex/windows-executables branch.
