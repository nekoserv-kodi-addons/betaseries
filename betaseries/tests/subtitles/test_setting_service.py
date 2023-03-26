from unittest import TestCase
from unittest.mock import patch

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService


class TestSettingService(TestCase):

    def mock_addon_method(self, item):
        return item

    @patch('betaseries.settings.setting_service.Addon.getAddonInfo', new=mock_addon_method)
    @patch('betaseries.settings.setting_service.Addon.getSetting', new=mock_addon_method)
    @patch('betaseries.settings.setting_service.Addon.getLocalizedString', 'lang')
    @patch('betaseries.settings.setting_service.Addon.getSetting', new=mock_addon_method)
    # @patch('betaseries.settings.setting_service.translatePath', MagicMock(return_value='profile'))
    def test_get(self):

        for item in SettingEnum:
            with self.subTest(item):
                self.assertEqual(item.name.lower(), SettingService.get(item))