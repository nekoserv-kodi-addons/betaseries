from sys import argv

import xbmcplugin
from betaseries.actions.download_subs import download_subs
from betaseries.actions.search_subs import search_subs
from betaseries.toolbox.file import clean_temp_directory
from betaseries.toolbox.params import get_params


def main():
    # clean temp directory
    clean_temp_directory()

    # get params
    params = get_params()

    # called when user is searching for subtitles
    if params['action'] == 'search':
        search_subs(params)
    # called when user clicks on a subtitle
    elif params['action'] == 'download':
        download_subs(params)

    xbmcplugin.endOfDirectory(int(argv[1]))
