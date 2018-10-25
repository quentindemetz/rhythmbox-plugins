#!/usr/bin/python
# coding: UTF-8
# 
# Copyright (C) 2018 - Quentin de Metz <quentin@de.me.tz>

import gi
from gi.repository import GObject, RB, Peas, Gdk, Gio
import os, os.path
from subprocess import run, DEVNULL
from time import time
from urllib.parse import urlparse, unquote

from upnp import UPNP
from webservice import lookup_table, Webservice
from pulseaudio import Pulseaudio

Gdk.threads_init()

class DLNAPlugin(GObject.Object, Peas.Activatable):
  __gtype_name__ = 'DLNAPlugin'
  object = GObject.property(type=GObject.Object)

  def __init__(self):
    super(DLNAPlugin, self).__init__()
    self.player_cb_ids = []
    self.last_track_position_change = None
    self.last_known_track_position = None
    self.last_track_change = None
    self.current_track = None
    self.media_renderer = None

  def do_activate(self):
    self.shell = self.object
    self.sp = self.shell.props.shell_player
    self.window = self.shell.props.window
    self.app = self.shell.props.application

    self.sp.set_volume(1)
    self.webservice = Webservice()
    self.webservice.start()

    UPNP().find_renderer_in_bg(
      success_cbs=[self.store_media_renderer, self.enable_streaming, self.setup_menu_items]
    )

  def store_media_renderer(self, media_renderer):
    self.media_renderer = media_renderer

  def setup_menu_items(self, **kwargs):
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
    self.pulseaudio = Pulseaudio(media_renderer=self.media_renderer)
    self.pulseaudio.setup()

    self.playing_song_changed_cb(None, self.sp.get_playing_entry())
    self.last_known_track_position = -1
    self.connect_signals()

  def disable_streaming(self, *args, **kwargs):
    self.app.remove_plugin_menu_item("tools", "disable-dlna-streaming")
    item = Gio.MenuItem.new(label=_("Enable Streaming"), detailed_action="win.enable-dlna-streaming")
    self.app.add_plugin_menu_item("tools", "enable-dlna-streaming", item)

    self.disconnect_signals()
    self.sp.set_volume(1)
    self.pulseaudio.teardown()
    if self.media_renderer is not None:
      self.media_renderer.stop_playback()

  def do_deactivate(self):
    self.disable_streaming()
    self.teardown_menu_items()
    self.disconnect_signals()

    if self.media_renderer is not None:
      self.media_renderer.stop_playback()
    self.webservice.stop()
    self.sp.pause()

    self.window.destroy()

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
    elapsed /= 1e9

    if self.last_known_track_position is not None and self.last_known_track_position is not None:
      # is this event triggered because we just changed tracks ?
      if abs(time() - self.last_track_change) > 1:
        # is the wall clock consistent with the track position change ?
        if abs(time() - self.last_track_position_change - elapsed + self.last_known_track_position) > 1:
          print('seek detected (%s, %s)' % (self.last_known_track_position, elapsed))
          # self.media_renderer.seek(elapsed)
          self.seek_workaround(elapsed)

    self.last_known_track_position = elapsed
    self.last_track_position_change = time()

  def seek_workaround(self, elapsed):
    _, extension = os.path.splitext(self.current_track)
    tmp_location = '/tmp/%s%s' % (time(), extension)
    current_track_location = unquote(urlparse(self.current_track).path)
    run(['ffmpeg', '-ss', str(elapsed), '-i', current_track_location, '-acodec', 'copy', tmp_location], stdout=DEVNULL, stderr=DEVNULL)
    url = self.webservice.url_for_file(tmp_location)
    self.media_renderer.seek_workaround(url)

  def playing_song_changed_cb(self, _player, entry):
    if entry is None:
      return
    self.last_track_change = time()
    location = entry.get_string(RB.RhythmDBPropType.LOCATION)
    self.current_track = location
    url = self.webservice.url_for_file(location)
    self.media_renderer.stop_playback()
    self.media_renderer.set_url(url)
    self.media_renderer.play()

  def playing_changed_cb(self, _player, is_playing):
    if (is_playing):
      self.media_renderer.play()
    else:
      self.media_renderer.pause()


