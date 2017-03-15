# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# http://www.pbs.org/newshour/videos/
# ------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
# ------------------------------------------------------------
import zlib
import json
import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin

import urllib2
import re

addonID = 'plugin.video.pbsnewshour'

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


def getRequest(url, udata=None, headers=httpHeaders):
    req = urllib2.Request(url.encode(UTF8), udata, headers)
    try:
        response = urllib2.urlopen(req)
        page = response.read()
        if response.info().getheader('Content-Encoding') == 'gzip':
            page = zlib.decompress(page, zlib.MAX_WBITS + 16)
        response.close()
    except Exception:
        page = ""
        xbmc.log(msg='REQUEST ERROR', level=xbmc.LOGDEBUG)
    return(page)


# https://github.com/learningit/Kodi-plugins-source/blob/master/plugin.video.thinktv/resources/lib/scraper.py
# modified from link above
def getAddonVideo(url, udata=None, headers=httpHeaders):
    html = getRequest(url)

    vid_num = re.compile('<span class="coveplayerid">(.+?)</span>',
                         re.DOTALL).search(html)
    if vid_num:
        vid_num = vid_num.group(1)
        pg = getRequest('http://player.pbs.org/viralplayer/%s/' % (vid_num))
        query = """PBS.videoData =.+?recommended_encoding.+?'url'.+?'(.+?)'"""
        urls = re.compile(query, re.DOTALL).search(pg)

        url = urls.groups()
        pg = getRequest('%s?format=json' % url)
        url = json.loads(pg)['url']
    else:  # weekend links are initially posted as youtube vids
        vid_num = re.compile('<span class="youtubeid">(.+?)</span>',
                             re.DOTALL).search(html)
        vid_num = vid_num.group(1)
        url = 'https://www.youtube.com/watch' + vid_num
        pg = getRequest(url)
        # https://www.youtube.com/watch?v=1CoH0aS4K3A
        # pg = getRequest('http://player.youtube.com/uniplayer/1CoH0aS4K3A/' % (vid_num))

    if 'mp4:' in url:
        url = 'http://ga.video.cdn.pbs.org/%s' % url.split('mp4:', 1)[1]
    elif '.m3u8' in url:
        url = url.replace('800k', '2500k')
        if 'hd-1080p' in url:
            url = url.split('-hls-', 1)[0]
            url = url+'-hls-6500k.m3u8'
    return url


# -------------- Create list of videos --------------------
# http://kodi.wiki/view/HOW-TO:Video_addon
def list_videos(url='http://www.pbs.org/newshour/videos/'):
    html = getRequest(url)

    query = """<div class='sw-pic maxwidth'>.+?href='(.+?)'.+?src="(.+?)".+?title="(.+?)" """
    videos = re.compile(query, re.DOTALL).findall(html)

    listing = []
    for vids in videos:
        list_item = xbmcgui.ListItem(label=vids[2],
                                     thumbnailImage=vids[1])
        list_item.setInfo('video', {'title': vids[2]})
        list_item.setProperty('IsPlayable', 'true')

        url = ("%s?action=%s&title=%s&url=%s&thumbnail=%s"
               % (base_url, 'play', vids[2], vids[0], vids[1]))

        listing.append((url, list_item, False))

    # Add list to Kodi.
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)


def play_video(path):
    path = getAddonVideo(path)
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def router():
    params = dict(args)

    if params:
        if params['action'][0] == 'play':
            play_video(params['url'][0])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(params))
    else:
        list_videos()


router()
