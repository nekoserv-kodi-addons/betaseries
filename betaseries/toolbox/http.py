from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from _socket import setdefaulttimeout
from xbmc import LOGERROR

from betaseries.toolbox.file import generate_tmp_file, write_to_file, extract_file
from betaseries.toolbox.logger import log, send_user_notification


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"


def get_content_from_url(url):
    setdefaulttimeout(10)
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
        from traceback import format_exc
        log('generic exception: ' + format_exc(), LOGERROR)
    # when error occurred
    send_user_notification(30008)
    return None


def download_subtitle(url, ext, filename):
    log("downloading url : %s" % url)
    setdefaulttimeout(10)
    content = get_content_from_url(url)

    if not content:
        return None

    temp_file = generate_tmp_file(ext)
    write_to_file(content, temp_file)

    log("file extension is : %s" % ext)

    if ext not in ['zip', 'rar']:
        log("selected file : %s" % filename)
        return temp_file

    return extract_file(temp_file, filename)
