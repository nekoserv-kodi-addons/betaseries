import re
from os import path
from sys import argv
from urllib.parse import quote
from urllib.parse import unquote

from _socket import setdefaulttimeout
from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from betaseries.subtitles.betaseries import self_betaseries_host, self_betaseries_api_version
from betaseries.subtitles.tmdb import get_imdb_id_from_tmdb
from betaseries.toolbox.http import get_url
from betaseries.toolbox.logger import log, send_user_notification
from betaseries.toolbox.strings import normalize_string, get_sub_team
from simplejson import loads
from xbmc import getInfoLabel, Player, getLanguage, convertLanguage, ISO_639_1, executeJSONRPC, ENGLISH_NAME
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem


def search_subs(params):
    item = {
        'tvshow': getInfoLabel("VideoPlayer.TVshowtitle"),
        'year': getInfoLabel("VideoPlayer.Year"),
        'season': getInfoLabel("VideoPlayer.Season"),
        'episode': getInfoLabel("VideoPlayer.Episode"),
        'path': unquote(Player().getPlayingFile()),
        'uilang': getLanguage(),
        'langs': []
    }
    # get user preferred languages for subtitles
    for lang in unquote(params['languages']).split(","):
        item['langs'].append(convertLanguage(lang, ISO_639_1))
    # remove rar:// or stack://
    if item['path'].find("rar://") > -1:
        item['path'] = path.dirname(item['path'][6:])
    elif item['path'].find("stack://") > -1:
        stack_path = item['path'].split(" , ")
        item['path'] = stack_path[0][8:]
    # show item data in debug log
    log("after item = %s" % item)
    # find playing mode
    if len(item['tvshow']) > 0:
        item['mode'] = "tvshow"
    elif item['year'] != "":
        item['mode'] = "movie"
    else:
        item['mode'] = "file"
    # search for subtitles
    search_subtitles(item)


