from urllib.parse import quote

from simplejson import loads as json_loads

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from betaseries.subtitles.tmdb import get_imdb_id_from_tmdb
from betaseries.toolbox.http import get_content_from_url
from betaseries.toolbox.json_rpc import get_tv_show_id, get_tvdb_id
from betaseries.toolbox.logger import log

self_betaseries_host = "https://api.betaseries.com"
self_betaseries_api_version = "3.0"


def search_episode_url(search_params):
    # initializations
    tv_show_id = get_tv_show_id()
    tvdb_id = get_tvdb_id(tv_show_id)
    imdb_id = get_imdb_id_from_tmdb(tvdb_id)
    show_id = get_show_id_from_betaseries(imdb_id)

    # then get betaseries episode id
    episode_url = "%s/episodes/search?show_id=%s&number=S%#02dE%#02d&key=%s&v=%s" % (
        self_betaseries_host, show_id, int(search_params['season']), int(search_params['episode']),
        SettingService.get(SettingEnum.BETASERIES_APIKEY), self_betaseries_api_version)
    return episode_url


def get_show_id_from_betaseries(imdb_id):
    # get betaseries show id from imdb_id
    show_url = "%s/shows/display?imdb_id=%s&key=%s&v=%s" % (self_betaseries_host,
                                                            imdb_id,
                                                            SettingService.get(SettingEnum.BETASERIES_APIKEY),
                                                            self_betaseries_api_version)
    try:
        show_id = json_loads(get_content_from_url(show_url))["show"]["id"]
    except:
        log("could not parse data or fetch url for show_id, cannot continue")
        return None
    log("show_id from betaseries = %s" % show_id)
    return show_id


def get_subtitles_from_betaseries(episode_id):
    # then get subtitles list
    list_url = "%s/subtitles/episode?id=%s&key=%s&v=%s" % (
        self_betaseries_host, episode_id, SettingService.get(SettingEnum.BETASERIES_APIKEY),
        self_betaseries_api_version)
    try:
        betaseries_subtitles = json_loads(get_content_from_url(list_url))["subtitles"]
    except:
        log("list_url : could not parse data or fetch url, cannot continue")
        return None
    return betaseries_subtitles


def generate_betaseries_url(search_params, filename):
    if search_params['mode'] == "tvshow":
        episode_url = search_episode_url(search_params)
    else:
        # define default url to get betaseries episode id from filename
        episode_url = "%s/episodes/scraper?file=%s&key=%s&v=%s" % (
            self_betaseries_host, quote(filename), SettingService.get(SettingEnum.BETASERIES_APIKEY),
            self_betaseries_api_version)
    return episode_url


def get_betaseries_episode_id(search_params, filename):
    # generate url
    episode_url = generate_betaseries_url(search_params, filename)
    try:
        episode_id = json_loads(get_content_from_url(episode_url))["episode"]["id"]
    except:
        log("episode_id : error or episode not found!")
        return None
    return episode_id
