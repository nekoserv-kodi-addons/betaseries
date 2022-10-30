from unittest import TestCase
from unittest.mock import patch

from betaseries.toolbox.param import get_params


class TestParam(TestCase):

    @patch('betaseries.toolbox.param.argv', [])
    def test_get_params_empty_array(self):
        self.assertEqual(get_params(), [])

    @patch('betaseries.toolbox.param.argv', ['./param.py'])
    def test_get_params_one_arg(self):
        self.assertEqual(get_params(), [])

    @patch('betaseries.toolbox.param.argv', ['./param.py', '1'])
    def test_get_params_two_args(self):
        self.assertEqual(get_params(), [])

    @patch('betaseries.toolbox.param.argv', ['./param.py', '1', '?foo=bar'])
    def test_get_params_three_args(self):
        self.assertEqual(get_params(), {'foo': 'bar'})

    @patch('betaseries.toolbox.param.argv', ['./param.py', '1',
                                                 '?action=search&languages=English&preferredlanguage=Unknown',
                                                 'resume:false'])
    def test_get_params_four_args(self):
        self.assertEqual(get_params(), {'action': 'search', 'languages': 'English', 'preferredlanguage': 'Unknown'})