def search_subtitles(search):
    subtitle_item = []
    log("entering search_subtitles()")
    if search['mode'] == "movie":
        log("movies not supported!")
        return False
    # get video file name
    if SettingService.get(SettingEnum.DIR_SYNC):
        # get directory name as filename
        filename = path.basename(path.dirname(search['path'])).lower()
    else:
        # or use filename
        filename = path.basename(search['path']).lower()
        # and remove file extension
        filename = re.sub(r"\.[^.]+$", "", filename)
    filename = normalize_string(filename)
    log("after filename = %s" % filename)
    # if "file", check if valid tv show
    if search['mode'] == "file" and not re.search(r"(?i)(s\d+e\d+|\d+x?\d{2,})", str(filename)):
        log("not a tv show or badly named!")
        return False
    # get subtitle team
    filename = filename.decode('UTF-8')
    sub_teams = get_sub_team(filename)
    # configure socket
    setdefaulttimeout(10)
    # define default url to get betaseries episode id from filename
    episode_url = "%s/episodes/scraper?file=%s&key=%s&v=%s" % (
        self_betaseries_host, quote(filename), SettingService.get(SettingEnum.BETASERIES_APIKEY), self_betaseries_api_version)
    # check video type
    if search['mode'] == "tvshow":
        # get player_id
        json_query = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        player_id = loads(executeJSONRPC(json_query))['result'][0]['playerid']
        # get tv_show_id
        json_query = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"playerid": ' + str(
            player_id) + ', "properties": ["tvshowid"]}, "id": 1}'
        tv_show_id = loads(executeJSONRPC(json_query))['result']['item']['tvshowid']
        # check result
        if tv_show_id > 0:
            # get tvdb_id
            json_query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": ' + str(
                tv_show_id) + ', "properties": ["imdbnumber"]}, "id": 1}'
            tvdb_id = loads(executeJSONRPC(json_query))
            log("result : %s" % repr(tvdb_id))
            # if we have tvdb_id, work with ids
            if 'result' in tvdb_id:
                # get tvdb_id (imdbnumber is a tmdb identifier)
                tvdb_id = tvdb_id['result']['tvshowdetails']['imdbnumber']
                imdb_id = get_imdb_id_from_tmdb(tvdb_id)
                # get betaseries show id from imdb_id
                show_url = "%s/shows/display?imdb_id=%s&key=%s&v=%s" % (self_betaseries_host,
                                                                        imdb_id,
                                                                        SettingService.get(SettingEnum.BETASERIES_APIKEY),
                                                                        self_betaseries_api_version)
                try:
                    show_id = loads(get_url(show_url))["show"]["id"]
                except:
                    log("could not parse data or fetch url for show_id, cannot continue")
                    return False
                log("after show_id = %s" % show_id)
                # then get betaseries episode id
                episode_url = "%s/episodes/search?show_id=%s&number=S%#02dE%#02d&key=%s&v=%s" % (
                    self_betaseries_host, show_id, int(search['season']), int(search['episode']),
                    SettingService.get(SettingEnum.BETASERIES_APIKEY), self_betaseries_api_version)
    try:
        episode_id = loads(get_url(episode_url))["episode"]["id"]
        log("after episode_id = %s" % episode_id)
    except:
        log("error or episode not found!")
        return False
    # then get subtitles list
    list_url = "%s/subtitles/episode?id=%s&key=%s&v=%s" % (
        self_betaseries_host, episode_id, SettingService.get(SettingEnum.BETASERIES_APIKEY), self_betaseries_api_version)
    try:
        data = loads(get_url(list_url))["subtitles"]
    except:
        log("could not parse data or fetch url, cannot continue")
        return False
    # for each release version
    log("parsing data after urlopen")
    log("--------------------------")
    for subtitle in data:
        # get filename
        sub_file = normalize_string(subtitle["file"])
        log("after sub_file = %s" % sub_file)
        # get file extension
        ext = sub_file.split(b'.')[-1].decode()
        # get season number from data
        season = int(subtitle["episode"]["season"])
        log("after season = %s" % season)
        # get episode number from data
        episode = int(subtitle["episode"]["episode"])
        log("after episode = %s" % episode)
        # get names of files contained in zip file, if any
        if len(subtitle["content"]) > 0:
            content = subtitle["content"]
        # or put filename in content
        else:
            content = [subtitle["file"]]
        log("after content = %s" % content)
        # for each file in content
        for sub_name in content:
            log("-------------")
            # subtitle file name
            sub_name = normalize_string(sub_name)
            log("after sub_name = %s" % sub_name)
            # subtitle download url
            link = subtitle["url"]
            log("after link = %s" % link)
            try:
                # normalize lang
                lang2 = {
                    "VO": "en",
                    "VF": "fr",
                    "VOVF": "xx",
                }[subtitle["language"]]
            except:
                log("unsupported language")
                continue
            # get note
            if 0 <= int(subtitle["quality"]) <= 5:
                note = int(subtitle["quality"])
            else:
                note = 0
            log("after note = %s" % note)
            # check if file is a subtitle
            sub_name = sub_name.decode('UTF-8')
            if len(re.findall(r'(?i)\.(srt|ssa|ass|sub)$', sub_name)) < 1:
                log("not a subtitle : %s" % sub_name)
                continue
            # if from a zip file
            if len(content) > 1:
                # check if file is for correct season and episode
                search_string = r"(?i)(s%#02de%#02d|%d%#02d|%dx%#02d)" % (
                    season, episode, season, episode, season, episode)
                if not re.search(search_string, sub_name):
                    log("file not matching episode : %s" % sub_name)
                    continue
                # get subtitle file lang
                langs = re.search(r"(?i)[ _.-](english|french|eng|fre|en|fr|vo|vf)[ _.-]", sub_name)
                # or get zip file lang
                if langs is None:
                    langs = lang2
                else:
                    langs = langs.group(1).lower()
                log("after zip langs = %s" % lang2)
                try:
                    lang2 = {
                        "french": 'fr',
                        "english": 'en',
                        "fre": 'fr',
                        "eng": 'en',
                        "fr": 'fr',
                        "en": 'en',
                        "vf": 'fr',
                        "vo": 'en'
                    }[langs]
                except:
                    log("unsupported language")
                    continue
                log("after zip lang2 = %s" % lang2)
            try:
                # get full language name
                lang_name = convertLanguage(lang2, ENGLISH_NAME)
            except:
                log("unsupported language")
                continue
            # if lang is user gui language
            if lang_name == search['uilang']:
                # put this file on top
                ui_lang = True
            else:
                ui_lang = False
            log("after lang = %s, lang2 = %s" % (lang_name, lang2))
            # check sync
            sync = False
            team = False
            for (key, sub_team) in enumerate(sub_teams):
                # if team corresponds
                if len(sub_team) > 0 and len(
                        re.findall(r"(?i)(^|[ _+.-])(" + sub_team + ")([ _+.-]|$)", sub_name)) > 0:
                    # set sync tag
                    sync = True
                    # if video file team match : use team
                    if key == 0:
                        team = True
            log("after sync = %s" % sync)
            # check if this is for hearing impaired
            if len(re.findall(r"(?i)[ _.-](CC|HI)[ _.-]", sub_name)) > 0:
                cc = True
            else:
                cc = False
            log("after cc = %s" % cc)
            # if language allowed by user
            if lang2 in search['langs']:
                # add subtitle to list
                subtitle_item.append(
                    {'uilang': ui_lang, 'ext': ext, 'filename': sub_name, 'link': link, 'lang': lang_name,
                     'lang2': lang2, "cc": cc, "sync": sync, "note": note, "team": team})
                log("subtitle added : %s" % sub_name)
        log("--------------------------")
    if subtitle_item:
        # get settings for sorting
        ui_first = SettingService.get(SettingEnum.UI_FIRST)
        cc_first = SettingService.get(SettingEnum.CC_FIRST)
        # sort accordingly
        log("sorting by filename asc")
        subtitle_item.sort(key=lambda x: [x['filename']])
        if not cc_first:
            log("sorting by cc last")
            subtitle_item.sort(key=lambda x: [x['cc']])
        log("sorting by note best")
        subtitle_item.sort(key=lambda x: [x['note']], reverse=True)
        log("sorting by lang asc")
        subtitle_item.sort(key=lambda x: [x['lang']])
        if cc_first:
            log("sorting by cc first")
            subtitle_item.sort(key=lambda x: [not x['cc']])
        if ui_first:
            log("sorting by uilang first")
            subtitle_item.sort(key=lambda x: [not x['uilang']])
        log("sorting by sync first")
        subtitle_item.sort(key=lambda x: [not x['sync']])
        log("sorting by team first")
        subtitle_item.sort(key=lambda x: [not x['team']])
        log("sorted subtitles = %s" % subtitle_item)
        # for each subtitle
        for sub_item in subtitle_item:
            # xbmc list item format
            sub_list_item = ListItem(label=sub_item["lang"], label2=sub_item["filename"])
            # set image and thumbnail
            sub_list_item.setArt({'icon': str(sub_item["note"]), 'thumb': sub_item["lang2"]})
            # setting sync / CC tag
            sub_list_item.setProperty("sync", 'true' if sub_item["sync"] else 'false')
            sub_list_item.setProperty("hearing_imp", 'true' if sub_item["cc"] else 'false')
            # adding item to GUI list
            url = "plugin://%s/?action=download&link=%s&ext=%s&filename=%s" % (
                SettingService.get(SettingEnum.ID), sub_item["link"], sub_item["ext"], quote(sub_item["filename"]))
            addDirectoryItem(handle=int(argv[1]), url=url, listitem=sub_list_item, isFolder=False)
    else:
        send_user_notification(30010)
        log("nothing found")
    log("end of search_subtitles()")