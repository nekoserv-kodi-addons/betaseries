import re
import shutil
from os import path, listdir
from sys import path as sys_path, argv
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import Request, build_opener

import simplejson as json
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from _socket import setdefaulttimeout
from unicodedata import normalize

__addon__ = xbmcaddon.Addon(id='service.subtitles.betaseries')
__addon_id__ = __addon__.getAddonInfo('id')
__addon_name__ = __addon__.getAddonInfo('name')
__addon_version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__language__ = __addon__.getLocalizedString
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__temp__ = xbmcvfs.translatePath(path.join(__profile__, 'temp'))

sys_path.append(path.join(__profile__, "lib"))

self_betaseries_host = "https://api.betaseries.com"
self_betaseries_apikey = __addon__.getSetting('betaseries_apikey')
self_api_version = "3.0"

self_tmdb_host = "https://api.themoviedb.org"
self_tmdb_api_version = "3"
self_tmdb_apikey = __addon__.getSetting('tmdb_apikey')

self_team_pattern = re.compile(r".*-([^-]+)$")
self_notify = __addon__.getSetting('notify') == 'true'

# equivalent of SD teams to HD teams
TEAMS = (
    # SD[0]              HD[1]
    ("lol|sys|dim", "dimension"),
    ("asap|xii|fqm|imm", "immerse|orenji"),
    ("excellence", "remarkable"),
    ("2hd|xor", "ctu"),
    ("tla", "bia"))

# equivalent language strings
LANGUAGES = (
    # [0]  [1]
    ("br", "pt"),
    ("gr", "el"))


def other_team(team, team_from, team_to):
    # get other team using TEAMS table
    for x in TEAMS:
        if len(re.findall(x[team_from], team)) > 0:
            return x[team_to]
    # return team if not found
    log("other team not found")
    return team


def normalize_string(to_normalize):
    return normalize('NFKD', to_normalize).encode('ascii', 'ignore')


def log(txt, level=xbmc.LOGDEBUG):
    message = '%s: %s' % (__addon_id__, txt)
    xbmc.log(msg=message, level=level)


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"


def init_params():
    init_param = []
    if len(argv[2]) >= 2:
        cleaned_params = argv[2].replace('?', '')
        pairs_of_params = cleaned_params.split('&')
        init_param = {}
        for i in range(len(pairs_of_params)):
            splitparams = pairs_of_params[i].split('=')
            if (len(splitparams)) == 2:
                init_param[splitparams[0]] = splitparams[1]
    return init_param


def get_url(url, referer=self_betaseries_host):
    req_headers = {
        'User-Agent': get_user_agent(),
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Referer': referer}
    request = Request(url, headers=req_headers)
    opener = build_opener()
    try:
        response = opener.open(request)
        contents = response.read()
        return contents
    except HTTPError as e:
        log('url = ' + url, xbmc.LOGERROR)
        log('HTTPError = ' + str(e.code), xbmc.LOGERROR)
        if e.code == 400:
            return None
    except URLError as e:
        log('URLError = ' + str(e.reason), xbmc.LOGERROR)
    except:
        import traceback
        log('generic exception: ' + traceback.format_exc(), xbmc.LOGERROR)
    # when error occurred
    if self_notify:
        xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % (__addon_name__, __language__(30008), 750, __icon__)))
    return None


