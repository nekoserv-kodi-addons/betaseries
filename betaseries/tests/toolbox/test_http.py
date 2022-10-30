from unittest import TestCase
from unittest.mock import patch, mock_open, Mock, MagicMock, ANY
from urllib.error import HTTPError

from betaseries.toolbox.http import get_user_agent, get_content_from_url, download_subtitle

mock_uri = 'http://dummy-web.site/api'
mock_http_content = b'<html><h1>Mock Content</h1></html>'


def mock_http(status):
    mock_build_opener = Mock()
    mock_build_opener.open = mock_open(read_data=mock_http_content)
    mock_build_opener.open.return_value.status = status
    return mock_build_opener


def mock_http_exception():
    mock_build_opener = Mock()
    mock_build_opener.open.side_effect = HTTPError(mock_uri, 500, 'Internal Error', {}, None)
    return mock_build_opener


def mock_weird_exception():
    mock_build_opener = Mock()
    mock_build_opener.open.side_effect = Exception('testing')
    return mock_build_opener


class TestHttp(TestCase):

    def test_get_user_agent(self):
        r = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
        self.assertEqual(r, get_user_agent())

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_http_exception()))
    def test_get_content_from_url_with_http_exception(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertIsNone(get_content_from_url(mock_uri))
            self.assertEqual(1, mock_log.call_count)
            self.assertEqual(('HTTPError for ' + mock_uri + ' : HTTP Error 500: Internal Error', 3),
                             mock_log.call_args[0])

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_weird_exception()))
    def test_get_content_from_url_with_weird_exception(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertIsNone(get_content_from_url(mock_uri))
            self.assertEqual(1, mock_log.call_count)
            self.assertEqual(('Exception for ' + mock_uri + ' : testing', 3), mock_log.call_args[0])

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_http(200)))
    def test_get_content_from_url_with_200(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertEqual(mock_http_content, get_content_from_url(mock_uri))
            self.assertEqual(0, mock_log.call_count)

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_http(300)))
    def test_get_content_from_url_with_300(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertEqual(mock_http_content, get_content_from_url(mock_uri))
            self.assertEqual(0, mock_log.call_count)

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_http(404)))
    def test_get_content_from_url_with_404(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertEqual(mock_http_content, get_content_from_url(mock_uri))
            self.assertEqual(0, mock_log.call_count)

    @patch('betaseries.toolbox.http.build_opener', MagicMock(return_value=mock_http(500)))
    def test_get_content_from_url_with_500(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertEqual(mock_http_content, get_content_from_url(mock_uri))
            self.assertEqual(0, mock_log.call_count)

    @patch('betaseries.toolbox.http.get_content_from_url', MagicMock(return_value=None))
    def test_download_subtitle_no_content(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            self.assertIsNone(download_subtitle(mock_uri, 'srt', 'dummy.srt'))
            self.assertEqual(1, mock_log.call_count)

    @patch('betaseries.toolbox.http.get_content_from_url', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.generate_tmp_file', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.write_to_file', MagicMock(return_value=ANY))
    def test_download_subtitle_with_content_no_extraction(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            with patch('betaseries.toolbox.http.extract_file') as mock_extract:
                download_subtitle(mock_uri, 'srt', 'dummy.srt')
                self.assertEqual(0, mock_extract.call_count)
            self.assertEqual(3, mock_log.call_count)

    @patch('betaseries.toolbox.http.get_content_from_url', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.generate_tmp_file', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.write_to_file', MagicMock(return_value=ANY))
    def test_download_subtitle_with_content_with_zip_extraction(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            with patch('betaseries.toolbox.http.extract_file') as mock_extract:
                download_subtitle(mock_uri, 'zip', 'dummy.srt')
                self.assertEqual(1, mock_extract.call_count)
            self.assertEqual(2, mock_log.call_count)

    @patch('betaseries.toolbox.http.get_content_from_url', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.generate_tmp_file', MagicMock(return_value=ANY))
    @patch('betaseries.toolbox.http.write_to_file', MagicMock(return_value=ANY))
    def test_download_subtitle_with_content_with_rar_extraction(self):
        with patch('betaseries.toolbox.http.log') as mock_log:
            with patch('betaseries.toolbox.http.extract_file') as mock_extract:
                download_subtitle(mock_uri, 'rar', 'dummy.srt')
                self.assertEqual(1, mock_extract.call_count)
            self.assertEqual(2, mock_log.call_count)
