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
import urllib2
from datetime import datetime as dt
import re
import ssl
import xbmc
import xbmcgui
import xbmcplugin

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


def deal_with_youtube(html):
    query = r"""<script type="application\/ld\+json">(.+?)<\/script>"""
    vid_num = re.compile(query).search(html)
    url = json.loads(vid_num.group(1))['embedUrl'].split('/')[-1]
    return url


# https://github.com/learningit/Kodi-plugins-source/blob/master/plugin.video.thinktv/resources/lib/scraper.py
# modified from link above
def getAddonVideo(url, udata=None, headers=httpHeaders):
    html = getRequest(url)
    query = """<iframe.+?src="(.+?)" seamless allowfullscreen></iframe>"""
    vid_num = re.compile(query, re.DOTALL).search(html)
    try:
        pg = getRequest(vid_num.group(1))
        query = """PBS.videoData =.+?recommended_encoding.+?'url'.+?'(.+?)'"""
        urls = re.compile(query, re.DOTALL).search(pg)

        url = urls.groups()
        pg = getRequest('%s?format=json' % url)
        url = json.loads(pg)['url']
    except:  # some links are initially posted as youtube vids
        return deal_with_youtube(html)

    if 'rtmp' in url:
        url = url.split('videos')[1]
        url = 'http://ga.video.cdn.pbs.org/videos' + url
        url = url.split('-mp4-')[0] + '-hls-6500k.m3u8'
    elif 'hd-1080p' in url:
        url = url.split('-hls-', 1)[0]
        url = url+'-hls-6500k.m3u8'
    elif '720p' in url:
        url = url.replace('720p.m3u8', '1080p.m3u8')
    return url


# -------------- Create list of folders with videos in them -------------------
def list_folders(url='https://www.pbs.org/newshour/video'):
    html = getRequest(url)

    # first folder is list of full episodes then one folder for each day
    folders = ['Full Episodes', 'All Videos']

    listing = []

    for items in folders:
        if items == 'Full Episodes':
            query = ("""<img class="lazyload" data-srcset=".+? 425w,"""
                     """.+? 768w, (.+?) 1024w" alt="">""")
            pic = re.compile(query, re.DOTALL).search(html)
            plot = 'All full episodes that have aired in the past week.'
        else:
            query = ("""<div class="playlist__img" style="background-image: """
                     """url\('(.+?)'\)">""")
            pic = re.compile(query, re.DOTALL).search(html)
            plot = 'All pbs newshour videos.'

        pic = pic.groups()[0]
        if '180x0' in pic:
            pic = pic.replace('180x0', '1024x0')
        list_item = xbmcgui.ListItem(label=items, thumbnailImage=pic)
        list_item.setInfo('video', {'title': items, 'genre': 'news',
                                    'plot': '[B]PBS NEWSHOUR[/B][CR][CR]'
                                    + plot})
        url = '%s?action=listing&category=%s' % (base_url, items)
        is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(addon_handle)


def key_func(s):
    reg_out = re.findall(r"""episode-(.+?-\d+-\d+)""", s)[0]
    if len(reg_out) < 12:
        output = dt.strptime(reg_out, "%b-%d-%Y")
    else:
        output = dt.strptime(reg_out, "%B-%d-%Y")
    return output


# -------------- Create list of videos --------------------
# http://kodi.wiki/view/HOW-TO:Video_addon
def list_videos(category, url='https://www.pbs.org/newshour/video'):
    html = getRequest(url)

    category = urllib2.unquote(category[0]).decode('utf8')
    # xbmc.log(category, level=xbmc.LOGDEBUG)

    if category == 'Full Episodes':
        query = ("""<a href="(https://www.pbs.org/newshour/show/""" +
                 """pbs-newshour-.+?)" class=".+?">""")
        links = list(set(re.compile(query).findall(html)))
        videos = sorted(links, key=key_func, reverse=True)
        plots = []
        for vids in videos:
            plots.append("Full Episode of %s" % '-'.join(vids.split('-')[-3:]))

    else:
        query = ("""<a href="(.+?)" class="card-sm__title">"""
                 """<span>(.+?)</span></a>""")
        videos = re.compile(query).findall(html)
        plots = [x[1] for x in videos]
        videos = [x[0] for x in videos]

    listing = []
    for vids, plot in zip(videos, plots):
        list_item = xbmcgui.ListItem(' '.join(vids.split('-')[-3:]).title(),
                                     thumbnailImage=vids,
                                     iconImage=vids)
        list_item.setInfo('video',
                          {'title': ' '.join(vids.split('-')[-3:]).title(),
                           'plot': '[B]PBS NEWSHOUR[/B][CR][CR]' + plot})
        list_item.setProperty("Video", "true")
        list_item.setProperty('IsPlayable', 'true')

        url = ("%s?action=%s&title=%s&url=%s&thumbnail=%s"
               % (base_url, 'play',
                  ' '.join(vids.split('-')[-3:]).title(),
                  vids, vids))
        is_folder = False
        listing.append((url, list_item, is_folder))

    # Add list to Kodi.
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)


def play_video(path):
    path = getAddonVideo(path)
    if '00k' in path or '0p' in path:
        play_item = xbmcgui.ListItem(path=path)
        xbmc.log('adding stream info', level=xbmc.LOGDEBUG)
        play_item.addStreamInfo('video', {'codec': 'h264',
                                          'width': 1280,
                                          'height': 720,
                                          'aspect': 1.78})
        play_item.addStreamInfo('audio', {'codec': 'aac',
                                          'language': 'en'})
        play_item.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(addon_handle, True, play_item)
    else:  # deal with youtube links
        path = 'plugin://plugin.video.youtube/?action=play_video&videoid=' \
                + path
        play_item = xbmcgui.ListItem(path=path)
        play_item.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(addon_handle, True, play_item)


def router():
    params = dict(args)

    if params:
        if params['action'][0] == 'play':
            play_video(params['url'][0])
        elif params['action'][0] == 'listing':
            list_videos(params['category'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(params))
    else:
        list_folders()


router()
