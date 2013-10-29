import subprocess

class NotifierBubble:
    def __init__(self):   # TODO: Don't hard code it
        self.bin_path = "/Users/knamasi/workspace/desktopnotify/Contents/MacOS/terminal-notifier"

    def popup(self, news, provider, url):
        notify_message = [self.bin_path, ] + ["-title", ] + [provider,]  + ["-message",] + [news,] + ["-open",] +  [url] + ["-execute",] + ["echo Karthik>/tmp/oyee"]  #TODO: remove this
        output = subprocess.Popen( notify_message, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if output.returncode:
            raise Exception("Some error during subprocess call.")
        return output
