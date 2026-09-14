import os
import sys
if sys.platform == 'win32' and hasattr(sys, '_MEIPASS'):
    os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ.get('PATH', '')
    _cosmos_dll_directory = os.add_dll_directory(sys._MEIPASS)
