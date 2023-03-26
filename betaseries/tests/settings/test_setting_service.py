from unittest import TestCase

from betaseries.settings.setting_enum import SettingEnum
from betaseries.settings.setting_service import SettingService


class TestSettingService(TestCase):

    def test_settings(self):
        actual_settings = {}
        for item in SettingEnum:
            actual_settings[item] = SettingService.get(item)
            with self.subTest(item.name + ' exists in settings'):
                self.assertTrue(item in actual_settings)
        with self.subTest('settings dict. length'):
            self.assertEqual(12, len(actual_settings))
