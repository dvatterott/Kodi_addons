# -*- coding: utf-8 -*-
#------------------------------------------------------------
# http://www.pbs.org/newshour/videos/
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#------------------------------------------------------------
import zlib
import json
import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
from addon.common.addon import Addon

from bs4 import BeautifulSoup
import urllib2
import re

addonID = 'plugin.video.pbsnewshour'
addon = Addon(addonID, sys.argv)

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

################# Create some functions for fetching videos ###########################
#https://github.com/learningit/Kodi-plugins-source/blob/master/script.module.t1mlib/lib/t1mlib.py
UTF8 = 'utf-8'
USERAGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
httpHeaders = {'User-Agent': USERAGENT,
                        'Accept':"application/json, text/javascript, text/html,*/*",
                        'Accept-Encoding':'gzip,deflate,sdch',
                        'Accept-Language':'en-US,en;q=0.8'
                }

def getRequest(url, udata=None, headers = httpHeaders):
    req = urllib2.Request(url.encode(UTF8), udata, headers)
    try:
        response = urllib2.urlopen(req)
        page = response.read()
        if response.info().getheader('Content-Encoding') == 'gzip':
            page = zlib.decompress(page, zlib.MAX_WBITS + 16)
        response.close()
    except:
        page = ""
    return(page)

#https://github.com/learningit/Kodi-plugins-source/blob/master/plugin.video.thinktv/resources/lib/scraper.py
#modified from link above
def getAddonVideo(url,udata=None,headers=httpHeaders):
    html = getRequest(url)

    soup = BeautifulSoup(html,'lxml')
    vid_num = soup.findAll('span',attrs={'class': 'coveplayerid'})[0].text

    pg = getRequest('http://player.pbs.org/viralplayer/%s/' % (vid_num))
    urls = re.compile("PBS.videoData =.+?recommended_encoding.+?'url'.+?'(.+?)'.+?'closed_captions_url'.+?'(.+?)'", re.DOTALL).search(pg)

    try:
        url,suburl = urls.groups()
        pg = getRequest('%s?format=json' % url)
        url = json.loads(pg)['url']
    except:
        return []

    if 'mp4:' in url:
        url = 'http://ga.video.cdn.pbs.org/%s' % url.split('mp4:',1)[1]
    elif '.m3u8' in url:
        url = url.replace('800k','2500k')
        if 'hd-1080p' in url:
            url = url.split('-hls-',1)[0]
            url = url+'-hls-6500k.m3u8'
    return url

######################## Create list of videos ###################################
#http://kodi.wiki/view/HOW-TO:Video_addon
def list_videos(url = 'http://www.pbs.org/newshour/videos/'):
    html = getRequest(url)

    xbmc.log(url)

    soup = BeautifulSoup(html,'lxml')
    videos = soup.findAll('ul',attrs={'class': 'sidebar-popular-list'})[0].findAll('a') #make a list of all the links

    listing = []
    for vids in videos:
        info = vids.findAll('img')
        if len(info) == 0:
            continue
        else:
            info  = info[0]

        list_item = xbmcgui.ListItem(label=info['title'], thumbnailImage=info['src'])
        list_item.setInfo('video', {'title': info['title']})
        list_item.setProperty('IsPlayable', 'true')

        url = getAddonVideo(vids['href'])
        if len(url) == 0: #videos are initially uploaded as youtube vids
            continue

        is_folder = False

        listing.append((url, list_item, is_folder))

    # Add list to Kodi.
    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)

def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def router():
    params = dict(args)

    if params:
        if params['action'] == 'play':
            play_video(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_videos()


#if __name__ == '__main__':
router()
