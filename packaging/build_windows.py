"""Run on Windows with Python 3.11 x64."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
if sys.platform != 'win32':
    raise SystemExit('Build on Windows with Python 3.11 x64.')
work = ROOT / 'build' / 'libiio'
work.mkdir(parents=True, exist_ok=True)
archive = work / 'Windows.zip'
urllib.request.urlretrieve('https://github.com/analogdevicesinc/libiio/releases/download/v0.26/Windows.zip', archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest() == '4ad4a8c6b3f7145922c122dcfc51d693f0d3f9a0054fb2228814ce58c538a6ca'
with zipfile.ZipFile(archive) as z:
    z.extractall(work)
dlls = work / 'Windows-VS-2022-x64'
for role in ('tx', 'rx'):
    cmd = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile', '--console',
           '--name', role.upper(), '--paths', str(ROOT), '--runtime-hook', 'packaging/runtime_hook.py',
           '--hidden-import', 'main_' + role, '--hidden-import', 'matplotlib.backends.backend_tkagg',
           '--collect-all', 'imageio_ffmpeg', '--collect-all', 'imageio', '--collect-all', 'adi']
    for dll in dlls.glob('*.dll'):
        if dll.name not in ('libiio-sharp.dll', 'vcruntime140.dll', 'msvcp140.dll'):
            cmd += ['--add-binary', str(dll) + ';.']
    cmd += ['packaging/windows_' + role + '.py']
    subprocess.run(cmd, cwd=ROOT, check=True)
for name in ('config.json', 'README-Windows.txt'):
    shutil.copy2(ROOT / 'packaging' / name, ROOT / 'dist' / name)
with (ROOT / 'dist' / 'build-dependencies.txt').open('w') as f:
    subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=f, check=True)
