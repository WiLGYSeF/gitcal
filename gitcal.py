#!/usr/bin/env python3

import datetime
import subprocess

from table import Table, CellInfo


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
        commit_shorthash = spl[0]
        dtime = datetime.datetime.strptime(spl[1], '%Y%m%d%H%M%S')
        name = ' '.join(spl[2:])

        commits.append( (commit_shorthash, dtime, name) )
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
