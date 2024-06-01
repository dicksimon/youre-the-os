import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'env_ppo.py',
    *args
], cwd='src')
