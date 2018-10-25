# coding: UTF-8

from datetime import time
import requests
from urllib.parse import urlparse
from urllib.request import urlopen
from xml.dom import minidom

from payloads import Payloads


class MediaRenderer(object):
  def __init__(self, payload):
    o = urlparse(payload['location'])
    base_url = "http://%s:%s" % (o.hostname, o.port)

    with urlopen(payload['location']) as response:
      xml = minidom.parseString(response.read())

    for service in xml.getElementsByTagName('service'):
      service_type = service.getElementsByTagName('serviceType')[0].firstChild.nodeValue
      control_url = service.getElementsByTagName('controlURL')[0].firstChild.nodeValue

      if service_type == 'urn:schemas-upnp-org:service:AVTransport:1':
        self.transport_url = base_url + control_url

      if service_type == 'urn:schemas-upnp-org:service:RenderingControl:1':
        self.control_url = base_url + control_url

    #self.get_volume_db_range()

#  def get_volume_db_range(self):
#    response = requests.post(self.control_url, **Payloads.get_volume_db_range())
#    parsed = xmltodict.parse(response.text)
#    block = parsed['s:Envelope']['s:Body']['u:GetVolumeDBRangeResponse']
#    self.volume_db_range = (int(block['MinValue']) / 256, int(block['MaxValue']) / 256)

  def set_volume_from_pulseaudio(self, volume):
    self.set_volume(volume * 100)
    return
    # minV, maxV = self.volume_db_range
    # volume_db = int(minV + volume * (maxV - minV))
    # self.set_volume_db(volume_db)

  def set_volume(self, volume):
    requests.post(self.control_url, **Payloads.set_volume(volume=volume))

  def set_volume_db(self, volume_db):
    requests.post(self.control_url, **Payloads.set_volume_db(volume_db=volume_db))

  def set_url(self, url):
    requests.post(self.transport_url, **Payloads.set_url(url=url))

  def set_next_url(self, url):
    requests.post(self.transport_url, **Payloads.set_next_url(url=url))

  def play(self):
    requests.post(self.transport_url, **Payloads.play())

  def pause(self):
    requests.post(self.transport_url, **Payloads.pause())

  def seek(self, time_in_seconds):
    target = time(int(time_in_seconds / 3600), int(time_in_seconds % 3600 / 60), int(time_in_seconds % 60), int(1000000 * (time_in_seconds % 1)))
    formatted_target = target.strftime('%H:%M:%S.%f')
    requests.post(self.transport_url, **Payloads.seek(target=formatted_target))

  def next(self):
    requests.post(self.transport_url, **Payloads.next())

  def stop_playback(self):
    requests.post(self.transport_url, **Payloads.stop())

  def seek_workaround(self, url):
    self.stop_playback()
    self.set_url(url)
    self.play()

