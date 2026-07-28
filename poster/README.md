# Wireless Image Transmission poster prototype

This draft is based on the transmitter/receiver implementation in this
repository. It presents the project as a real-time image link between two
ADALM-Pluto software-defined radios.

## Source narrative

- Capture and resize a camera frame to 100 × 100 pixels.
- Compress RGB from 24 bits to an RGB 3-3-2 packed byte.
- Convert bytes to bits and map groups of four bits to 16-QAM symbols.
- Add STF/LTF training fields and pilots, then apply RRC pulse shaping.
- Transmit over a 915 MHz, 1 MS/s radio link.
- Apply matched filtering, symbol and frame synchronization, coarse/fine CFO
  correction, pilot-based channel estimation, and equalization.
- Demap the received symbols and reconstruct the image.

## Final generation prompt

Create an airy Swiss-modern scientific poster titled “WIRELESS IMAGE
TRANSMISSION” with the subtitle “A REAL-TIME SOFTWARE-DEFINED RADIO LINK.”
Use a white background, minimal sans-serif typography, primary blue #1267D6,
deep navy #102A43, and pale blue #EAF3FF. Explain the system at two levels:
a plain-language overview for a general audience and concise technical
annotations for engineering readers. Show a seven-stage pipeline from camera
capture through RGB 3-3-2 compression, bits, 16-QAM, a 915 MHz ADALM-Pluto
link, synchronization/equalization, and reconstruction. Include input and
reconstructed hamster frames, a signal-anatomy waveform with STF, guard, LTF,
pilots, and payload, ideal-versus-received 16-QAM plots, transmitter and
receiver method flows, draft result placeholders, and a key-parameters strip.
Preserve generous whitespace, strong alignment, high contrast, restrained
technical graphics, and an accessible reading order. Avoid clutter, tiny
paragraphs, decorative circuit patterns, dark backgrounds, gradients, serif
fonts, and invented final performance values.

The final prototype canvas is 1500 × 1900 pixels, matching the requested
30:38 (15:19) aspect ratio. It is intended for layout exploration, not final
30-inch print production.
