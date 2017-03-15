# Kodi_addons
This is a repsitory of [kodi](https://kodi.tv/) addons that I have built.

* plugin.video.pbsnewshour-master is a plugin that I built from scratch. It's for watching [PBS NewsHour's](http://www.pbs.org/newshour/videos/) broadcasts from the past week. Most the work is done in the file default.py, which scrapes PBS's sites, finds links to the videos, and passes these links to Kodi so that users can watch them! This addon works great with PBS's videos, but PBS initially posts their videos as youtube links. I need to punch out some more code for handling the youtube links. Once I have everything completed, I'll publish a blog post detailing how everything in the addon works.

* plugin.video.pbsnewshouryoutube-master is a plugin that I built using the existing [youtube Kodi addon](http://kodi.wiki/view/Add-on:YouTube). This addon is also for watching PBS NewsHour. This addon works great, but I wanted to build an addon from scratch so I built the addon mentioned above. 
