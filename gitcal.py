#!/usr/bin/env python3

import sys

from args import parse_args, table_config_from_namespace
from table import Table, CellInfo
from gitcommit import create_table_from_commits, get_commit_data


def draw_tables(argspace, table_configs):
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
            col_count=cfg['col'],
            make_labels=cfg['label'],
            labels_inclusive=cfg['label_inclusive'],
            long_labels=cfg['long_label'],
            delta=cfg['delta'],
            start_date=cfg['start'],
            end_date=cfg['end'],
            filter_names=cfg['filter_names'],
        )
        setattr(tbl, 'config', cfg)
        tbl.table_name = cfg['tbl_name']
        tbl.left_label = cfg['left_label']
        tbl.label_sep = cfg['label_sep']
        tablelist.append(tbl)

    return Table.draw_tables(
        tablelist,
        spacing=argspace.spacing,
    )

def draw_cell_bordered(val):
    yield '+--+'
    yield '|%s|' % val
    yield '+--+'

def draw_cell_unborder(val):
    yield val

def getval(tbl, val, col=-1, row=-1):
    if val == 0:
        if tbl.config['color']:
            return '\x1b[100m  \x1b[0m'

        if not tbl.cell_info.has_border:
            return '..'
        return '  '

    celldata = '  '
    if tbl.config['num']:
        celldata = '%2d' % val
        if len(celldata) > 2:
            celldata = '#^'

        if tbl.config['color'] and col != -1 and row != -1 and (col & 1) == 1:
            if is_val_touching_adjacent(tbl, val, col, row):
                celldata = '\x1b[4m%s\x1b[24m' % celldata

    if not tbl.config['color']:
        if tbl.config['num']:
            return celldata
        return '##'

    if val < tbl.config['threshold']:
        return '\x1b[30;43m%s\x1b[39;49m' % celldata
    return '\x1b[30;42m%s\x1b[39;49m' % celldata

def is_val_touching_adjacent(tbl, val, col, row):
    return (
        val > 9 and col > 0 and tbl.data[row][col - 1] != 0
    ) or (
        col < len(tbl.data[row]) - 1 and tbl.data[row][col + 1] > 9
    )

def draw_tables_from_args(argv):
    argspace, table_configs = parse_args(argv)
    table_configs.append(table_config_from_namespace(argspace))

    return draw_tables(argspace, table_configs)

if __name__ == '__main__': #pragma: no cover
    print(draw_tables_from_args(sys.argv[1:]))
