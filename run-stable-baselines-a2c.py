import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'stable-baselines-a2c.py',
    *args
], cwd='src')
