import shutil
from os import path

import xbmcvfs
from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService


def clean_temp_directory():
    temp_dir = SettingService.get(SettingEnum.TEMP_DIR)
    if path.exists(temp_dir):
        shutil.rmtree(temp_dir.encode("utf-8", "ignore"))
    xbmcvfs.mkdirs(temp_dir)
