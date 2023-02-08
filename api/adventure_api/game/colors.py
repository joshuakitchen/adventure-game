import re

COLOR_PLAYER = '\x1b[92m'
COLOR_REGEX = r'@(res|bla|red|gre|yel|blu|mag|cya|lgy|gry|lre|lgr|lye|lbl|lma|lcy|whi)@'

COLORS = {
    'res': '\x1b[0m',
    'bla': '\x1b[30m',
    'red': '\x1b[31m',
    'gre': '\x1b[32m',
    'yel': '\x1b[33m',
    'blu': '\x1b[34m',
    'mag': '\x1b[35m',
    'cya': '\x1b[36m',
    'lgy': '\x1b[37m',
    'gry': '\x1b[90m',
    'lre': '\x1b[91m',
    'lgr': '\x1b[92m',
    'lye': '\x1b[93m',
    'lbl': '\x1b[94m',
    'lma': '\x1b[95m',
    'lcy': '\x1b[95m',
    'whi': '\x1b[95m',
}


def replace_colors(txt: str) -> str:
    end_txt = ''
    txt_spl = re.split(COLOR_REGEX, txt)
    for i, t in enumerate(txt_spl):
        if i % 2 == 1:
            end_txt = end_txt + COLORS[t]
        else:
            end_txt = end_txt + t
    return end_txt
