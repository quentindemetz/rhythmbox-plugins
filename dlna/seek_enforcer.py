# coding: UTF-8

from threading import Thread
from time import time, sleep

class SeekEnforcer(Thread):
  def __init__(self, dlna):
    super(SeekEnforcer, self).__init__()
    self.dlna = dlna

  def run(self):
    started_at = time()
    while time() - started_at < 0.5:
      print('enforcing seek')
      self.dlna.current_track_position = -1
      sleep(0.1)


