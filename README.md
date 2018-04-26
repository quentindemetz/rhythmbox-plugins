# Rhythmbox DLNA plugin

## Context
- my laptop runs pulseaudio (like any ubuntu box)
- I listen to music with rhythmbox
- I've plugged in a raspberrypi to my old stereo and installed [gmediarenderer](https://github.com/hzeller/gmrender-resurrect), which provides an [DLNA](https://en.wikipedia.org/wiki/Digital_Living_Network_Alliance) Digital Media Renderer
- I've been wanting to stream my music to my stereo over wifi (aka airplay in the apple world)
- I couldn't get [pulseaudio-dlna](https://github.com/masmu/pulseaudio-dlna) to work

## Solution
This plugin:
- locates my network's Digital Media Renderer
- streams rhythmbox's currently playing track to it
- synchronizes my laptop's pulseaudio volume (itself controlled with the media keys) with the renderer's volume

This works great in my particular setup. While there isn't anything strictly hard-coded, I have made couple of assumptions.
Your Mileage May Vary.

## Installation
- copy/symlink the dlna folder inside `~/.local/share/rhythmbox/plugins/` 
- install dependencies: `pip3 install -r ~/.local/share/rhythmbox/plugins/dlna/requirements.txt`
- restart rhythmbox and activate the plugin
- that's it!
