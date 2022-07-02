from os import path, listdir
from os.path import join
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from _socket import setdefaulttimeout
from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from xbmc import LOGERROR, executebuiltin

from .logger import log, send_user_notification
from .strings import normalize_string


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"


def get_url(url):
    req_headers = {
        'User-Agent': get_user_agent(),
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache'}
    request = Request(url, headers=req_headers)
    opener = build_opener()
    try:
        response = opener.open(request)
        contents = response.read()
        return contents
    except HTTPError as e:
        log('url = ' + url, LOGERROR)
        log('HTTPError = ' + str(e.code), LOGERROR)
        if e.code == 400:
            return None
    except URLError as e:
        log('URLError = ' + str(e.reason), LOGERROR)
    except:
        import traceback
        log('generic exception: ' + traceback.format_exc(), LOGERROR)
    # when error occurred
    send_user_notification(30008)
    return None


def download_subtitle(url, ext, subversion):
    tmpdir = SettingService.get(SettingEnum.TEMP_DIR)
    # name of temp file for download
    local_tmp_file = join(tmpdir, "betaseries." + ext)
    log("downloading url : %s" % url)
    setdefaulttimeout(15)
    content = get_url(url)

    if content is None:
        return False

    local_file_handle = open(local_tmp_file, "w" + "b")
    local_file_handle.write(content)
    local_file_handle.close()
    log("file extension is : %s" % ext)

    if ext not in ['zip', 'rar']:
        log("selected file : %s" % subversion)
        return local_tmp_file

    files = listdir(tmpdir)
    init_filecount = len(files)
    log("number of files : %s" % init_filecount)
    filecount = init_filecount
    log("extracting archive : %s" % local_tmp_file)
    executebuiltin("XBMC.Extract(" + local_tmp_file + "," + tmpdir + ")")
    wait_time = 0
    max_time = 30  # timeout for extraction = 3 seconds
    while (filecount == init_filecount) and (wait_time < max_time):  # nothing yet extracted
        sleep(0.1)  # wait 100ms to let the builtin function 'XBMC.extract' unpack
        files = listdir(tmpdir)
        filecount = len(files)
        wait_time = wait_time + 1
    # if max wait_time reached
    if wait_time == max_time:
        log("error unpacking files in : %s" % tmpdir)
    else:
        log("unpacked files in : %s" % tmpdir)
        sleep(0.1)
        files = listdir(tmpdir)
        log("looking for %s" % subversion)
        for filename in files:
            log("checking file %s" % filename)
            if normalize_string(filename) == subversion:
                filepath = path.normpath(path.join(tmpdir, filename))
                log("selected file : %s" % filename)
                return filepath
