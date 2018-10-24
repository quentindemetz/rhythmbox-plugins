# coding: UTF-8

import socket
import struct

from media_renderer import MediaRenderer

UDP_MTU_SIZE = 65507
DLNA_GROUP = '239.255.255.250'
DLNA_PORT = 1900

SEARCH_MSG = """M-SEARCH * HTTP/1.1
HOST:239.255.255.250:1900
ST:ssdp:all
MX:2
MAN:"ssdp:discover"
""".replace('\n', '\r\n').encode()

class UPNP(object):

  def __init__(self):
    pass

  # https://stackoverflow.com/questions/603852/multicast-in-python
  def find_renderer(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((DLNA_GROUP, DLNA_PORT))
    s.settimeout(60)
    s.sendto(SEARCH_MSG, ('239.255.255.250', 1900) )
    mreq = struct.pack("4sl", socket.inet_aton(DLNA_GROUP), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    try:
      while True:
        data, addr = s.recvfrom(UDP_MTU_SIZE)
        device = self.parse_search_response(addr, data.decode())
        if device.get('nt') == 'urn:schemas-upnp-org:device:MediaRenderer:1':
          print('renderer found on %s' % (device['location'])) 
          return MediaRenderer(device)
    except socket.timeout:
      pass

  def parse_search_response(self, addr, data):
    entry = {}
    lines = data.split('\r\n')
    for line in lines:
      if ':' in line:
        key, value = line.split(':', maxsplit=1)
        entry[key.strip().lower()] =  value.strip()
    return entry

