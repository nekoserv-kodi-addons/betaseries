from sys import argv
from urllib.parse import quote

from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from betaseries.toolbox.logger import log


def sort_subtitles(subtitle_item):
    # get settings for sorting
    ui_first = SettingService.get(SettingEnum.UI_FIRST)
    cc_first = SettingService.get(SettingEnum.CC_FIRST)
    # sort accordingly
    log('sorting by filename asc')
    subtitle_item.sort(key=lambda x: [x['filename']])
    if not cc_first:
        log('sorting by cc last')
        subtitle_item.sort(key=lambda x: [x['cc']])
    log('sorting by note best')
    subtitle_item.sort(key=lambda x: [x['note']], reverse=True)
    log('sorting by lang asc')
    subtitle_item.sort(key=lambda x: [x['lang']])
    if cc_first:
        log('sorting by cc first')
        subtitle_item.sort(key=lambda x: [not x['cc']])
    if ui_first:
        log('sorting by uilang first')
        subtitle_item.sort(key=lambda x: [not x['uilang']])
    log('sorting by sync first')
    subtitle_item.sort(key=lambda x: [not x['sync']])
    log('sorting by team first')
    subtitle_item.sort(key=lambda x: [not x['team']])
    log('sorted subtitles = %s' % subtitle_item)


def add_subtitles_to_gui(subtitle_item):
    for sub_item in subtitle_item:
        # xbmc list item format
        sub_list_item = ListItem(label=sub_item['lang'], label2=sub_item['filename'])
        # set image and thumbnail
        sub_list_item.setArt({'icon': str(sub_item['note']), 'thumb': sub_item['lang2']})
        # setting sync / CC tag
        sub_list_item.setProperty('sync', 'true' if sub_item['sync'] else 'false')
        sub_list_item.setProperty('hearing_imp', 'true' if sub_item['cc'] else 'false')
        # adding item to GUI list
        url = 'plugin://%s/?action=download&link=%s&ext=%s&filename=%s' % (
            SettingService.get(SettingEnum.ID), sub_item['link'], sub_item['ext'], quote(sub_item['filename']))
        addDirectoryItem(handle=int(argv[1]), url=url, listitem=sub_list_item, isFolder=False)
