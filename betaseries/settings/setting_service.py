from os.path import join

from xbmcaddon import Addon
from xbmcvfs import translatePath

from betaseries.settings.setting_enum import SettingEnum


class SettingService:
    __settings = None

    @staticmethod
    def get(item):
        """init configuration if needed, then item from __settings"""
        # reload if needed
        if SettingService.__settings is None:
            SettingService.__load()
        # get item from settings
        return SettingService.__settings[item]

    @staticmethod
    def __load():
        """load all settings"""
        addon = Addon(id='service.subtitles.betaseries')

        profile = translatePath(addon.getAddonInfo('profile'))

        SettingService.__settings = {SettingEnum.ID: addon.getAddonInfo('id'),
                                     SettingEnum.NAME: addon.getAddonInfo('name'),
                                     SettingEnum.LANG: addon.getLocalizedString,
                                     SettingEnum.ICON: addon.getAddonInfo('icon'),
                                     SettingEnum.PROFILE: profile,
                                     SettingEnum.TEMP_DIR: translatePath(join(profile, 'temp', '')),
                                     SettingEnum.NOTIFY: addon.getSetting('notify') == 'true',
                                     SettingEnum.DIR_SYNC: addon.getSetting('dirsync') == 'true',
                                     SettingEnum.UI_FIRST: addon.getSetting('uifirst') == 'true',
                                     SettingEnum.CC_FIRST: addon.getSetting('ccfirst') == 'true',
                                     SettingEnum.BETASERIES_APIKEY: addon.getSetting('betaseries_apikey'),
                                     SettingEnum.TMDB_APIKEY: addon.getSetting('tmdb_apikey')}
