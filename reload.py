import sys
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

try:
    import _thread as thread
except ImportError:
    import thread

from reload_demo import run

RUN_RELOADER = True

class FileChangedHandler(PatternMatchingEventHandler):

    def on_any_event(self, event):
        print(event.src_path, event.event_type) 
        os._exit(3)  


def restart_with_reloader():
    while True:
        args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
        new_environ = os.environ.copy()
        new_environ["RUN_MAIN"] = 'true'
        # print('restart_with_reloader args, ', args)
        exit_code = subprocess.call(args, env=new_environ)
        
        if exit_code != 3:
            return exit_code

def reloader_thread():
    observer = Observer()
    path = '.'
    event_handler = FileChangedHandler(ignore_patterns=['*/.vscode/*', '*/.idea/*'], ignore_directories=True)
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
    python_reloader(run, args=('test',), kwargs={'test':'test'})
