# coding: UTF-8

import binascii
from flask import Flask, request, send_file, Response
import mimetypes
import netifaces
import os
import re
import requests
from threading import Thread
from urllib.parse import unquote

app = Flask(__name__)
lookup_table = {}
reverse_lookup = {}

@app.after_request
def after_request(response):
  response.headers.add('Accept-Ranges', 'bytes')
  return response

@app.route('/shutdown')
def shutdown():
  request.environ.get('werkzeug.server.shutdown')()
  return ''

@app.route('/media/<hashcode>')
def index(hashcode):
  if not hashcode in lookup_table:
    print(hashcode, 'not found')
    return ('', 204)
  print(lookup_table[hashcode])
  return send_file_partial(lookup_table[hashcode])

class Webservice(object):
  def start(self):
    Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5001}).start()

  def stop(self):
    requests.get('http://localhost:5001/shutdown')

  def url_for_file(self, location):
    filepath = unquote(location).replace('file://', '')
    if filepath in reverse_lookup:
      hashcode = reverse_lookup[filepath]
    else:
      hashcode = binascii.b2a_hex(os.urandom(15)).decode()
      lookup_table[hashcode] = filepath 
      reverse_lookup[filepath] = hashcode
    return self.media_base_url() + hashcode

  def media_base_url(self):
    gws = netifaces.gateways()
    _, interface = gws['default'][netifaces.AF_INET]
    addrs = netifaces.ifaddresses(interface)
    best_address = addrs[netifaces.AF_INET][0]['addr']
    return 'http://{addr}:5001/media/'.format(addr=best_address)

# https://gist.github.com/lizhiwei/7885684
def send_file_partial(path):
  """
      Simple wrapper around send_file which handles HTTP 206 Partial Content
      (byte ranges)
      TODO: handle all send_file args, mirror send_file's error handling
      (if it has any)
  """
  range_header = request.headers.get('Range', None)
  if not range_header: return send_file(path)

  size = os.path.getsize(path)
  byte1, byte2 = 0, None

  m = re.search('(\d+)-(\d*)', range_header)
  g = m.groups()

  if g[0]: byte1 = int(g[0])
  if g[1]: byte2 = int(g[1])

  length = size - byte1
  if byte2 is not None:
      length = byte2 + 1 - byte1

  data = None
  with open(path, 'rb') as f:
      f.seek(byte1)
      data = f.read(length)

  rv = Response(data,
      206,
      mimetype=mimetypes.guess_type(path)[0],
      direct_passthrough=True)
  rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

  return rv
