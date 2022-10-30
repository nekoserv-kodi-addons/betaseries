from re import findall

from unicodedata import normalize

from betaseries.toolbox.logger import log

TEAMS = (
    # equivalent of SD teams to HD teams
    # format should be ('SD', 'HD')
    ('lol|sys|dim', 'dimension'),
    ('asap|xii|fqm|imm', 'immerse|orenji'),
    ('excellence', 'remarkable'),
    ('2hd|xor', 'ctu'),
    ('tla', 'bia'))


def is_blank(input_string: str) -> bool:
    if input_string and input_string.strip():
        return False
    return True


def normalize_string(to_normalize: str) -> str:
    return normalize('NFKD', to_normalize).encode('ascii', 'ignore').decode('ascii')


def get_sub_teams(filename: str) -> list:
    if is_blank(filename):
        return []
    formatted_filename = filename.replace('.', '-').lower()
    # guess team name
    team = formatted_filename.split('-')[-2]
    results = [team]
    # add equivalent team(s), if any
    results.extend(get_team_alias(team))
    log('get_sub_teams = %s' % results)
    return results


def get_team_alias(team) -> list:
    aliases = []
    # find team aliases
    for sd, hd in TEAMS:
        # sd -> hd
        if len(findall(sd, team)) > 0:
            aliases.append(hd)
        # hd -> sd
        if len(findall(hd, team)) > 0:
            aliases.append(sd)
    log('get_team_alias = %s' % aliases)
    return aliases
