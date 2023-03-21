from unittest import TestCase
from unittest.mock import patch, MagicMock

from betaseries.settings.setting_service import SettingService


def mock_addon_method(item):
    return item


class TestSettingService(TestCase):

    @patch('betaseries.settings.setting_service.Addon.getAddonInfo', MagicMock(return_value=mock_addon_method))
    def test_get(self, mock_addon):
        # mock_addon.getAddonInfo.return_value = mock_addon_method
        # mock_addon.getLocalizedString.return_value = mock_addon_method('locale')
        # mock_addon.getSetting.return_value = mock_addon_method

        param_list = [
            'profile', 'id', 'name', 'locale', 'icon', 'notify', 'dirsync', 'uifirst', 'ccfirst', 'betaseries_apikey',
            'tmdb_apikey'
        ]
        for item in param_list:
            with self.subTest(item):
                self.assertEqual(item, SettingService.get(item))