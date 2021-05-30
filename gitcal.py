#!/usr/bin/env python3

import sys

import args
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

        if cfg['collapse'] > 0:
            collapse_table(tbl, cfg['collapse'])

        setattr(tbl, 'config', cfg)
        tbl.table_name = cfg['tbl_name']
        tbl.label_left = cfg['label_left']
        tbl.label_sep = cfg['label_sep']
        tablelist.append(tbl)

    return Table.draw_tables(
        tablelist,
        spacing=argspace.spacing,
    )

def collapse_table(tbl, consecutive):
    if consecutive < 1:
        raise ValueError('collapse value must be at least 1')

    def empty(row):
        for val in row:
            if val != 0:
                return False
        return True

    last_empty = None
    idx = 0

    while idx < len(tbl.data):
        row = tbl.data[idx]
        if empty(row):
            if last_empty is None:
                last_empty = idx
            idx += 1
            continue

        if last_empty is None:
            idx += 1
            continue

        if idx - last_empty >= consecutive:
            tbl.data = tbl.data[:last_empty] + [[-1] * len(tbl.data[0])] + tbl.data[idx:]
            if tbl.has_labels():
                labels = tbl.row_labels
                length = tbl.longest_label_length
                if isinstance(labels, dict):
                    for i in range(last_empty, idx):
                        if i in labels:
                            del labels[i]
                    tbl.row_labels = labels
                else:
                    tbl.row_labels = labels[:last_empty] + [''] + labels[idx:]
            idx -= idx - last_empty - 1
        last_empty = None
        idx += 1


def draw_cell_bordered(val):
    yield '+--+'
    yield '|%s|' % val
    yield '+--+'

def draw_cell_unborder(val):
    yield val

def getval(tbl, val, col=-1, row=-1):
    if val == -1:
        return '**'
    if val == 0:
        if tbl.config['color']:
            return '\x1b[100m  \x1b[49m'
        return '  ' if tbl.cell_info.has_border else '..'

    celldata = '  '
    if tbl.config['num']:
        celldata = '%2d' % val
        if len(celldata) > 2:
            celldata = '#^'

        if (
            not tbl.cell_info.has_border
            and tbl.config['color']
            and col != -1 and row != -1 and (col & 1) == 1
        ):
            if is_val_touching_adjacent(tbl, val, col, row):
                celldata = '\x1b[4m%s\x1b[24m' % celldata

    if not tbl.config['color']:
        return celldata if tbl.config['num'] else '##'

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
    argspace, table_configs = args.parse_args(argv)
    args.append_table_config(argspace, table_configs)
    return draw_tables(argspace, table_configs)

if __name__ == '__main__': #pragma: no cover
    print(draw_tables_from_args(sys.argv[1:]))
