import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'raylib.py',
    *args
], cwd='src')
