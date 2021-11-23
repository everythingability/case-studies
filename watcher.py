from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from playsound import playsound
from importlib import reload  
import index

WATCH_FOLDER = "/Library/WebServer/Documents/site/html"

class Handler(FileSystemEventHandler):
   
    def on_modified(self, event):
        reload(index)
        path = event.src_path

        if path.endswith(".md"):
            print ("changed", event.src_path)
            index.render() # rebuild the site
        #playsound("assets/ding.wav")

    def on_moved(self, event):
        ''
        #print("moved", event.src_path)

    def on_deleted(self, event):
        ''
        #print("deleted", event.src_path)
        #_check_modification(event.src_path)

observer = Observer()
# watch the local directory
observer.schedule(Handler(), WATCH_FOLDER, recursive=True) 
print("watching:", WATCH_FOLDER)
observer.start()

try:
    while True:
        sleep(4)
except KeyboardInterrupt:
    observer.stop()

observer.join()