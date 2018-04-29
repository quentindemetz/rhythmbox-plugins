#!/usr/bin/python
# coding: UTF-8
# 
# Copyright (C) 2018 - Quentin de Metz <quentin@de.me.tz>

import gi
from gi.repository import GObject, RB, Peas, Gdk, Gio
from urllib.parse import urlparse
import os
import urllib.request, urllib.parse, urllib.error

from upnp import UPNP
from webservice import lookup_table, Webservice
from pulseaudio import Pulseaudio
from seek_enforcer import SeekEnforcer

Gdk.threads_init()

class DLNAPlugin(GObject.Object, Peas.Activatable):
  __gtype_name__ = 'DLNAPlugin'
  object = GObject.property(type=GObject.Object)

  def __init__(self):
    super(DLNAPlugin, self).__init__()
    self.player_cb_ids = []
    self.current_track_position = None

  def do_activate(self):
    self.shell = self.object
    self.sp = self.shell.props.shell_player
    self.window = self.shell.props.window
    self.app = self.shell.props.application

    self.upnp = UPNP()
    self.upnp.setup()
    self.webservice = Webservice()
    self.webservice.start()
    self.setup_menu_items()
    self.enable_streaming()

  def setup_menu_items(self):
    self.enable_action = Gio.SimpleAction.new("enable-dlna-streaming", None)
    self.disable_action = Gio.SimpleAction.new("disable-dlna-streaming", None)
    self.enable_action.connect("activate", self.enable_streaming, self.shell)
    self.disable_action.connect("activate", self.disable_streaming, self.shell)

    self.window.add_action(self.enable_action)
    self.window.add_action(self.disable_action)

  def teardown_menu_items(self):
    self.app.remove_plugin_menu_item("tools", "enable-dlna-streaming")
    self.app.remove_plugin_menu_item("tools", "disable-dlna-streaming")
    self.app.remove_action('enable-dlna-streaming')
    self.app.remove_action('disable-dlna-streaming')
    del self.enable_action
    del self.disable_action

  def enable_streaming(self, *args, **kwargs):
    self.app.remove_plugin_menu_item("tools", "enable-dlna-streaming")
    item = Gio.MenuItem.new(label=_("Disable Streaming"), detailed_action="win.disable-dlna-streaming")
    self.app.add_plugin_menu_item("tools", "disable-dlna-streaming", item)

    self.sp.set_volume(0)
    self.pulseaudio = Pulseaudio(upnp=self.upnp)
    self.pulseaudio.setup()

    self.playing_song_changed_cb(None, self.sp.get_playing_entry())
    SeekEnforcer(self).start()
    #self.current_track_position = -1
    self.connect_signals()

  def disable_streaming(self, *args, **kwargs):
    self.app.remove_plugin_menu_item("tools", "disable-dlna-streaming")
    item = Gio.MenuItem.new(label=_("Enable Streaming"), detailed_action="win.enable-dlna-streaming")
    self.app.add_plugin_menu_item("tools", "enable-dlna-streaming", item)

    self.disconnect_signals()
    self.sp.set_volume(1)
    self.pulseaudio.teardown()
    self.upnp.stop()

  def do_deactivate(self):
    self.disable_streaming()
    self.teardown_menu_items()
    self.disconnect_signals()

    self.upnp.teardown()
    self.webservice.stop()
    self.sp.pause()

    self.window.destroy()
    del self.shell
    del self.sp
    del self.upnp
    del self.pulseaudio
    del self.current_track_position
    del self.window
    del self.player_cb_ids

  def connect_signals(self):
    self.player_cb_ids = (
      self.sp.connect('playing-changed', self.playing_changed_cb),
      self.sp.connect ('playing-song-changed', self.playing_song_changed_cb),
      self.sp.connect('elapsed-nano-changed', self.elapsed_changed_cb),
    )

  def disconnect_signals(self):
    for cb_id in self.player_cb_ids:
      self.sp.disconnect(cb_id)
    self.player_cb_ids = []

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


