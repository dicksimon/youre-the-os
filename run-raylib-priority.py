import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'raylib_priority.py',
    *args
], cwd='src')
