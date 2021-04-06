import argparse
import datetime
import re

import gitcommit


class ColAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        val = values

        if val.lower() == 'guess':
            setattr(namespace, 'col', 'guess')
            return

        try:
            col = int(val)
            setattr(namespace, 'col', val)
            return
        except ValueError:
            pass

        raise ValueError('invalid column value: %s' % val)

class DeltaAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        val = values

        match = re.fullmatch(r'([0-9]+) *m(?:in(?:utes?)?)?', val)
        if match is not None:
            setattr(namespace, 'delta', datetime.timedelta(minutes=int(match[1])))
            return

        match = re.fullmatch(r'([0-9]+) *h(?:(?:ou)?rs?)?', val)
        if match is not None:
            setattr(namespace, 'delta', datetime.timedelta(hours=int(match[1])))
            return

        match = re.fullmatch(r'([0-9]+)(?: *d(?:ays?)?)?', val)
        if match is not None:
            setattr(namespace, 'delta', datetime.timedelta(days=int(match[1])))
            return

        raise ValueError('unknown delta value: %s' % val)

def table_config_from_namespace(namespace):
    tbl_name = namespace.tbl_name
    namespace.tbl_name = None

    delta = getattr(namespace, 'delta', None)
    if delta is None:
        delta = datetime.timedelta(days=1)

    col = namespace.col
    if col is None or col.lower() == 'guess':
        col = guess_col_count(delta)
        if col is None:
            col = 10
    else:
        col = int(col)

    start = None
    if namespace.start is not None:
        try:
            start = datetime.datetime.strptime(namespace.start, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            start = datetime.datetime.strptime(namespace.start, '%Y-%m-%d')
    end = None
    if namespace.end is not None:
        try:
            end = datetime.datetime.strptime(namespace.end, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            end = datetime.datetime.strptime(namespace.end, '%Y-%m-%d')

    filter_names = namespace.filter
    namespace.filter = []

    return {
        'tbl_name': tbl_name,
        'color': namespace.color,
        'border': namespace.border,
        'col': col,
        'delta': delta,
        'filter_names': filter_names,
        'start': start,
        'end': end,

        'label_left': namespace.label_left,
        'label_sep': namespace.label_sep,
        'label': namespace.label,
        'label_inclusive': namespace.label_inclusive,
        'long_label': namespace.long_label,

        'threshold': namespace.threshold,
        'num': namespace.num,
    }

def guess_col_count(delta, min_col=4, max_col=12):
    timeframes = [
        60,
        3600,
        6 * 3600,
        86400,
        7 * 86400,
        14 * 86400
    ]

    seconds = delta.days * 86400 + delta.seconds
    idx = 0

    for i in range(len(timeframes)): #pylint: disable=consider-using-enumerate
        idx = i
        if seconds < timeframes[i]:
            break

    count = timeframes[idx] // seconds
    checked = set()

    while count < min_col or count > max_col:
        if count < min_col:
            idx += 1
        else:
            idx -= 1

        if idx == -1 or idx == len(timeframes) or idx in checked:
            return None

        count = timeframes[idx] // seconds
        checked.add(idx)
    return count

def append_table_config(namespace, table_configs):
    if namespace.all_users:
        append_all_users_table(namespace, table_configs)
        namespace.all_users = False
    else:
        table_configs.append(table_config_from_namespace(namespace))

def append_all_users_table(namespace, table_configs):
    commits = gitcommit.get_commit_data()
    users = gitcommit.get_users_from_commits(commits)
    do_label = namespace.label

    last_date = namespace.end
    if last_date is None:
        last_date = commits[0]['datetime'].strftime('%Y-%m-%d %H:%M:%S')

    user_dict = {}
    for user in users:
        user_dict[user] = {
            'filter': [ user ]
        }

    merge_dict = {}
    users_merged = set()

    for merge in namespace.merge:
        alias = merge[0]
        if alias in user_dict:
            names = merge
        else:
            names = merge[1:]

        if len(names) < 2:
            raise ValueError('must merge with at least two users')

        users_merged.update(names)
        merge_dict[alias] = {
            'filter': names
        }

    for user in users_merged:
        if user not in user_dict:
            raise ValueError('cannot merge with nonexisting user: %s' % user)
        del user_dict[user]
    user_dict.update(merge_dict)

    for name in sorted(user_dict):
        user = user_dict[name]
        namespace.tbl_name = name
        namespace.filter = user['filter']
        namespace.end = last_date

        namespace.label = do_label
        namespace.label_left = True
        do_label = False

        table_configs.append(
            table_config_from_namespace(namespace)
        )

    namespace.merge = []

def parse_args(argv):
    table_configs = []

    class TableAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            append_table_config(namespace, table_configs)

    parser = argparse.ArgumentParser(
        description='Show git commits in a visual calendar-like format'
    )

    group = parser.add_argument_group('table options')
    group.add_argument('-n', '--tbl-name',
        action='store', metavar='NAME',
        help='sets the current table name, resets after each --table'
    )
    group.add_argument('--color',
        action='store_true', default=True,
        help='display the table in color (default)'
    )
    group.add_argument('--no-color',
        dest='color', action='store_false',
        help='do not display the table in color'
    )
    group.add_argument('-b', '--border',
        action='store_true', default=True,
        help='removes the cell borders from the output (default)'
    )
    group.add_argument('-B', '--no-border',
        dest='border', action='store_false', default=False,
        help='removes the cell borders from the output'
    )
    group.add_argument('-c', '--col',
        action=ColAction, metavar='NUM', default=None,
        help='sets the column count (default is "guess" based on the --delta value)'
    )
    group.add_argument('-d', '--delta',
        action=DeltaAction, metavar='TIME',
        help='sets the delta value of each cell (default 1 day), time can be given in #d, #h, or #m (e.g. 4h)'
    )
    group.add_argument('-f', '--filter',
        action='append',
        help='adds a git username to filter for in the table entries, resets after each --table'
    )
    group.add_argument('-m', '--merge',
        action='append', metavar=('ALIAS', 'NAME'), nargs='+', default=[],
        help='merge user tables to one table under ALIAS when using --all-users'
    )
    group.add_argument('--start',
        action='store', metavar='DATE',
        help='starts the table after date (%%Y-%%m-%%d %%H:%%M:%%S format)'
    )
    group.add_argument('--end',
        action='store', metavar='DATE',
        help='ends the table after date (%%Y-%%m-%%d %%H:%%M:%%S format)'
    )
    group.add_argument('-T', '--table',
        action=TableAction, nargs=0,
        help='creates a new table to display alongside the others, all table options are applied to the previous table'
    )
    group.add_argument('--spacing',
        action='store', type=int, metavar='NUM', default=2,
        help='change the spacing between tables (default 2)'
    )
    group.add_argument('--all-users',
        action='store_true', default=False,
        help='create labelled tables for all usernames'
    )

    group = parser.add_argument_group('label options')
    group.add_argument('--label-left',
        action='store_true', default=True,
        help='display labels on the left-hand side (default)'
    )
    group.add_argument('--label-right',
        dest='label_left', action='store_true', default=False,
        help='display labels on the right-hand side'
    )
    group.add_argument('--label-sep',
        action='store', metavar='STRING', default=' ' * 2,
        help='set the string used to separate the table and labels (default "  ")'
    )
    group.add_argument('--label',
        action='store_true', default=True,
        help='show labels for the table rows (default)'
    )
    group.add_argument('--no-label',
        dest='label', action='store_false',
        help='show labels for the table rows'
    )
    group.add_argument('--label-inclusive',
        action='store_true', default=True,
        help='the end label range is inclusive (default)'
    )
    group.add_argument('--label-noninclusive',
        dest='label_inclusive', action='store_false',
        help='the end label range is not inclusive'
    )
    group.add_argument('--long-label',
        action='store_true', default=True,
        help='use full datetimes for label ranges (default)'
    )
    group.add_argument('--short-label',
        dest='long_label', action='store_false',
        help='use shortened datetimes for label ranges'
    )

    group = parser.add_argument_group('cell options')
    group.add_argument('-t', '--threshold',
        action='store', type=int, metavar='NUM', default=0,
        help='set the threshold value where the cell value is no longer considered small (default 0)'
    )
    group.add_argument('--num',
        action='store_true', default=False,
        help='prints the commit counts in the cells'
    )
    group.add_argument('--no-num',
        dest='num', action='store_false',
        help='do not print the commit counts in the cells (default)'
    )

    argspace = parser.parse_args(argv)
    return argspace, table_configs
