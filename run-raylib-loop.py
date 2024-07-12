import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'raylib_loop.py',
    *args
], cwd='src')
