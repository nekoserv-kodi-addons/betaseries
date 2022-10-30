from unittest import TestCase
from unittest.mock import MagicMock, patch, mock_open

from betaseries.toolbox.file import clean_temp_directory, get_filename, generate_tmp_file, write_to_file, extract_file, \
    count_files_in_dir


class TestFile(TestCase):

    @patch('betaseries.toolbox.file.SettingService.get', MagicMock())
    @patch('betaseries.toolbox.file.path.exists', MagicMock(return_value=True))
    def test_clean_temp_directory_with_rmtree(self):
        with patch('betaseries.toolbox.file.rmtree') as mock_rmtree:
            with patch('betaseries.toolbox.file.mkdirs') as mock_mkdirs:
                clean_temp_directory()
                self.assertEqual(1, mock_mkdirs.call_count)
            self.assertEqual(1, mock_rmtree.call_count)

    @patch('betaseries.toolbox.file.SettingService.get', MagicMock())
    @patch('betaseries.toolbox.file.path.exists', MagicMock(return_value=False))
    def test_clean_temp_directory_without_rmtree(self):
        with patch('betaseries.toolbox.file.rmtree') as mock_rmtree:
            with patch('betaseries.toolbox.file.mkdirs') as mock_mkdirs:
                clean_temp_directory()
                self.assertEqual(1, mock_mkdirs.call_count)
            self.assertEqual(0, mock_rmtree.call_count)

    @patch('betaseries.toolbox.file.SettingService.get', MagicMock(return_value=True))
    def test_get_filename_with_dir_sync(self):
        self.assertEqual('..', get_filename('../test'))

    @patch('betaseries.toolbox.file.SettingService.get', MagicMock(return_value=False))
    def test_get_filename_no_dir_sync(self):
        self.assertEqual('test', get_filename('../test'))

    @patch('betaseries.toolbox.file.SettingService.get', MagicMock(return_value='prefix/'))
    def test_generate_tmp_file(self):
        self.assertEqual('prefix/betaseries.test', generate_tmp_file('test'))

    def test_write_to_file(self):
        with patch("builtins.open", mock_open()) as mock_open_file:
            write_to_file('data-to-write', mock_open_file)
            mock_open_file.assert_called_once_with(mock_open_file, 'wb')
            self.assertEqual(1, mock_open_file.call_count)
            mock_open_file.return_value.__enter__().write.assert_called_once_with('data-to-write')

    @patch('betaseries.toolbox.file.listdir', MagicMock(return_value=['dummy-file']))
    @patch('betaseries.toolbox.file.SettingService.get', MagicMock())
    @patch('betaseries.toolbox.file.sleep', MagicMock())
    @patch('betaseries.toolbox.file.executebuiltin', MagicMock())
    def test_extract_file_timeout(self):
        with patch('betaseries.toolbox.file.log', MagicMock()) as mock_log:
            self.assertIsNone(extract_file('archive.zip', 'mock_filename'))
            self.assertEqual(3, mock_log.call_count)

    @patch('betaseries.toolbox.file.listdir', MagicMock(return_value=['dummy-file']))
    @patch('betaseries.toolbox.file.SettingService.get', MagicMock(return_value='.'))
    @patch('betaseries.toolbox.file.sleep', MagicMock())
    @patch('betaseries.toolbox.file.executebuiltin', MagicMock())
    @patch('betaseries.toolbox.file.count_files_in_dir', MagicMock(return_value=2))
    def test_extract_file_ok(self):
        with patch('betaseries.toolbox.file.log', MagicMock()) as mock_log:
            self.assertEqual('dummy-file', extract_file('archive.zip', 'mock_filename'))
            self.assertEqual(6, mock_log.call_count)

    @patch('betaseries.toolbox.file.listdir', MagicMock(return_value=['dummy-file']))
    @patch('betaseries.toolbox.file.SettingService.get', MagicMock(return_value='.'))
    @patch('betaseries.toolbox.file.sleep', MagicMock())
    @patch('betaseries.toolbox.file.executebuiltin', MagicMock())
    @patch('betaseries.toolbox.file.count_files_in_dir', MagicMock(return_value=2))
    @patch('betaseries.toolbox.file.normalize_string', MagicMock(return_value='not-my-file'))
    def test_extract_file_not_found(self):
        with patch('betaseries.toolbox.file.log', MagicMock()) as mock_log:
            self.assertIsNone(extract_file('archive.zip', 'mock_filename'))
            self.assertEqual(6, mock_log.call_count)

    @patch('betaseries.toolbox.file.listdir', MagicMock(return_value=['one-file', 'two-files', 'three-files']))
    def test_count_files_in_dir(self):
        self.assertEqual(3, count_files_in_dir('dummy'))
