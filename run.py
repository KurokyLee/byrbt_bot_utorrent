import sys
import time
import os
import subprocess

if __name__ == '__main__':
    now = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    cmd = f'python -u bot.py > logs/bot_{now}.log'
    print(f'Running command: {cmd}')
    sys.exit(subprocess.call(cmd, shell=True))

