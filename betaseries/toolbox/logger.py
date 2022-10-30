from xbmc import log as xbmc_log, LOGDEBUG, executebuiltin

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService


def log(txt, level=LOGDEBUG):
    message = '%s: %s' % (SettingService.get(SettingEnum.ID), txt)
    print(message)
    xbmc_log(msg=message, level=level)


def send_user_notification(msg_id):
    if SettingService.get(SettingEnum.NOTIFY):
        executebuiltin(('Notification(%s,%s,%s,%s)' % (
            SettingService.get(SettingEnum.NAME), SettingService.get(SettingEnum.LANG)(msg_id), 750,
            SettingService.get(SettingEnum.ICON))))
