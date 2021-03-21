#!/usr/bin/env python3

import argparse
import datetime
import subprocess
import sys

from table import Table, CellInfo


def create_table_from_commits(cell_info, commits, **kwargs):
    delta = kwargs.get('delta', datetime.timedelta(days=1))
    filter_names = kwargs.get('filter_names')
    if filter_names is not None and not isinstance(filter_names, list):
        filter_names = [ filter_names ]
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    make_labels = kwargs.get('make_labels', True)
    col_count = kwargs.get('col_count', 7)

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
        return '%04d-%02d-%02d %02d' % (dtime.year, dtime.month, dtime.day, dtime.hour)
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

def main(argv):
    parser = argparse.ArgumentParser(description='Show git commits in a visual calendar-like format')
    parser.add_argument('--no-border',
        action='store_true', default=False,
        help='removes the cell borders from the output (default is bordered)'
    )
    parser.add_argument('--right-label',
        action='store_true', default=False,
        help='display labels on the right-hand side (default is left-hand side)'
    )

    argspace = parser.parse_args(argv)

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

    cell_info = cell_bordered
    if argspace.no_border:
        cell_info = cell_unborder

    commits = get_commit_data()
    commits.reverse()

    tbl = create_table_from_commits(cell_info, commits)
    tbl.table_name = 'aaaa'
    tbl.left_label = not argspace.right_label

    tbl2 = create_table_from_commits(
        cell_info,
        commits,
        start_date=datetime.datetime.strptime('2021-01-15', '%Y-%m-%d'),
        make_labels=True
    )
    #tbl2.table_name = 'bbbb'

    tbl3 = create_table_from_commits(
        cell_info,
        commits,
        start_date=datetime.datetime.strptime('2021-01-15', '%Y-%m-%d'),
        end_date=datetime.datetime.strptime('2021-01-29', '%Y-%m-%d'),
        make_labels=True
    )
    tbl3.table_name = 'cccc'
    print(Table.draw_tables( (tbl, tbl2, tbl3) ))

if __name__ == '__main__':
    main(sys.argv[1:])
