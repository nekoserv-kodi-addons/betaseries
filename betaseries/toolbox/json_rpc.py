from simplejson import loads as json_loads
from xbmc import executeJSONRPC

from betaseries.toolbox.logger import log


def get_player_id():
    json_query = "{'jsonrpc': '2.0', 'method': 'Player.GetActivePlayers', 'id': 1}"
    return json_loads(executeJSONRPC(json_query))['result'][0]['playerid']


def get_tv_show_id():
    # get player_id
    player_id = get_player_id()
    # get tv_show_id
    json_query = "{'jsonrpc': '2.0', 'method': 'Player.GetItem', 'params': {'playerid': " + str(
        player_id) + ", 'properties': ['tvshowid']}, 'id': 1}"
    tv_show_id = json_loads(executeJSONRPC(json_query))['result']['item']['tvshowid']
    # check result
    if tv_show_id > 0:
        return tv_show_id
    log('unable to get tvshowid')
    return None


def get_tvdb_id(tv_show_id):
    if not tv_show_id:
        return None
    json_query = "{'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShowDetails', 'params': {'tvshowid': " + str(
        tv_show_id) + ", 'properties': ['imdbnumber']}, 'id': 1}"
    tvdb_id = json_loads(executeJSONRPC(json_query))
    log('result : %s' % repr(tvdb_id))
    if 'result' not in tvdb_id:
        return None
    # return tvdb_id (imdbnumber is a tmdb identifier)
    return tvdb_id['result']['tvshowdetails']['imdbnumber']
