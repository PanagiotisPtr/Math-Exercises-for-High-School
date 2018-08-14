import subprocess
import time
import sys
import datetime
import os
import pyinotify
import sched
import threading
import easygui

filename = sys.argv[1]

if filename[-3:] != "tex":
    print("Invalid file. You need to input a .tex file")
    exit()

def create_tex_error(text):
    return "\\documentclass{article}\n\\usepackage[greek,english]{babel}\n\\usepackage[utf8x]{inputenc}\n\\author{}\n\\date{}\n\\title{" + text + "}\n\\begin{document}\n\\maketitle\n\\end{document}"

def show_error_message(message):
    easygui.msgbox(message, title="Compile Error")

def save_file(filename, dir_name="file_save_log"):
    if not os.path.exists("file_save_log"):
        os.makedirs("file_save_log")
    ts = datetime.datetime.now().strftime('%d.%m.%Y__%H.%M.%S')
    content = ""
    with open(filename, 'r') as f:
        content = f.read()
    completePath = os.path.join("./file_save_log", ts+".tex")
    with open(completePath, 'w') as f:
        f.write(content)

# Saves file automatically every 5 mins
def time_save(filename):
    while True:
        print("saving...")
        save_file(filename)
        time.sleep(60*5)

class ModHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, evt):
        result = subprocess.run(["pdflatex", "-halt-on-error", filename], stdout=subprocess.PIPE)
        s = result.stdout.decode('utf-8')
        print(s)
        if "No pages of output." in s or "error occurred" in s:
            print("COMPILE ERROR")
            show_error_message(s)
        # remove unnecessary files
        os.remove(filename[:-3] + 'aux')
        os.remove(filename[:-3] + 'log')
        print("Done!")

saver_thread = threading.Thread(target=time_save, args=(filename,))
saver_thread.start()

handler = ModHandler()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(filename, pyinotify.IN_CLOSE_WRITE)
notifier.loop()
