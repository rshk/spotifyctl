#!/usr/bin/env python

"""
Spotify Control Script

This thing talks with spotify via DBus, sending commands like
play|pause|next|previous|stop and showing nice notification popups
on song change.

I didn't need extra functionality as the main purpose of this script
is to be used in global keyboard shortcuts, associated with XF86Audio*
keys. If you want some more, drop me a line or send a pull request
on https://github.com/rshk/spotifyctl.
"""

from __future__ import print_function

import sys
import optparse

try:
    import dbus
except ImportError:
    print("You need the python-dbus package")
    sys.exit(1)

## Directly exposed methods
exposed_methods = [
    'Play', 'Pause', 'PlayPause', 'Stop', 'Next', 'Previous',
]

parser = optparse.OptionParser()

for method in exposed_methods:
    mlower_name = method.lower()
    parser.add_option(
        '--{}'.format(mlower_name),
        action='store_const',
        dest='action',
        const=method)

parser.add_option(
    '--info', action='store_const', dest='action', const='info')
parser.add_option(
    '--showinfo', action='store_true', dest='show_info', default=False,
    help="Show information about the current song, as an inotify message")
parser.add_option(
    '--watch', action='store_const', dest='action', const="watch",
    help="Keep watching for events and display notifications")
opts, args = parser.parse_args()


_player = None
_info = None


def get_player():
    global _player

    if _player is None:
        bus = dbus.SessionBus()
        player = bus.get_object('com.spotify.qt', '/')
        iface = dbus.Interface(player, 'org.freedesktop.MediaPlayer2')
        _player = iface
    return _player


def get_info():
    return get_player().GetMetadata()


if opts.action in exposed_methods:
    ## Simply wrap the DBus method
    get_player().get_dbus_method(opts.action)()

elif opts.action == 'info':
    info = get_info()
    for key, value in info.iteritems():
        if isinstance(value, dbus.Array):
            print(key, ", ".join(value))
        else:
            print(key, value)

def show_info(info=None):

    import tempfile
    import urllib2

    try:
        import pynotify
    except ImportError:
        print("You need the python-notify package")
        sys.exit(1)

    if info is None:
        info = get_info()

    _duration = int(info['mpris:length']) / 1000000.0 / 60
    _duration_str = "{:d}:{:02d}".format(
        int(_duration), int(60*(_duration%1)))

    metadata = {
        'duration': _duration_str,
        'title': info['xesam:title'],
        'album': info['xesam:album'],
        'artist': ', '.join(info['xesam:artist']),
    }

    pynotify.init('SpotifyNotify')

    _title_format = "{title}"
    _body_format = "{artist}\n\nAlbum: {album}\nDuration: {duration}"

    notif  = pynotify.Notification(
        _title_format.format(**metadata),
        _body_format.format(**metadata))

    ## Retrieve cover art ------------------------------------------------------
    _art_url = info['mpris:artUrl']
    f = tempfile.NamedTemporaryFile()
    r = urllib2.urlopen(_art_url)
    f.write(r.read())
    f.flush()
    notif.set_property('icon-name', f.name)

    ## Show notification -------------------------------------------------------
    notif.show()

    # The temporary file should be GC-ed -> closed -> deleted


if opts.show_info:
    show_info()


if opts.action == 'watch':
    import gobject
    from dbus.mainloop.glib import DBusGMainLoop

    print("Starting watcher...")
    def on_signal(*args):
        ## We cannot trust metadata for some reason -> let's fetch again..
        print("--- Signal received", args)
        show_info()

    dbus_loop = DBusGMainLoop()
    bus = dbus.SessionBus(mainloop=dbus_loop)

    player = bus.get_object('com.spotify.qt', '/org/mpris/MediaPlayer2')

    ## This works only when the current song changes..
    ## But, eg, it will still display stuff when stopped, etc..
    iface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
    iface.connect_to_signal('PropertiesChanged', on_signal)

    # iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
    # iface.connect_to_signal(None, on_signal)

    ## This doesn't work -- why?
    ## (This should send meaningful names like Next|Previous)
    #bus.add_signal_receiver(on_signal, dbus_interface="org.mpris.MediaPlayer2.Player")

    ## This matches every event.. but we don't want that!
    #bus.add_signal_receiver(on_signal)

    ## Some signals caught via dbus-monitor..
    ## method call sender=:1.553 -> dest=com.spotify.qt serial=2 path=/org/mpris/MediaPlayer2; interface=org.mpris.MediaPlayer2.Player; member=Previous
    ## signal sender=:1.106 -> dest=(null destination) serial=621 path=/org/mpris/MediaPlayer2; interface=org.freedesktop.DBus.Properties; member=PropertiesChanged
    ## method return sender=:1.106 -> dest=:1.542 reply_serial=2

    ## Start the main loop
    loop = gobject.MainLoop()
    loop.run()
