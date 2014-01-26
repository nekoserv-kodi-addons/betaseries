# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

import urllib, urllib2, socket, hashlib, time
import xbmc, xbmcgui, xbmcaddon
from xml.dom import minidom
import simplejson as json

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString

socket.setdefaulttimeout(10)

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def get_urldata(url, urldata, method):
    # create a handler
    handler = urllib2.HTTPSHandler()
    # create an openerdirector instance
    opener = urllib2.build_opener(handler)
    # encode urldata
    body = urllib.urlencode(urldata)
    # build a request
    req = urllib2.Request(url, data=body)
    # add any other information you want
    req.add_header('Accept', 'application/json')
    # overload the get method function
    req.get_method = lambda: method
    try:
        #response = urllib2.urlopen(req)
        connection = opener.open(req)
    except urllib2.HTTPError,e:
        connection = e
    if connection.code:
        response = connection.read()
        return response
    else:
        log('#DEBUG# response empty')
        return 0

class Main:
    def __init__( self ):
        self._service_setup()
        while (not xbmc.abortRequested):
            xbmc.sleep(1000)

    def _service_setup( self ):
        self.apikey       = '16e587ee3891'
        self.apiurl       = 'https://api.betaseries.com'
        self.apiver       = '2.2'
        self.UserAgent    = 'Mozilla/5.0 (compatible; ' + __addonname__ + ' ' + __addonversion__ + '; XBMC)'
        self.Monitor      = MyMonitor(action = self._get_settings)
        urllib._urlopener = AppURLopener(agent = self.UserAgent)
        self._get_settings()

    def _get_settings( self ):
        log('#DEBUG# reading settings')
        service    = []
        BetaActive = __addon__.getSetting('betaactive') == 'true'
        BetaFirst  = __addon__.getSetting('betafirst') == 'true'
        BetaUser   = __addon__.getSetting('betauser')
        BetaPass   = __addon__.getSetting('betapass')
        BetaBulk   = __addon__.getSetting('betabulk') == 'true'
        BetaMark   = __addon__.getSetting('betamark') == 'true'
        BetaUnMark = __addon__.getSetting('betaunmark') == 'true'
        BetaFollow = __addon__.getSetting('betafollow') == 'true'
        if BetaActive and BetaUser and BetaPass:
            # [service, api-url, api-key, user, pass, first-only, token, auth-fail, failurecount, timercounter, timerexpiretime, bulk, mark, unmark, follow]
            service = ['betaseries', self.apiurl, self.apikey, BetaUser, BetaPass, BetaFirst, '', False, 0, 0, 0, BetaBulk, BetaMark, BetaUnMark, BetaFollow]
            self.Player = MyPlayer(action = self._service_betaserie, service = service)

    def _service_betaserie( self, episode, service ):
        tstamp = int(time.time())
        # don't proceed if we had an authentication failure
        if not service[7]:
            # test if we are authenticated
            if not service[6]:
                # authenticate                    
                service = self._service_authenticate(service, str(tstamp))
            # only proceed if authentication was succesful
            if service[6]:
                # mark as watched if we still have a valid session key after submission and have episode info
                if episode[0] and episode[1]:
                    # first-only check
                    if not service[5] or (service[5] and episode[2] <= 1):
                        # mark as watched
                        service = self._service_mark(service, episode)

    def _service_authenticate( self, service, timestamp ):
        # don't proceed if timeout timer has not expired
        if service[10] > int(timestamp):
            return service
        # create a pass hash
        md5pass = hashlib.md5()
        md5pass.update(service[4])
        url = service[1] + '/members/auth'
        urldata = {'v':self.apiver, 'key':service[2], 'login':service[3], 'password':md5pass.hexdigest()}
        try:
            # authentication request
            response = get_urldata(url, urldata, "POST")
            # authentication response
            data = json.loads(response)
            log('#DEBUG# successfully authenticated')
        except:
            service = self._service_fail( service, True )
            log('%s: failed to connect for authentication' % service[0])
            return service         
        # parse results
        if 'token' in data:
            # get token
            service[6] = str(data['token'])
            # reset failure count
            service[8] = 0
            # reset timer
            service[9] = 0
            service[10] = 0
        elif data['errors'][0]['code'] < 2000:
            # API error
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('BetaSeries', __language__(32002))).encode('utf-8', 'ignore'))
            log('%s: bad API usage' % service[0])
            # disable the service, the monitor class will pick up the changes
            __addon__.setSetting('betaactive', 'false')
        elif data['errors'][0]['code'] < 3000:
            # user has to change username / password
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('BetaSeries', __language__(32001))).encode('utf-8', 'ignore'))
            log('%s: invalid credentials' % service[0])
            service[7] = True
        else:
            # temporary server error
            service = self._service_fail( service, True )
            log('%s: server error while authenticating: %s' % (service[0], response))
        return service

    def _service_mark( self, service, episode ):
        # abort if betamark = false and playcount > 0 and play = false
        if not service[12] and episode[2] > 0 and not episode[3]:
            log("#DEBUG# abort marking, as play = %s" % episode[3])
            return service
        # abort if betaunmark = false and playcount = 0 and play = false
        elif not service[13] and episode[2] == 0 and not episode[3]:
            log("#DEBUG# abort unmarking, as play = %s" % episode[3])
            return service            
        # follow show if BetaFollow = true
        if service[14]:
            url = service[1] + "/shows/show"
            urldata = {'v':self.apiver, 'key':service[2], 'token':service[6], 'thetvdb_id':episode[0]}
            try:
                # marking request
                response = get_urldata(url, urldata, "POST")
                # marking response
                data = json.loads(response)
            except:
                service = self._service_fail( service, False )
                log('%s: failed to follow show %s' % (service[0], episode[4]))
                return service
            # parse results
            if data['errors']:
                log("%s: encountered error : %s %s" % (service[0], data['errors'][0]['code'], data['errors'][0]['text']))
                if data['errors'][0]['code'] == 2001:
                    # drop our session key
                    service[6] = ''
                    log('%s: bad token' % service[0])
                    return service
                elif data['errors'][0]['code'] == 2003:
                    log('%s: already following show %s' % (service[0], episode[4]))
                else:
                    log('%s: failed to follow show %s : %s' % (service[0], episode[4], data['errors'][0]['text']))
                    return service
            else:
                log('#DEBUG# now following show %s' % (episode[4]))
        # mark episode as watched
        url = service[1] + "/episodes/watched"
        urldata = {'v':self.apiver, 'key':service[2], 'token':service[6], 'thetvdb_id':episode[1]}
        if service[11]:
            urldata.update({'bulk': 1})
        if episode[2] == 0:
            method = "DELETE"
            act = "unwatched"
        else:
            method = "POST"
            act = "watched"
        try:
            # marking request
            response = get_urldata(url, urldata, method)
            # marking response
            data = json.loads(response)
        except:
            service = self._service_fail( service, False )
            log('%s: failed to mark as %s' % (service[0], act))
            return service
        # parse results
        if data['errors']:
            log("%s: encountered error : %s %s" % (service[0], data['errors'][0]['code'], data['errors'][0]['text']))
            if data['errors'][0]['code'] == 2001:
                # drop our session key
                service[6] = ''
                log('%s: bad token for mark as %s' % (service[0], act))
            elif data['errors'][0]['code'] == 0:
                log('%s: not following show, or episode %s already marked as %s' % (service[0], episode[1], act))
            else:
                log('%s: error marking episode %s as %s : %s' % (service[0], episode[1], act, data['errors'][0]['text']))
        else:
            log('#DEBUG# episode %s marked as %s' % (episode[1], act))
        return service

    def _service_fail( self, service, timer ):
        timestamp = int(time.time())
        # increment failure counter
        service[8] += 1
        # drop our session key if we encouter three failures
        if service[8] > 2:
            service[6] = ''
        # set a timer if failure occurred during authentication phase
        if timer:
            # wrap timer if we cycled through all timeout values
            if service[9] == 0 or service[9] == 7680:
                service[9] = 60
            else:
                # increment timer
                service[9] = 2 * service[9]
        # set timer expire time
        service[10] = timestamp + service[9]
        return service

