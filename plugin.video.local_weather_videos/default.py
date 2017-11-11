# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# http://www.nbc.com
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
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

addonID = 'plugin.video.local_weather_videos'
addon = xbmcaddon.Addon(addonID)
user_Loc = addon.getSetting('User_Location')

url_dict = {'0': 'http://www.nbcnewyork.com/weather/',
            '1': 'http://www.ksdk.com/weather/forecast/local-weather/41276826',
            '2': 'http://www.kare11.com/weather/forecast/' +
                 'local-weather-forecast-1/412872353',
            '3': 'http://www.nbclosangeles.com/weather/',
            '4': 'http://media.ksl.com/weather.mp4'}

url = url_dict[user_Loc]

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

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


def play_weather_vid(vid_link):
    play_item = xbmcgui.ListItem(path=vid_link)
    play_item.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(addon_handle, True, play_item)


def get_vid_link(url):
    if '.mp4' in url:
        return url
    html = getRequest(url)
    query = 'src=.+?/portableplayer/.+?&videoID=(.+?)&'
    vid_num = re.compile(query, re.DOTALL).search(html)
    if vid_num:
        vid_num = vid_num.groups()[0]
        url = 'https://link.theplatform.com/s/Yh1nAC/'+vid_num +\
              '?manifest=m3u&formats=m3u,mpeg4,webm,ogg&format=SMIL&embedded='\
              'true&tracking=true'
        html = getRequest(url)
        vid_link = re.compile('<video src="(.+?)"', re.DOTALL).search(html)
        vid_link = vid_link.groups()[0]
    else:
        query = 'data-type="video".+?data-id="(.+?)".+?data-site'
        vid_num = re.compile(query, re.DOTALL).search(html)
        vid_num = vid_num.groups()[0]
        url = 'http://api.tegna-tv.com/video/v2/getAllVideoPathsById/'\
              + vid_num + '/63?subscription-key='\
              '29ef605dc92345708f6da324ff5c637f'
        html = getRequest(url)
        json_data = json.loads(html)
        vid_link = json_data['Sources'][5]['Path']

    return vid_link


def list_video(url):
    vid_link = get_vid_link(url)
    list_item = xbmcgui.ListItem('Your Local Weather Report!')
    list_item.setInfo('video', {'title': 'test video'})
    list_item.setProperty("Video", "true")
    list_item.setProperty('IsPlayable', 'true')

    url = ("%s?action=%s&title=%s&url=%s"
           % (base_url, 'play', 'test_video', vid_link))
    is_folder = False
    listing = [(url, list_item, is_folder)]

    # Add list to Kodi.
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)


def router():
    params = dict(args)

    if params:
        if params['action'][0] == 'play':
            play_weather_vid(params['url'][0])
        elif params['action'][0] == 'autostart':
            list_video(url)
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(params))
    else:
        list_video(url)


router()
