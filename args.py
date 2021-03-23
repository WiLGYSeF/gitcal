import argparse
import datetime
import re


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

    col_count = namespace.col_count
    if col_count is None or col_count.lower() == 'guess':
        col_count = guess_col_count(delta)
        if col_count is None:
            col_count = 10
    else:
        col_count = int(col_count)

    filter_names = namespace.filter
    namespace.filter = []

    return {
        'tbl_name': tbl_name,
        'col_count': col_count,
        'border': namespace.border,

        'left_label': namespace.left_label,
        'label_sep': namespace.label_sep,
        'make_labels': namespace.make_labels,
        'labels_inclusive': namespace.labels_inclusive,

        'threshold': namespace.threshold,
        'print_num': namespace.print_num,

        'delta': delta,
        'filter_names': filter_names,
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

    if delta.seconds == 0:
        return None

    for i in range(len(timeframes)): # pylint: disable=consider-using-enumerate
        tframe = timeframes[i]
        if delta.seconds < tframe:
            count = tframe // delta.seconds
            if count < min_col:
                i += 1
                count = timeframes[i] // delta.seconds
            if count > max_col and timeframes[i - 1] > delta.seconds:
                i -= 1
                count = timeframes[i] // delta.seconds
            return count
    return None

def parse_args(argv):
    table_configs = []

    class TableAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            table_configs.append(table_config_from_namespace(namespace))

    parser = argparse.ArgumentParser(
        description='Show git commits in a visual calendar-like format'
    )

    parser.add_argument('--tbl-name',
        action='store',
        help='sets the current table name. resets after each --table'
    )
    parser.add_argument('--col-count',
        action='store', default=None,
        help='sets the column count (default is "guess" based on the --delta value)'
    )

    parser.add_argument('--border',
        action='store_true', default=True,
        help='removes the cell borders from the output (default is bordered)'
    )
    parser.add_argument('--no-border',
        dest='border', action='store_false', default=False,
        help='removes the cell borders from the output (default is bordered)'
    )

    parser.add_argument('--left-label',
        action='store_true', default=True,
        help='display labels on the left-hand side (default is left-hand side)'
    )
    parser.add_argument('--right-label',
        dest='left_label', action='store_true', default=False,
        help='display labels on the right-hand side (default is left-hand side)'
    )
    parser.add_argument('--label-sep',
        action='store', default=' ' * 2,
        help='set the string used to separate the table and labels'
    )
    parser.add_argument('--make-labels',
        action='store_true', default=True,
        help='make labels for the table rows (default is true)'
    )
    parser.add_argument('--no-make-labels',
        dest='make_labels', action='store_false',
        help='do not make labels for the table rows (default is true)'
    )
    parser.add_argument('--labels-inclusive',
        action='store_true', default=True,
        help='the end label range is inclusive'
    )
    parser.add_argument('--labels-not-inclusive',
        dest='labels_inclusive', action='store_false',
        help='the end label range is not inclusive'
    )

    parser.add_argument('--threshold',
        action='store', type=int, default=0,
        help='set the threshold value where the cell value is no longer considered small (default is 0)'
    )
    parser.add_argument('--print-num',
        action='store_true', default=False,
        help='prints the commit counts in the cells (default is false)'
    )
    parser.add_argument('--no-print-num',
        dest='print_num', action='store_false',
        help='do not print the commit counts in the cells (default is false)'
    )

    parser.add_argument('--delta',
        action=DeltaAction,
        help='sets the delta value of each cell (default is 1 day)'
    )

    parser.add_argument('--filter',
        action='append',
        help='adds a git username to filter for in the table entries. resets after each --table'
    )

    parser.add_argument('--table',
        action=TableAction, nargs=0,
        help='creates a new table to display alongside the others, all table options are applied to the previous table'
    )
    parser.add_argument('--spacing',
        action='store', type=int, default=2,
        help='change the spacing between tables (default is 2)'
    )

    return parser.parse_args(argv), table_configs
