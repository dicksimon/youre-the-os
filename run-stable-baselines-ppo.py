import subprocess
import sys

args = sys.argv[1:]


subprocess.run([
    'python',
    'stable-baselines-ppo.py',
    *args
], cwd='src')
