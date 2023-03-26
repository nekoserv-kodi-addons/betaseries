from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from betaseries.settings.setting_enum import SettingEnum
from betaseries.toolbox.gui import sort_subtitles, sort_by_item, add_subtitles_to_gui


def get_argument(mocked_method, arg_number):
    arg_list = []
    for i in range(mocked_method.call_count):
        arg_list.append(mocked_method.call_args_list[i][0][arg_number - 1])
    return arg_list


class TestGui(TestCase):
    s = [{'uilang': 'jp', 'ext': 'srt', 'filename': 'show-s01e01-fff.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'jp', 'lang2': 'en', 'cc': False, 'sync': True, 'note': 1, 'team': 'aSa'},
         {'uilang': 'it', 'ext': 'srt', 'filename': 'show-s01e01-eee.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'it', 'lang2': 'en', 'cc': True, 'sync': False, 'note': 2, 'team': 'aSa'},
         {'uilang': 'gb', 'ext': 'srt', 'filename': 'show-s01e01-ddd.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'gb', 'lang2': 'en', 'cc': False, 'sync': True, 'note': 3, 'team': 'aSa'},
         {'uilang': 'fr', 'ext': 'srt', 'filename': 'show-s01e01-ccc.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'fr', 'lang2': 'en', 'cc': True, 'sync': False, 'note': 4, 'team': 'aSa'},
         {'uilang': 'en', 'ext': 'srt', 'filename': 'show-s01e01-bbb.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'en', 'lang2': 'en', 'cc': False, 'sync': True, 'note': 5, 'team': 'aSa'},
         {'uilang': 'de', 'ext': 'srt', 'filename': 'show-s01e01-aaa.srt', 'link': 'http://dummy-web.site/api/getsrt',
          'lang': 'de', 'lang2': 'en', 'cc': True, 'sync': False, 'note': 6, 'team': 'DEVOTION'}]

    # @patch('betaseries.toolbox.gui.SettingService.get')
    # def test_sort_subtitles(self, mock_settings_service_get):
    def test_sort_subtitles(self):

        test_list = [
            {'uifirst': False, 'ccfirst': False, 'call_count': 6,
             'expected_args': ['filename', 'note', 'lang', 'cc', 'sync', 'team']},
            {'uifirst': True, 'ccfirst': False, 'call_count': 7,
             'expected_args': ['filename', 'note', 'lang', 'cc', 'uilang', 'sync', 'team']},
            {'uifirst': False, 'ccfirst': True, 'call_count': 5,
             'expected_args': ['filename', 'note', 'lang', 'sync', 'team']},
            {'uifirst': True, 'ccfirst': True, 'call_count': 6,
             'expected_args': ['filename', 'note', 'lang', 'uilang', 'sync', 'team']}
        ]

        for current_test in test_list:
            with self.subTest(current_test):
                # dynamic mock based on SettingService.get()
                def dynamic_mock(item):
                    if item == SettingEnum.UI_FIRST:
                        return current_test['uifirst']
                    if item == SettingEnum.CC_FIRST:
                        return current_test['ccfirst']
                # dynamic mock setup
                with patch('betaseries.toolbox.gui.SettingService.get', side_effect=lambda x: dynamic_mock(x)):
                    with patch('betaseries.toolbox.gui.sort_by_item') as sb:
                        sort_subtitles(self.s)
                        self.assertEqual(current_test['call_count'], sb.call_count)
                        current_second_args = get_argument(sb, 2)
                        self.assertEqual(current_test['expected_args'], current_second_args)

    @patch('betaseries.toolbox.gui.argv', ['./gui.py', '1'])
    def test_add_subtitles_to_gui(self):
        with patch('betaseries.toolbox.gui.addDirectoryItem') as adi_mock:
            add_subtitles_to_gui(self.s)
            self.assertEqual(len(self.s), adi_mock.call_count)

    def test_sort_by_item(self):
        subtitles_list = Mock()
        subtitles_list.sort.return_value = ANY
        sort_by_item(subtitles_list, 'item')
        self.assertEqual(1, subtitles_list.sort.call_count)
