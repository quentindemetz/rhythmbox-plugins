#!/usr/bin/python
# coding: UTF-8
# 
# Copyright (C) 2018 - Quentin de Metz <quentin@de.me.tz>

import gi
gi.require_version('Notify', '0.7')
from gi.repository import GObject, RB, Peas, GLib, Gdk, Notify
from urllib.parse import urlparse
import os
import urllib.request, urllib.parse, urllib.error

from upnp import UPNP
from webservice import lookup_table, Webservice
from pulseaudio import Pulseaudio

Gdk.threads_init()

class DLNAPlugin(GObject.Object, Peas.Activatable):
  __gtype_name__ = 'DLNAPlugin'
  object = GObject.property(type=GObject.Object)

  def __init__(self):
    '''
    init plugin
    '''
    super(DLNAPlugin, self).__init__()

  def do_activate(self):
    self.shell = self.object
    self.sp = self.shell.props.shell_player
    self.connect_signals()
    self.upnp = UPNP()
    self.upnp.setup()
    self.webservice = Webservice()
    self.webservice.start()
    self.pulseaudio = Pulseaudio(upnp=self.upnp)
    self.pulseaudio.setup()
    self.sp.set_volume(0)
    self.current_track_position = None

  def do_deactivate(self):
    self.disconnect_signals()
    self.upnp.teardown()
    self.webservice.stop()
    self.sp.pause()
    self.sp.set_volume(1)
    self.pulseaudio.teardown()
    del self.shell
    del self.sp
    del self.upnp
    del self.pulseaudio
    del self.current_track_position

  def connect_signals(self):
    self.player_cb_ids = (
      self.sp.connect('playing-changed', self.playing_changed_cb),
      self.sp.connect ('playing-song-changed', self.playing_song_changed_cb),
      self.sp.connect('elapsed-nano-changed', self.elapsed_changed_cb),
    )

  def disconnect_signals(self):
    for cb_id in self.player_cb_ids:
      self.sp.disconnect(cb_id)
    del self.player_cb_ids

  def elapsed_changed_cb(self, _player, elapsed):
    elapsed /= 1000000000
    if self.current_track_position is not None and abs(elapsed - self.current_track_position) > 1:
      print('seek detected')
      self.upnp.seek(elapsed)
    self.current_track_position = elapsed

  def playing_song_changed_cb(self, _player, entry):
    if entry is None:
      return
    location = entry.get_string(RB.RhythmDBPropType.LOCATION)
    url = self.webservice.url_for_file(location)
    self.upnp.stop()
    self.upnp.set_url(url)
    self.upnp.play()

  def playing_changed_cb(self, _player, is_playing):
    if (is_playing):
      self.upnp.play()
    else:
      self.upnp.pause()

