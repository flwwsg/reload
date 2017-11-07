import sys
import os
import subprocess
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import _thread as thread
import traceback
import six

from reload_demo import run

RUN_RELOADER = True


class FileChangedHandler(FileSystemEventHandler):
   
    def on_any_event(self, event):
        print('something happened')
        print(event.src_path, event.event_type) 
        os._exit(3)  


def restart_with_reloader():
    while True:
        args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
        new_environ = os.environ.copy()
        new_environ["RUN_MAIN"] = 'true'
        print('restart_with_reloader args, ', args)
        exit_code = subprocess.call(args, env=new_environ)
        
        if exit_code != 3:
            return exit_code

def check_errors(fn):
    # print('initing...')
    def wrapper(*args, **kwargs):
        global _exception
        try:
            fn(*args, **kwargs)
        except Exception:
            _exception = sys.exc_info()
            et, ev, tb = _exception
            
            if getattr(ev, 'filename', None) is None:
                # get the filename from the last item in the stack
                filename = traceback.extract_tb(tb)[-1][0]
            else:
                filename = ev.filename
            print(_exception)
            raise
    return wrapper

def reloader_thread():
    observer = Observer()
    path = '.'
    event_handler = FileChangedHandler()
    observer.schedule(event_handler, path)
    observer.start()
    while True:
        time.sleep(1)

def python_reloader(main_func, args, kwargs):
    print('python_reloader args,', args)
    print ( os.environ.get('RUN_MAIN'))
    if os.environ.get('RUN_MAIN') == 'true':
        thread.start_new_thread(main_func, args, kwargs)
        try:
            reloader_thread()
        except KeyboardInterrupt:
            pass
    else:
        try:
            exit_code = restart_with_reloader()
            if exit_code < 0:
                os.kill(os.getpid(), -exit_code)
            else:
                sys.exit(exit_code)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    # # restart_with_reloader()
    # logging.basicConfig(level=logging.INFO, 
                        # format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S'
    #                     )
    # path = sys.argv[1] if len(sys.argv) > 1  else '.'
    # event_handler = FileChangedHandler()
    # observer = Observer()
    # observer.schedule(event_handler, path, recursive=True)
    # observer.start()
    # try:
    #     while True:
            # time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()
    
    python_reloader(check_errors(run), args=('test',), kwargs={'test':'test'})
