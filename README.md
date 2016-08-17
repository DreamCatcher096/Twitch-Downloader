# Twitch-Downloader
A python script that can download twitch boardcasts and save it as a .ts file, compatible with the new-style VODs only.
Other python scripts doesn't work on my computer, especially those that uses wget, so I wrote one myself.
Programmed on Windows environment, python version 2.7.12
Uses some code from [twitch_downloader](https://github.com/ilyalissoboi/twitch_downloader), your code helped me a lot, thanks!

Probably will add a function to covert the .ts file to .mp4 file, and add a progress bar or something like it.

Variable names are a mess, I will make it better later.

Bug: sometimes some subprocess will hang for a while, currently to solve it you need to stop the program and delete the unfinished files and start it again, this will be solved in future updates.

Requires:
- [cement](https://pypi.python.org/pypi/cement/2.4.0)
- [m3u8](https://github.com/ilyalissoboi/m3u8)
- [requests](https://pypi.python.org/pypi/requests)
- [pycurl](https://pypi.python.org/pypi/pycurl/)
