#!/usr/bin/env python3

from table import Table, CellInfo


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
