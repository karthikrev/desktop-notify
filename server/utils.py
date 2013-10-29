import multiprocessing
import time

class Oscillator(multiprocessing.Process):
    def __init__(self, event, period):
        self.event = event
        self.period = period
        super(Oscillator, self).__init__()

    def run(self):
        try:
            while True:
                self.event.clear()
                time.sleep(self.period)
                self.event.set()
        except KeyboardInterrupt:
            pass
