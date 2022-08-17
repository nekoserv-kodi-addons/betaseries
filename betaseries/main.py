from sys import argv

from xbmcplugin import endOfDirectory

from betaseries.actions.download_subs import download_subs
from betaseries.actions.search_subs import search_subs
from betaseries.toolbox.file import clean_temp_directory
from betaseries.toolbox.params import get_params

if __name__ == '__main__':
    # clean temp directory
    clean_temp_directory()

    # get params
    params = get_params()

    # called when user is searching for subtitles
    if params['action'] == 'search':
        search_subs(params['languages'])
    # called when user clicks on a subtitle
    elif params['action'] == 'download':
        download_subs(params)

    # end of directory
    endOfDirectory(int(argv[1]))
