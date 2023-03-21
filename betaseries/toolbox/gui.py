from sys import argv
from urllib.parse import quote

from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService


def sort_subtitles(subtitles_list):
    # get settings for sorting
    ui_first = SettingService.get(SettingEnum.UI_FIRST)
    cc_first = SettingService.get(SettingEnum.CC_FIRST)
    # sort by filename
    sort_by_item(subtitles_list, 'filename')
    sort_by_item(subtitles_list, 'note', reverse=True)
    sort_by_item(subtitles_list, 'lang')
    if cc_first:
        sort_by_item(subtitles_list, 'cc')
    else:
        sort_by_item(subtitles_list, 'cc')
    if ui_first:
        sort_by_item(subtitles_list, 'uilang')
    sort_by_item(subtitles_list, 'sync')
    sort_by_item(subtitles_list, 'team')
    # log('sorted subtitles = %s' % subtitles_list)


def add_subtitles_to_gui(subtitles_list):
    for subtitle in subtitles_list:
        # convert to kodi ListItem()
        list_item = ListItem(label=subtitle['lang'], label2=subtitle['filename'])
        # set image and thumbnail
        list_item.setArt({'icon': str(subtitle['note']), 'thumb': subtitle['lang2']})
        # setting sync / CC tag
        list_item.setProperty('sync', 'true' if subtitle['sync'] else 'false')
        list_item.setProperty('hearing_imp', 'true' if subtitle['cc'] else 'false')
        # adding item to GUI list
        url = 'plugin://%s/?action=download&link=%s&ext=%s&filename=%s' % (
            SettingService.get(SettingEnum.ID), subtitle['link'], subtitle['ext'], quote(subtitle['filename']))
        addDirectoryItem(handle=int(argv[1]), url=url, listitem=list_item, isFolder=False)


def sort_by_item(subtitles_list, item, reverse=False):
    direction = 'last' if reverse else 'first'
    print('sorting by ' + item + ' ' + direction)
    subtitles_list.sort(key=lambda x: [x[item]], reverse=reverse)