def download_subtitle(url, ext, subversion, referer):
    # name of temp file for download
    local_tmp_file = path.join(__temp__, "betaseries." + ext)
    log("downloading url : %s" % url)
    setdefaulttimeout(15)
    content = get_url(url, referer)
    if content is not None:
        local_file_handle = open(local_tmp_file, "w" + "b")
        local_file_handle.write(content)
        local_file_handle.close()
        log("file extension is : %s" % ext)
        if ext in ['zip', 'rar']:
            files = listdir(__temp__)
            init_filecount = len(files)
            log("number of files : %s" % init_filecount)
            filecount = init_filecount
            log("extracting zip file : %s" % local_tmp_file)
            xbmc.executebuiltin("XBMC.Extract(" + local_tmp_file + "," + __temp__ + ")")
            wait_time = 0
            max_time = 30  # timeout for extraction = 3 seconds
            while (filecount == init_filecount) and (wait_time < max_time):  # nothing yet extracted
                sleep(0.1)  # wait 100ms to let the builtin function 'XBMC.extract' unpack
                files = listdir(__temp__)
                filecount = len(files)
                wait_time = wait_time + 1
            # if max wait_time reached
            if wait_time == max_time:
                log("error unpacking files in : %s" % __temp__)
            else:
                log("unpacked files in : %s" % __temp__)
                sleep(0.1)
                files = listdir(__temp__)
                log("looking for %s" % subversion)
                for filename in files:
                    log("checking file %s" % filename)
                    if normalize_string(filename) == subversion:
                        filepath = path.normpath(path.join(__temp__, filename))
                        log("selected file : %s" % filename)
                        return filepath
        else:
            log("selected file : %s" % subversion)
            return local_tmp_file
    else:
        return False


def get_imdb_id_from_tmdb(tmdb_id):
    if self_tmdb_apikey == "":
        xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % (__addon_name__, __language__(30012), 750, __icon__)))
        return None

    imdb_url = "%s/%s/tv/%s?api_key=%s&append_to_response=external_ids" % (
        self_tmdb_host, self_tmdb_api_version, int(tmdb_id), self_tmdb_apikey)

    try:
        return json.loads(get_url(imdb_url))["external_ids"]["imdb_id"]
    except:
        log("could not parse data or fetch url for tmdb_id '%s', cannot continue" % int(tmdb_id))
        return None


def search_subtitles(search):
    subtitle_item = []
    log("entering search_subtitles()")
    if search['mode'] == "movie":
        log("movies not supported!")
        return False
    # get video file name
    dirsync = __addon__.getSetting('dirsync') == 'true'
    if dirsync:
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
    sub_teams = [filename.replace(".", "-")]
    if len(sub_teams[0]) > 0:
        # get team name (everything after "-")
        sub_teams[0] = self_team_pattern.match("-" + sub_teams[0]).groups()[0].lower()
        # find equivalent teams, if any
        tmp = other_team(sub_teams[0], 0, 1)
        if len(tmp) > 0 and tmp != sub_teams[0]:
            sub_teams.append(tmp)
        # find other equivalent teams, if any
        tmp = other_team(sub_teams[0], 1, 0)
        if len(tmp) > 0 and tmp != sub_teams[0]:
            sub_teams.append(tmp)
    log("after sub_teams = %s" % sub_teams)
    # configure socket
    setdefaulttimeout(10)
    # define default url to get betaseries episode id from filename
    episode_url = "%s/episodes/scraper?file=%s&key=%s&v=%s" % (
        self_betaseries_host, quote(filename), self_betaseries_apikey, self_api_version)
    # check video type
    if search['mode'] == "tvshow":
        # get player_id
        json_query = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        player_id = json.loads(xbmc.executeJSONRPC(json_query))['result'][0]['playerid']
        # get tv_show_id
        json_query = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"playerid": ' + str(
            player_id) + ', "properties": ["tvshowid"]}, "id": 1}'
        tv_show_id = json.loads(xbmc.executeJSONRPC(json_query))['result']['item']['tvshowid']
        # check result
        if tv_show_id > 0:
            # get tvdb_id
            json_query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": ' + str(
                tv_show_id) + ', "properties": ["imdbnumber"]}, "id": 1}'
            tvdb_id = json.loads(xbmc.executeJSONRPC(json_query))
            log("result : %s" % repr(tvdb_id))
            # if we have tvdb_id, work with ids
            if 'result' in tvdb_id:
                # get tvdb_id (imdbnumber is a tmdb identifier)
                tvdb_id = tvdb_id['result']['tvshowdetails']['imdbnumber']
                imdb_id = get_imdb_id_from_tmdb(tvdb_id)
                # get betaseries show id from imdb_id
                show_url = "%s/shows/display?imdb_id=%s&key=%s&v=%s" % (self_betaseries_host,
                                                                        imdb_id, self_betaseries_apikey,
                                                                        self_api_version)
                try:
                    show_id = json.loads(get_url(show_url))["show"]["id"]
                except:
                    log("could not parse data or fetch url for show_id, cannot continue")
                    return False
                log("after show_id = %s" % show_id)
                # then get betaseries episode id
                episode_url = "%s/episodes/search?show_id=%s&number=S%#02dE%#02d&key=%s&v=%s" % (
                    self_betaseries_host, show_id, int(search['season']), int(search['episode']),
                    self_betaseries_apikey, self_api_version)
    try:
        episode_id = json.loads(get_url(episode_url))["episode"]["id"]
        log("after episode_id = %s" % episode_id)
    except:
        log("error or episode not found!")
        return False
    # then get subtitles list
    list_url = "%s/subtitles/episode?id=%s&key=%s&v=%s" % (
        self_betaseries_host, episode_id, self_betaseries_apikey, self_api_version)
    try:
        data = json.loads(get_url(list_url))["subtitles"]
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
                lang_name = xbmc.convertLanguage(lang2, xbmc.ENGLISH_NAME)
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
        ui_first = __addon__.getSetting('uifirst') == 'true'
        cc_first = __addon__.getSetting('ccfirst') == 'true'
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
            sub_list_item = xbmcgui.ListItem(label=sub_item["lang"], label2=sub_item["filename"])
            # set image and thumbnail
            sub_list_item.setArt({'icon': str(sub_item["note"]), 'thumb': sub_item["lang2"]})
            # setting sync / CC tag
            sub_list_item.setProperty("sync", 'true' if sub_item["sync"] else 'false')
            sub_list_item.setProperty("hearing_imp", 'true' if sub_item["cc"] else 'false')
            # adding item to GUI list
            url = "plugin://%s/?action=download&link=%s&ext=%s&filename=%s" % (
                __addon_id__, sub_item["link"], sub_item["ext"], quote(sub_item["filename"]))
            xbmcplugin.addDirectoryItem(handle=int(argv[1]), url=url, listitem=sub_list_item, isFolder=False)
    else:
        if self_notify:
            xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % (__addon_name__, __language__(30010), 750, __icon__)))
        log("nothing found")
    log("end of search_subtitles()")


