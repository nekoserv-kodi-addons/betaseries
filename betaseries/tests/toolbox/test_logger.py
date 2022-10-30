from io import StringIO
from unittest import TestCase
from unittest.mock import patch, MagicMock

from betaseries.toolbox.logger import log, send_user_notification


class TestLogger(TestCase):

    @patch('betaseries.toolbox.logger.SettingService.get', MagicMock(return_value='123'))
    def test_log(self):
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('betaseries.toolbox.logger.xbmc_log', side_effect=MagicMock()) as mock_xmbc_log:
                log('this is a sentence')
                self.assertEqual('123: this is a sentence\n', mock_stdout.getvalue())
                self.assertEqual(1, mock_xmbc_log.call_count)

    @patch('betaseries.toolbox.logger.SettingService.get', MagicMock(return_value=None))
    def test_send_user_notification_no_id(self):
        with patch('betaseries.toolbox.logger.executebuiltin', side_effect=MagicMock()) as mock_eb:
            send_user_notification('message id here')
            self.assertEqual(0, mock_eb.call_count)

    @patch('betaseries.toolbox.logger.SettingService.get', MagicMock(return_value=MagicMock()))
    def test_send_user_notification_with_id(self):
        with patch('betaseries.toolbox.logger.executebuiltin', side_effect=MagicMock()) as mock_eb:
            send_user_notification('this is a message id')
            self.assertEqual(1, mock_eb.call_count)