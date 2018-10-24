# coding: UTF-8

from pulsectl import Pulse, PulseLoopStop, PulseDisconnected
from threading import Thread


class Pulseaudio(object):
  def __init__(self, media_renderer):
    self.pulse = Pulse('rhythmbox-dlna')
    self.running = True
    self.media_renderer = media_renderer
    self.thread = Thread(target=self.loop)

  def setup(self):
    self.thread.start()

  def on_event(self, event_info):
    if event_info.t != 'change' or event_info.facility != 'sink':
      return
    self.has_event = True
    raise PulseLoopStop()

  def loop(self):
    self.pulse.event_mask_set('sink')
    self.pulse.event_callback_set(self.on_event)
    while self.running:
      self.has_event = False
      try:
        self.pulse.event_listen(timeout=0.1)
      except PulseDisconnected:
        pass
      if self.has_event:
        sink = self.find_running_sink()
        if sink:
          volume = sink.volume.value_flat
          self.media_renderer.set_volume_from_pulseaudio(volume)

  def teardown(self):
    self.running = False
    self.thread.join()

  def find_running_sink(self):
    for sink in self.pulse.sink_list():
      if sink.state == 'running':
        return sink
    print('could not find active sink')


