from utils import Oscillator
from pluginmanager import PluginManager
from notifier import NotifierBubble
import multiprocessing

if __name__ == "__main__":
    notifier = NotifierBubble()
    mgr = multiprocessing.Manager()
    pm = PluginManager(notifier)
    event = mgr.Event()
    o = Oscillator(event, 5)        # TODO: Move this to config file as configurable parameter
    o.start()
    while True:
        pm.call_plugin()
        event.wait()
