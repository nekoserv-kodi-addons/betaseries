from sys import argv
from urllib.parse import unquote

from betaseries.toolbox.http import download_subtitle
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem


def download_subs(params):
    # download link
    sub = download_subtitle(params["link"], params["ext"], unquote(params["filename"]))
    if sub:
        # xbmc handles moving and using the subtitle
        list_item = ListItem(label=sub)
        addDirectoryItem(handle=int(argv[1]), url=sub, listitem=list_item, isFolder=False)

# from betaseries.toolbox.http import download_subtitle
# from betaseries.toolbox.http import download_subtitle
