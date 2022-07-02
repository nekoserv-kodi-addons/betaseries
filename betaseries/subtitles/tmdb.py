from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from betaseries.toolbox.http import get_url
from betaseries.toolbox.logger import log, send_user_notification
from simplejson import loads as json_loads

self_tmdb_host = "https://api.themoviedb.org"
self_tmdb_api_version = "3"


def get_imdb_id_from_tmdb(tmdb_id):
    if SettingService.get(SettingEnum.TMDB_APIKEY) == "":
        send_user_notification(30012)
        return None

    imdb_url = "%s/%s/tv/%s?api_key=%s&append_to_response=external_ids" % (
        self_tmdb_host, self_tmdb_api_version, int(tmdb_id), SettingService.get(SettingEnum.TMDB_APIKEY))

    try:
        return json_loads(get_url(imdb_url))["external_ids"]["imdb_id"]
    except:
        log("could not parse data or fetch url for tmdb_id '%s', cannot continue" % int(tmdb_id))
        return None
