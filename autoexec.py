# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# kodi auto_exec
# ------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
# ------------------------------------------------------------
import datetime
import xbmc

if datetime.datetime.now().hour < 12:
    xbmc.executebuiltin("ActivateWindow(Videos,"
                        "plugin://plugin.video.local_weather_videos/"
                        "?action=autostart)")
