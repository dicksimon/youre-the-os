import subprocess
import sys

args = sys.argv[1:]


subprocess.run([
    'python',
    'ppo.py',
    *args
], cwd='src')
