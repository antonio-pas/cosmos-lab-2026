"""Windows entry point: configuration, diagnostics and useful startup errors."""
import argparse
import json
import os
from pathlib import Path
import runpy
import sys


def launch(role):
    parser = argparse.ArgumentParser(description=f'COSMOS image {role.upper()}')
    parser.add_argument('--uri', help='Pluto address, e.g. ip:192.168.2.1 or usb:...')
    parser.add_argument('--camera', type=int, help='TX webcam index (default 0)')
    parser.add_argument('--self-test', action='store_true', help='Check bundled libraries without opening hardware')
    args = parser.parse_args()
    try:
        if args.self_test:
            import adi
            import iio
            import numpy as np
            import scipy.signal
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            import imageio.v3
            import imageio_ffmpeg
            from PIL import Image
            import common
            import cosmos
            import digicomm
            from bytes_and_bits_skeleton import bytes_to_bits, bits_to_bytes
            from compression import compress_24_to_8, decompress_8_to_24
            assert bits_to_bytes(bytes_to_bits(b'COSMOS')) == b'COSMOS'
            assert scipy.signal.convolve([1, 2], [1, 1]).tolist() == [1, 3, 2]
            assert Image.fromarray(np.zeros((2, 2, 3), dtype=np.uint8)).size == (2, 2)
            fig = plt.figure()
            fig.canvas.draw()
            plt.close(fig)
            print('libiio:', iio.version)
            print('FFmpeg:', imageio_ffmpeg.get_ffmpeg_version())
            print(role.upper(), 'self-test passed (no SDR or camera accessed)')
            return
        folder = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
        config_path = folder / 'config.json'
        config = json.loads(config_path.read_text(encoding='utf-8-sig')) if config_path.exists() else {}
        uri = args.uri or config.get(role + '_uri', 'ip:192.168.2.1')
        camera = args.camera if args.camera is not None else config.get('camera', 0)
        if not isinstance(uri, str) or not uri.strip():
            raise ValueError('Device URI must be a nonempty string')
        if not isinstance(camera, int) or camera < 0:
            raise ValueError('Camera must be a nonnegative integer')
        os.environ['COSMOS_' + role.upper() + '_URI'] = uri
        os.environ['COSMOS_CAMERA'] = str(camera)
        print(f'Starting {role.upper()} with Pluto at {uri}', flush=True)
        runpy.run_module('main_' + role, run_name='__main__')
    except KeyboardInterrupt:
        print('\nStopped.')
    except Exception:
        import traceback
        traceback.print_exc()
        if not args.self_test and sys.stdin is not None and sys.stdin.isatty():
            input('\nPress Enter to close...')
        raise SystemExit(1)
