# coding: UTF-8

import requests
import socket
from urllib.request import urlopen
import xmltodict

from payloads import Payloads

UDP_MTU_SIZE = 65507

SEARCH_MSG = """M-SEARCH * HTTP/1.1
HOST:239.255.255.250:1900
ST:ssdp:all
MX:2
MAN:"ssdp:discover"
""".replace('\n', '\r\n').encode()

class UPNP(object):

  def __init__(self):
    pass

  def find_renderer(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 1900))
    s.settimeout(20)
    s.sendto(SEARCH_MSG, ('239.255.255.250', 1900) )

    try:
      while True:
        data, addr = s.recvfrom(UDP_MTU_SIZE)
        device = self.parse_search_response(addr, data.decode())
        if device.get('nt') == 'urn:schemas-upnp-org:device:MediaRenderer:1':
          return device
    except socket.timeout:
      pass

  def parse_search_response(self, addr, data):
    entry = {
      'ip': addr[0],
      'port': addr[1],
    }
    lines = data.split('\r\n')
    for line in lines:
      if ':' in line:
        key, value = line.split(':', maxsplit=1)
        entry[key.strip().lower()] =  value.strip()
    return entry

  def fetch_description(self, device):
    with urlopen(device['location']) as response:
      device['description'] = xmltodict.parse(response.read())['root']

  def find_transport_control_url(self, device):
    base_url = self.find_base_url(device)
    transport_service = self.find_transport_service(device['description'])
    self.transport_control_url =  ''.join([base_url, transport_service['controlURL']])

  def find_rendering_control_url(self, device):
    base_url = self.find_base_url(device)
    rendering_control_service = self.find_rendering_control_service(device['description'])
    self.rendering_control_url =  ''.join([base_url, rendering_control_service['controlURL']])

  def find_base_url(self, device):
    return device['description']['URLBase'].rstrip('/')

  def find_transport_service(self, description):
    for service in description['device']['serviceList']['service']:
      if service['serviceType'] == 'urn:schemas-upnp-org:service:AVTransport:1':
        return service

  def find_rendering_control_service(self, description):
    for service in description['device']['serviceList']['service']:
      if service['serviceType'] == 'urn:schemas-upnp-org:service:RenderingControl:1':
        return service

  def setup(self):
    renderer = self.find_renderer()
    if renderer is None:
      print('no renderer found')
      return
    print('renderer found on host', renderer['ip'], ', port', renderer['port']) 
    self.fetch_description(renderer)
    self.find_transport_control_url(renderer)
    self.find_rendering_control_url(renderer)
    self.get_volume_db_range()

  def get_volume_db_range(self):
    print('fetch volume db range')
    response = requests.post(self.rendering_control_url, **Payloads.get_volume_db_range())
    parsed = xmltodict.parse(response.text)
    block = parsed['s:Envelope']['s:Body']['u:GetVolumeDBRangeResponse']
    self.volume_db_range = (int(block['MinValue']) / 256, int(block['MaxValue']) / 256)
    print(self.volume_db_range)

  def set_volume_from_pulseaudio(self, volume):
    self.set_volume(volume * 100)
    return
    minV, maxV = self.volume_db_range
    volume_db = int(minV + volume * (maxV - minV))
    self.set_volume_db(volume_db)

  def set_volume(self, volume):
    print('set volume', volume)
    requests.post(self.rendering_control_url, **Payloads.set_volume(volume=volume))

  def set_volume_db(self, volume_db):
    print('set volume db', volume_db)
    requests.post(self.rendering_control_url, **Payloads.set_volume_db(volume_db=volume_db))

  def set_url(self, url):
    print('set url', url)
    requests.post(self.transport_control_url, **Payloads.set_url(url=url))

  def set_next_url(self, url):
    print('set next url', url)
    requests.post(self.transport_control_url, **Payloads.set_next_url(url=url))

  def play(self):
    print('play')
    requests.post(self.transport_control_url, **Payloads.play())

  def pause(self):
    print('pause')
    requests.post(self.transport_control_url, **Payloads.pause())

  def next(self):
    print('next')
    requests.post(self.transport_control_url, **Payloads.next())

  def stop(self):
    print('stop')
    requests.post(self.transport_control_url, **Payloads.stop())

  def teardown(self):
    self.stop()