# monitor notifications
class MyPlayer(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']
        self.service = kwargs['service']
        self.Play = False
        log('#DEBUG# Player Class Init')

    def onNotification( self, sender, method, data ):
        if sender == 'xbmc':
            if method == 'Player.OnPlay':
                result = json.loads(data)
                if 'item' in result:
                    if result['item']['type'] == 'episode':
                        log("#DEBUG# watching episode, id = %s" % result['item']['id'])
                        self.Play = True
            elif method == 'Player.OnStop':
                xbmc.sleep(2000)
                log("#DEBUG# stopped playback")
                self.Play = False
            elif method == 'VideoLibrary.OnUpdate':
                result = json.loads(data)
                if 'playcount' in result:
                    if 'item' in result and result['item']['type'] == 'episode':
                        log("#DEBUG# episode status changed, id = %s, playcount = %s" % (result['item']['id'], result['playcount']))
                        episode = self._get_info(result['item']['id'], result['playcount'], self.Play)
                        # mark as watched or not, depending on playcount
                        self.action(episode, self.service)
                        self.Play = False

    def _get_info( self, episodeid, playcount, playstatus ):
        tvshow_query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"episodeid": ' + str(episodeid) + ', "properties": ["tvshowid", "showtitle", "season", "episode"]}, "id": 1}'
        tvshow = json.loads(xbmc.executeJSONRPC (tvshow_query))['result']['episodedetails']

        tvdbid_query = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"tvshowid": ' + str(tvshow['tvshowid']) + ', "properties": ["imdbnumber"]}, "id": 1}'
        tvdbid = json.loads(xbmc.executeJSONRPC (tvdbid_query))['result']['tvshowdetails']['imdbnumber']
        
        url = self.service[1] + '/shows/episodes'
        urldata = '?v=2.2&key=' + self.service[2] + '&thetvdb_id=' + str(tvdbid) + '&season=' + str(tvshow['season']) + '&episode=' + str(tvshow['episode'])
        tvdbepid_query = get_urldata(url + urldata, '', "GET")
        tvdbepid = json.loads(tvdbepid_query)['episodes'][0]['thetvdb_id']

        epinfo = [int(tvdbid), int(tvdbepid), int(playcount), bool(playstatus), str(tvshow['showtitle']), int(tvshow['season']), int(tvshow['episode'])]
        log('#DEBUG# episode info: %s' % epinfo)
        return epinfo

# monitor settings change
class MyMonitor(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']

    def onSettingsChanged( self ):
        log('#DEBUG# onSettingsChanged')
        self.action()

# change default user-agent
class AppURLopener(urllib.FancyURLopener):
    def __init__( self, *args, **kwargs ):
        self.agent = kwargs['agent']
        version = self.agent

# start script
if ( __name__ == "__main__" ):
    log('script version %s started' % __addonversion__)
    Main()