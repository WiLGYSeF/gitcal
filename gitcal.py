#!/usr/bin/env python3

import datetime
import subprocess

from table import Table, CellInfo


def create_table_from_commits(cell_info, commits, timedelta=None, filter_names=None):
    if timedelta is None:
        timedelta = datetime.timedelta(days=1)
    if filter_names is not None and not isinstance(filter_names, list):
        filter_names = [ filter_names ]

    tbl = Table(cell_info)
    tbl.left_label = True

    data = []
    row = []
    labels = []
    counter = 0

    col_count = 7

    first_date = commits[0]['datetime']
    curdate = datetime.datetime(first_date.year, first_date.month, first_date.day)
    labels.append(str(curdate))
    curdate += timedelta

    def append(val):
        nonlocal curdate, row

        row.append(val)

        if len(row) == col_count:
            data.append(row)
            row = []

            labels[-1] += ' - %s' % (curdate - timedelta)
            labels.append(str(curdate))

        curdate += timedelta

    for commit in commits:
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
        labels.pop()

    tbl.set_table_data(data)

    tbl.row_labels = labels

    return tbl

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

def main():
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

    tbl = create_table_from_commits(cell_bordered, commits)
    print(tbl.draw_table())
    return

    tbl = Table(cell_bordered)
    tbl.set_table_data([
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]
    ])

    tbl_long = Table(cell_bordered)
    tbl_long.set_table_data([
        [1, 0],
        [1, 0],
        [1, 1],
        [0, 0],
        [0, 0],
        [1, 1],
        [0, 1],
    ])

    tbl2 = Table(cell_bordered)
    tbl2.set_table_data([
        [0, 1, 1, 1],
        [0, 1, 0, 0],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
    ])

    print(tbl.draw_table())

    print(Table.draw_tables( (tbl, tbl_long, tbl2) ))

if __name__ == '__main__':
    main()
