# coding: UTF-8

import binascii
from flask import Flask, request, send_file
import netifaces
import os
import requests
from threading import Thread
from urllib.parse import unquote

app = Flask(__name__)
lookup_table = {}
reverse_lookup = {}

@app.route('/shutdown')
def shutdown():
  request.environ.get('werkzeug.server.shutdown')()
  return ''

@app.route('/media/<hashcode>')
def index(hashcode):
  print(lookup_table[hashcode])
  return send_file(lookup_table[hashcode])


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
 

