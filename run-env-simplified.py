import subprocess
import sys

args = sys.argv[1:]




subprocess.run([
    'python',
    'env_handler_simplified.py',
    *args
], cwd='src')
