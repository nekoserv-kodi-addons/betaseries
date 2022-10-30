from os.path import dirname
from re import findall, search
from urllib.parse import unquote

from xbmc import getInfoLabel, Player, getLanguage, convertLanguage, ISO_639_1, ENGLISH_NAME

from betaseries.subtitles.betaseries import get_subtitles_from_betaseries, get_betaseries_episode_id
from betaseries.toolbox.file import get_filename
from betaseries.toolbox.gui import sort_subtitles, add_subtitles_to_gui
from betaseries.toolbox.logger import log, send_user_notification
from betaseries.toolbox.string import normalize_string, get_sub_teams


def validate(search_params, filename):
    if search_params['mode'] == 'movie':
        log('movies not supported!')
        return False
    if search_params['mode'] == 'file' and not search(r'(?i)(s\d+e\d+|\d+x?\d{2,})', filename):
        log('not a tv show or badly named!')
        return False
    return True


def get_kodi_subtitles(search_params, filename, betaseries_subtitles):
    kodi_subtitles = []
    for betaseries_sub in betaseries_subtitles:
        # init
        sub_extension = normalize_string(betaseries_sub['file']).split('.')[-1]
        season = int(betaseries_sub['episode']['season'])
        episode = int(betaseries_sub['episode']['episode'])

        # get names from content (ZIP file) or directly from file
        if len(betaseries_sub['content']) > 0:
            subtitles = betaseries_sub['content']
        else:
            subtitles = [betaseries_sub['file']]

        # for each file in content
        for current_sub in subtitles:
            # subtitle file name
            sub_name = normalize_string(current_sub)
            try:
                # normalize lang
                lang2 = {
                    'VO': 'en',
                    'VF': 'fr',
                    'VOVF': 'xx',
                }[betaseries_sub['language']]
            except:
                log('unsupported language - from vo/vf/vovf')
                continue
            # get note
            if 0 <= int(betaseries_sub['quality']) <= 5:
                note = int(betaseries_sub['quality'])
            else:
                note = 0
            # check if file is a subtitle
            if len(findall(r'(?i)\.(srt|ssa|ass|sub)$', sub_name)) < 1:
                log('not a subtitle : %s' % sub_name)
                continue
            # if from a zip file
            if len(subtitles) > 1:
                # check if file is for correct season and episode
                search_string = r'(?i)(s%#02de%#02d|%d%#02d|%dx%#02d)' % (
                    season, episode, season, episode, season, episode)
                if not search(search_string, sub_name):
                    log('file not matching episode : %s' % sub_name)
                    continue
                # get subtitle file lang
                langs = search(r'(?i)[ _.-](english|french|eng|fre|en|fr|vo|vf)[ _.-]', sub_name)
                # or get zip file lang
                if langs is None:
                    langs = lang2
                else:
                    langs = langs.group(1).lower()
                log('langs from zip = %s' % langs)
                try:
                    lang2 = {
                        'french': 'fr',
                        'english': 'en',
                        'fre': 'fr',
                        'eng': 'en',
                        'fr': 'fr',
                        'en': 'en',
                        'vf': 'fr',
                        'vo': 'en'
                    }[langs]
                except:
                    log('unsupported language from extended langs')
                    continue
            try:
                # get full language name
                lang_name = convertLanguage(lang2, ENGLISH_NAME)
            except:
                log('unsupported language - with convertLanguage')
                continue
            # if lang is user gui language
            if lang_name == search_params['uilang']:
                # put this file on top
                ui_lang = True
            else:
                ui_lang = False
            # check sync
            sync = False
            team = False
            sub_teams = get_sub_teams(filename)
            for (key, sub_team) in enumerate(sub_teams):
                # if team corresponds
                if len(sub_team) > 0 and len(findall(r'(?i)(^|[ _+.-])(' + sub_team + ')([ _+.-]|$)', sub_name)) > 0:
                    # set sync tag
                    sync = True
                    # if video file team match : use team
                    if key == 0:
                        team = True
            # check if this is for hearing impaired
            if len(findall(r'(?i)[ _.-](CC|HI)[ _.-]', sub_name)) > 0:
                closed_caption = True
            else:
                closed_caption = False
            # if language allowed by user
            if lang2 in search_params['langs']:
                # add subtitle to list
                kodi_subtitles.append(
                    {'uilang': ui_lang, 'ext': sub_extension, 'filename': sub_name, 'link': betaseries_sub['url'],
                     'lang': lang_name, 'lang2': lang2, 'cc': closed_caption, 'sync': sync, 'note': note, 'team': team})
                log('subtitle added : %s' % sub_name)
    return kodi_subtitles


def search_subs(languages):
    log('entering search_subs()')

    # initialization
    search_params = get_search_params(languages)
    filename = get_filename(search_params['path'])

    # validation
    if validate(search_params, filename) is False:
        return

    # get episode id
    episode_id = get_betaseries_episode_id(search_params, filename)

    # get betaseries subtitles
    betaseries_subtitles = get_subtitles_from_betaseries(episode_id)

    # get subtitles for kodi GUI
    kodi_subtitles = get_kodi_subtitles(search_params, filename, betaseries_subtitles)

    # found nothing
    if not kodi_subtitles:
        send_user_notification(30010)
        log('nothing found')

    # sort and add subtitles
    sort_subtitles(kodi_subtitles)
    add_subtitles_to_gui(kodi_subtitles)

    log('end of search_subtitles()')


def get_search_params(languages):
    item = {
        'tvshow': getInfoLabel('VideoPlayer.TVshowtitle'),
        'year': getInfoLabel('VideoPlayer.Year'),
        'season': getInfoLabel('VideoPlayer.Season'),
        'episode': getInfoLabel('VideoPlayer.Episode'),
        'path': unquote(Player().getPlayingFile()),
        'uilang': getLanguage(),
        'langs': []
    }
    # get user preferred languages for subtitles
    for lang in unquote(languages).split(','):
        item['langs'].append(convertLanguage(lang, ISO_639_1))
    # remove rar:// or stack://
    if item['path'].find('rar://') > -1:
        item['path'] = dirname(item['path'][6:])
    elif item['path'].find('stack://') > -1:
        stack_path = item['path'].split(' , ')
        item['path'] = stack_path[0][8:]
    # show item data in debug log
    log('item search param = %s' % item)
    # find playing mode
    if len(item['tvshow']) > 0:
        item['mode'] = 'tvshow'
    elif item['year'] != '':
        item['mode'] = 'movie'
    else:
        item['mode'] = 'file'
    return item
