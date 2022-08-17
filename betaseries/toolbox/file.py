
from os import path, listdir
from os.path import basename, dirname, join, normpath
from re import sub
from shutil import rmtree
from time import sleep

from betaseries.toolbox.logger import log
from xbmc import executebuiltin
from xbmcvfs import mkdirs

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService
from betaseries.toolbox.strings import normalize_string


def clean_temp_directory():
    temp_dir = SettingService.get(SettingEnum.TEMP_DIR)
    if path.exists(temp_dir):
        rmtree(temp_dir.encode("utf-8", "ignore"))
    mkdirs(temp_dir)


def get_filename(playing_file):
    if SettingService.get(SettingEnum.DIR_SYNC):
        # get directory name as filename
        filename = basename(dirname(playing_file)).lower()
    else:
        # or use filename
        filename = basename(playing_file).lower()
        # and remove file extension
        filename = sub(r"\.[^.]+$", "", filename)
    return normalize_string(filename)


def generate_tmp_file(extension):
    tmpdir = SettingService.get(SettingEnum.TEMP_DIR)
    return join(tmpdir, "betaseries." + extension)


def write_to_file(data, file):
    with open(file, 'wb') as f:
        f.write(data)


def extract_file(temp_file, filename):
    tmpdir = SettingService.get(SettingEnum.TEMP_DIR)
    files = listdir(tmpdir)
    nb_files_in_dir = len(files)
    log("number of files : %s" % nb_files_in_dir)
    filecount = nb_files_in_dir
    log("extracting archive : %s" % temp_file)
    executebuiltin("XBMC.Extract(" + temp_file + "," + tmpdir + ")")
    wait_time = 0
    time_threshold = 30  # timeout for extraction = 3 seconds
    while (filecount == nb_files_in_dir) and (wait_time < time_threshold):  # nothing yet extracted
        sleep(0.1)  # wait 100ms to let the builtin function 'XBMC.extract' unpack
        files = listdir(tmpdir)
        filecount = len(files)
        wait_time = wait_time + 1
    # if max wait_time reached
    if wait_time == time_threshold:
        log("error unpacking files in : %s" % tmpdir)
        return None
    log("unpacked files in : %s" % tmpdir)
    sleep(0.1)
    files = listdir(tmpdir)
    log("looking for %s" % filename)
    for filename in files:
        log("checking file %s" % filename)
        if normalize_string(filename) == filename:
            filepath = normpath(join(tmpdir, filename))
            log("selected file : %s" % filename)
            return filepath
    log("%s not found in archive" % filename)
    return None
