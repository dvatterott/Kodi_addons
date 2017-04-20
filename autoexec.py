# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# kodi auto_exec
# ------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
# ------------------------------------------------------------
import zlib
import json
import sys
import ssl
import urllib2
import re
import datetime
import urlparse
import xbmc

# -----------  Create some functions for fetching videos ---------------
# https://github.com/learningit/Kodi-plugins-source/blob/master/script.module.t1mlib/lib/t1mlib.py
UTF8 = 'utf-8'
USERAGENT = """Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"""
httpHeaders = {'User-Agent': USERAGENT,
               'Accept': "application/json, text/javascript, text/html,*/*",
               'Accept-Encoding': 'gzip,deflate,sdch',
               'Accept-Language': 'en-US,en;q=0.8'
               }
context = ssl._create_unverified_context()


def getRequest(url, udata=None, headers=httpHeaders, context=context):
    req = urllib2.Request(url.encode(UTF8), udata, headers)
    try:
        response = urllib2.urlopen(req, context=context)
        page = response.read()
        if response.info().getheader('Content-Encoding') == 'gzip':
            page = zlib.decompress(page, zlib.MAX_WBITS + 16)
        response.close()
    except Exception:
        page = ""
        xbmc.log('REQUEST ERROR', level=xbmc.LOGDEBUG)
    return(page)


def play_weather_vid():
    url = 'http://www.nbcnewyork.com/weather/'
    html = getRequest(url)
    query = 'http://www.nbcnewyork.com/portableplayer/.+?&videoID=(.+?)&'
    vid_num = re.compile(query, re.DOTALL).search(html)
    vid_num = vid_num.groups()[0]
    url = 'https://link.theplatform.com/s/Yh1nAC/'+vid_num +\
          '?manifest=m3u&formats=m3u,mpeg4,webm,ogg&format=SMIL&embedded='\
          'true&tracking=true'
    html = getRequest(url)
    vid_link = re.compile('<video src="(.+?)"', re.DOTALL).search(html)
    vid_link = vid_link.groups()[0]
    xbmc.log('here i am', level=xbmc.LOGDEBUG)
    xbmc.log(vid_link, level=xbmc.LOGDEBUG)

    xbmc.executebuiltin("PlayMedia(%s)" % (vid_link))


if datetime.datetime.now().hour < 12:
    play_weather_vid()
