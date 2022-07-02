from re import compile, findall

from unicodedata import normalize

from .logger import log

# equivalent of SD teams to HD teams
TEAMS = (
    # SD[0]              HD[1]
    ("lol|sys|dim", "dimension"),
    ("asap|xii|fqm|imm", "immerse|orenji"),
    ("excellence", "remarkable"),
    ("2hd|xor", "ctu"),
    ("tla", "bia"))


def normalize_string(to_normalize):
    return normalize('NFKD', to_normalize).encode('ascii', 'ignore')


def get_sub_team(filename):
    self_team_pattern = compile(r".*-([^-]+)$")
    sub_teams = [filename.replace(".", "-")]
    if len(sub_teams[0]) > 0:
        # get team name (everything after "-")
        sub_teams[0] = self_team_pattern.match("-" + sub_teams[0]).groups()[0].lower()
        # find equivalent teams, if any
        tmp = other_team(sub_teams[0], 0, 1)
        if len(tmp) > 0 and tmp != sub_teams[0]:
            sub_teams.append(tmp)
        # find other equivalent teams, if any
        tmp = other_team(sub_teams[0], 1, 0)
        if len(tmp) > 0 and tmp != sub_teams[0]:
            sub_teams.append(tmp)
    log("after sub_teams = %s" % sub_teams)
    return sub_teams


def other_team(team, team_from, team_to):
    # get other team using TEAMS table
    for x in TEAMS:
        if len(findall(x[team_from], team)) > 0:
            return x[team_to]
    # return team if not found
    log("other team not found")
    return team
