from task import *
from music_task import *

import time
import gc

class Executor:
    def step(self):
        tasks = get_avaiable_task()
        for t in tasks:
            mt = MusicTask(t)
            mt.process()
        gc.collect()

    def run(self):
        while True:
            self.step()
            time.sleep(15)

if __name__ == "__main__":
    e = Executor()
    e.run()