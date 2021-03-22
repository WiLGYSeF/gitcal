#!/usr/bin/env python3

import argparse
import datetime
import subprocess
import sys

from table import Table, CellInfo


def create_table_from_commits(cell_info, commits, **kwargs):
    delta = kwargs.get('delta', datetime.timedelta(days=1))
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    make_labels = kwargs.get('make_labels', True)
    col_count = kwargs.get('col_count', 7)
    filter_names = kwargs.get('filter_names')
    if filter_names is not None and not isinstance(filter_names, list):
        filter_names = [ filter_names ]

    tbl = Table(cell_info)

    data = []
    row = []
    labels = []
    start_idx = 0
    counter = 0

    if start_date is not None:
        while start_idx < len(commits) and commits[start_idx]['datetime'] < start_date:
            start_idx += 1

    first_date = commits[start_idx]['datetime']
    curdate = datetime.datetime(first_date.year, first_date.month, first_date.day)
    if make_labels:
        labels.append(shortdate(curdate, delta))
    curdate += delta

    def append(val):
        nonlocal curdate, row

        row.append(val)

        if len(row) == col_count:
            data.append(row)
            row = []

            if make_labels:
                labels[-1] += ' - %s' % shortdate(curdate - delta, delta)
                labels.append(shortdate(curdate, delta))

        curdate += delta

    for idx in range(start_idx, len(commits)):
        commit = commits[idx]
        if start_date is not None and commit['datetime'] < start_date:
            continue
        if end_date is not None and commit['datetime'] > end_date:
            break
        if filter_names is not None and commit['name'] not in filter_names:
            continue

        if curdate < commit['datetime']:
            append(counter)
            while curdate < commit['datetime']:
                append(0)

            counter = 1
        else:
            counter += 1

    if counter != 0:
        append(counter)

    if len(row) != 0:
        data.append(row)
        for _ in range(col_count - len(row)):
            append(0)

        data.pop()
        if make_labels:
            labels.pop()

    tbl.set_table_data(data)
    if make_labels:
        tbl.row_labels = labels

    return tbl

def shortdate(dtime, delta):
    if delta == datetime.timedelta(days=1):
        return '%04d-%02d-%02d' % (dtime.year, dtime.month, dtime.day)
    if delta == datetime.timedelta(hours=1):
        return '%04d-%02d-%02d %02dh' % (dtime.year, dtime.month, dtime.day, dtime.hour)
    return str(dtime)

def get_commit_data():
    output = subprocess.check_output([
        'git', 'log',
        '--pretty=format:%h %ad %an',
        '--date=format:%Y%m%d%H%M%S'
    ])
    commits = []

    for line in output.split(b'\n'):
        line = line.decode('utf-8')

        spl = line.split(' ')
        shorthash = spl[0]
        dtime = datetime.datetime.strptime(spl[1], '%Y%m%d%H%M%S')
        name = ' '.join(spl[2:])

        commits.append({
            'shorthash': shorthash,
            'datetime': dtime,
            'name': name
        })
    return commits

def draw_cell_bordered(val):
    yield '+--+'
    yield '|%s|' % val
    yield '+--+'

def draw_cell_unborder(val):
    yield val

def getval(val):
    if val == 0:
        return '  '
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
        tablelist.append(tbl)

    print(Table.draw_tables(tablelist))

if __name__ == '__main__':
    main(sys.argv[1:])
