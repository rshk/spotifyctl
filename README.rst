Spotify Control
###############

Utility script, written in Python, to control the Spotify player via DBus.

:Author: Samuele Santi
:License: Apache 2.0 (or MIT/BSD/whatever..)
:Homepage: https://github.com/rshk/spotifyctl


Dependencies
============

* ``python-dbus``
* ``python-notify``
* ``python-gobject``


Usage
=====

Send a command to the player::

    ./spotifyctl.py --<command> [--showinfo]

Where the ``<command>`` is one of playpause|stop|next|previous (note: there
are play and pause commands too, but they seem not to work properly,
or at all..).

If the ``--showinfo`` flag is added, a popup with song metadata will be shown
after command execution.

Monitor song changes::

    ./spotifyctl.py --watch

Will watch song changes and show notifications.
Anyways, this thing is still not 100% functional, due to seemingly-irrational
behavior of the dbus (and quite likely lack of knowledge about some dbus
thing on my side..).


Configuring awesome shortcuts
-----------------------------

I use this as my keybindings configuration for this script:

.. code-block:: lua

    home = os.getenv("HOME")
    here = home .. "/.config/awesome"
    scripts_dir = here .. "/scripts"
    exec = awful.util.spawn

    globalkeys = awful.util.table.join(

        -- ...

        -- Spotify
        awful.key({  }, "XF86AudioPrev", false, function () exec(scripts_dir .. "/spotifyctl.py --previous") end),
        awful.key({  }, "XF86AudioPlay", false, function () exec(scripts_dir .. "/spotifyctl.py --playpause") end),
        awful.key({  }, "XF86AudioStop", false, function () exec(scripts_dir .. "/spotifyctl.py --stop") end),
        awful.key({  }, "XF86AudioNext", false, function () exec(scripts_dir .. "/spotifyctl.py --next") end),

        -- ...

    )

And of course, don't forget about launching ``spotifyctl.py --watch`` in the
background, using your abitual method for autostarting things at login.
