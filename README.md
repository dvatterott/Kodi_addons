# Kodi_addons
This is a repsitory of [kodi](https://kodi.tv/) addons that I have built.

* **plugin.video.pbsnewshour** is a plugin that I built for watching [PBS NewsHour's](http://www.pbs.org/newshour/videos/) broadcasts. Most the work is done in the file default.py, which scrapes PBS's sites, finds links to the videos, and passes these links to Kodi so that users can watch them! The addon requires Kodi's [youtube addon](http://kodi.wiki/view/Add-on:YouTube). I wrote a [blog post](http://www.danvatterott.com/blog/2017/03/11/my-first-kodi-addon-pbs-newshour/) describing how the addon works.

* **plugin.video.pbsnewshouryoutube** is a plugin that I built using the existing [youtube Kodi addon](http://kodi.wiki/view/Add-on:YouTube). This addon is also for watching PBS NewsHour. This addon works great, but I wanted to build an addon from scratch so I built the addon mentioned above. This addon also requires Kodi's youtube addon.

* **repository.dvatterott** is the xml file and icon associated with my kodi repository (basically a lookup table that kodi can use to find my addons on the web).

* **_repo** is a folder with a subfolder for my repository and each plugin. The subfolders contain .zip files that Kodi uses to install the plugins. I used code from [Twilight0's](https://github.com/Twilight0/Repository-Bootstrapper) to build the contents of this folder and my repository structure. If you want to install my repository, grab the zip file in ./\_repo/repository.dvatterott/. These folders also have some info that Kodi displays when users decide whether to install a plugin.

[NOTE FOR ME]: update repo by running python generate_repo.py from ./_tools in a python2 environment.