# start of script

# clean up
if path.exists(__temp__):
    log("deleting temp tree...")
    shutil.rmtree(__temp__.encode("utf-8", "ignore"))
log("recreating temp dir...")
xbmcvfs.mkdirs(__temp__)

# get params
params = init_params()

# called when user is searching for subtitles
if params['action'] == 'search':
    item = {
        'tvshow': xbmc.getInfoLabel("VideoPlayer.TVshowtitle"),
        'year': xbmc.getInfoLabel("VideoPlayer.Year"),
        'season': xbmc.getInfoLabel("VideoPlayer.Season"),
        'episode': xbmc.getInfoLabel("VideoPlayer.Episode"),
        'path': unquote(xbmc.Player().getPlayingFile()),
        'uilang': xbmc.getLanguage(),
        'langs': []
    }
    # get user preferred languages for subtitles
    for lang in unquote(params['languages']).split(","):
        item['langs'].append(xbmc.convertLanguage(lang, xbmc.ISO_639_1))
    # remove rar:// or stack://
    if item['path'].find("rar://") > -1:
        item['path'] = path.dirname(item['path'][6:])
    elif item['path'].find("stack://") > -1:
        stackPath = item['path'].split(" , ")
        item['path'] = stackPath[0][8:]
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

# called when user clicks on a subtitle
elif params['action'] == 'download':
    # download link
    sub = download_subtitle(params["link"], params["ext"], unquote(params["filename"]), self_betaseries_host)
    if sub:
        # xbmc handles moving and using the subtitle
        list_item = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(handle=int(argv[1]), url=sub, listitem=list_item, isFolder=False)

xbmcplugin.endOfDirectory(int(argv[1]))
