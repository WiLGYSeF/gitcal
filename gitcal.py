#!/usr/bin/env python3

import argparse
import datetime
import sys

from table import Table, CellInfo
from gitcommit import create_table_from_commits, get_commit_data


def draw_cell_bordered(val):
    yield '+--+'
    yield '|%s|' % val
    yield '+--+'

def draw_cell_unborder(val):
    yield val

def getval(tbl, val):
    if val == 0:
        return '\x1b[100m  \x1b[0m'
    return '\x1b[42m  \x1b[0m'

table_configs = []

class TableAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        table_configs.append(table_config_from_namespace(namespace))

class DeltaAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        val = option_string
        if val.startswith('--'):
            val = val[2:]

        if val in ('h', 'hour', 'hours', 'hourly'):
            setattr(namespace, 'delta', datetime.timedelta(hours=1))
        elif val in ('d', 'day', 'days', 'daily'):
            setattr(namespace, 'delta', datetime.timedelta(days=1))
        else:
            raise ValueError('unknown delta value')

def table_config_from_namespace(namespace):
    tbl_name = namespace.tbl_name
    namespace.tbl_name = None

    delta = getattr(namespace, 'delta', None)
    if delta is None:
        delta = datetime.timedelta(days=1)

    filter_names = namespace.filter
    namespace.filter = []

    return {
        'tbl_name': tbl_name,
        'border': namespace.border,
        'left_label': namespace.left_label,
        'label_sep': namespace.label_sep,
        'delta': delta,
        'make_labels': namespace.make_labels,
        'col_count': namespace.col_count,
        'filter_names': filter_names,
    }

def main(argv):
    parser = argparse.ArgumentParser(
        description='Show git commits in a visual calendar-like format'
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
        help="don't make labels for the table rows (default is true)"
    )
    parser.add_argument('--col-count',
        action='store', type=int, default=7,
        help='sets the column count (default is 7)'
    )
    parser.add_argument('--tbl-name',
        action='store',
        help='sets the current table name. resets after each --table'
    )

    parser.add_argument('--day', '--daily',
        dest='delta', action=DeltaAction, nargs=0,
        help='sets the delta value to 1 day  (default is 1 day)'
    )
    parser.add_argument('--hour', '--hourly',
        dest='delta', action=DeltaAction, nargs=0,
        help='sets the delta value to 1 hour (default is 1 day)'
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

    argspace = parser.parse_args(argv)
    table_configs.append(table_config_from_namespace(argspace))

    cell_bordered = CellInfo(
        width=4,
        height=3,
        has_border=True,
        drawcell=draw_cell_bordered,
        getval=getval
    )
    cell_unborder = CellInfo(
        width=2,
        height=1,
        has_border=False,
        drawcell=draw_cell_unborder,
        getval=getval
    )

    commits = get_commit_data()
    commits.reverse()

    tablelist = []

    for cfg in table_configs:
        tbl = create_table_from_commits(
            cell_bordered if cfg['border'] else cell_unborder,
            commits,
            delta=cfg['delta'],
            make_labels=cfg['make_labels'],
            col_count=cfg['col_count'],
            filter_names=cfg['filter_names'],
        )
        tbl.table_name = cfg['tbl_name']
        tbl.left_label = cfg['left_label']
        tbl.label_sep = cfg['label_sep']
        tablelist.append(tbl)

    print(Table.draw_tables(
        tablelist,
        spacing=argspace.spacing,
    ))

if __name__ == '__main__':
    main(sys.argv[1:])
