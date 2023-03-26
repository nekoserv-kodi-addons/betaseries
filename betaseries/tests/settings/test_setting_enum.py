from unittest import TestCase

from betaseries.settings.setting_enum import SettingEnum


class TestSettingEnum(TestCase):
    def test_setting_enum(self):
        enum_dict = {
            'ID': 1,
            'NAME': 2,
            'LANG': 3,
            'ICON': 4,
            'PROFILE': 5,
            'TEMP_DIR': 6,
            'NOTIFY': 7,
            'DIR_SYNC': 8,
            'UI_FIRST': 9,
            'CC_FIRST': 10,
            'BETASERIES_APIKEY': 11,
            'TMDB_APIKEY': 12,
        }
        for item in enum_dict:
            item_id = enum_dict[item]
            with self.subTest(item + ' exists in SettingEnum'):
                self.assertEqual(item, SettingEnum(item_id).name)
            with self.subTest(item + ' should be ' + str(item_id) + ' in SettingEnum'):
                self.assertEqual(item_id, SettingEnum(item_id).value)
