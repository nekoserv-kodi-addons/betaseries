from unittest import TestCase

from betaseries.toolbox.string import get_sub_teams, is_blank, get_team_alias
from betaseries.toolbox.string import normalize_string


class TestString(TestCase):

    def tests_is_blank(self):
        parameterized = [('', True), ('  ', True), (None, True), (' str ', False)]
        for arg, expected in parameterized:
            self.assertEqual(is_blank(arg), expected)
            print('%s -> %s : OK' % (arg, expected))

    def tests_normalize_string(self):
        parameterized = [('', ''), ('abc', 'abc'), ('DEF', 'DEF')]
        for arg, expected in parameterized:
            self.assertEqual(normalize_string(arg), expected)
            print('%s -> %s : OK' % (arg, expected))

    def tests_get_sub_teams(self):
        parameterized = [('', []),
                         ('  ', []),
                         (None, []),
                         ('tv.show.name.S01E01.this.is.a.title.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb.mkv', ['ntb']),
                         ('tvshowname.S01E02.720p.WEB-DL-AsAp.mkv', ['asap', 'immerse|orenji']),
                         ('movie-name.2022.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-LoL.mkv', ['lol', 'dimension'])
                         ]
        for arg, expected in parameterized:
            self.assertEqual(get_sub_teams(arg), expected)
            print('%s -> %s : OK' % (arg, expected))

    def tests_get_team_alias(self):
        parameterized = [('dummy', []),
                         ('lol', ['dimension']),
                         ('dimension', ['dimension', 'lol|sys|dim']),
                         ('immerse', ['immerse|orenji', 'asap|xii|fqm|imm']),
                         ('xii', ['immerse|orenji']),
                         ('bia', ['tla']),
                         ('tla', ['bia'])
                         ]
        for arg, expected in parameterized:
            self.assertEqual(get_team_alias(arg), expected)
            print('%s -> %s : OK' % (arg, expected))
