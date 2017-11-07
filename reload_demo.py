import os
import sys
import time




def run(*args, **kwargs):
    while True:
        # print('running ok')
        # tmp()
        print('running once')
        time.sleep(30)

if __name__ == '__main__':
    os.execv(__file__, sys.argv)  # Run a new iteration of the current script, providing any command line args from the current iteration.
