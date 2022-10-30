from unittest import TestCase
from unittest.mock import patch, MagicMock

from betaseries.toolbox.json_rpc import get_tv_show_id, get_player_id, get_tvdb_id


class TestJsonRpc(TestCase):

    def test_get_player_id(self):
        v = {'result': [{'playerid': 123}]}
        with patch('betaseries.toolbox.json_rpc.json_loads', MagicMock(return_value=v)):
            self.assertEqual(123, get_player_id())

    @patch('betaseries.toolbox.json_rpc.get_player_id', MagicMock(return_value=1))
    def test_get_tv_show_id_is_none(self):
        v = {'result': {'item': {'tvshowid': 0}}}
        with patch('betaseries.toolbox.json_rpc.json_loads', MagicMock(return_value=v)):
            self.assertIsNone(get_tv_show_id())

    @patch('betaseries.toolbox.json_rpc.get_player_id', MagicMock(return_value=1))
    def test_get_tv_show_id_is_found(self):
        v = {'result': {'item': {'tvshowid': 456}}}
        with patch('betaseries.toolbox.json_rpc.json_loads', MagicMock(return_value=v)):
            self.assertEqual(456, get_tv_show_id())

    def test_get_tvdb_id_with_none(self):
        self.assertIsNone(get_tvdb_id(None))

    def test_get_tv_show_id_no_result(self):
        v = {'error'}
        with patch('betaseries.toolbox.json_rpc.json_loads', MagicMock(return_value=v)):
            self.assertIsNone(get_tvdb_id(123))

    def test_get_tv_show_id_with_result(self):
        v = {'result': {'tvshowdetails': {'imdbnumber': 789}}}
        with patch('betaseries.toolbox.json_rpc.json_loads', MagicMock(return_value=v)):
            self.assertEqual(789, get_tvdb_id(123))
