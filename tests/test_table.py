from contextlib import contextmanager
import unittest

from table import Table, CellInfo


class TableTest(unittest.TestCase):
    def test_empty_table(self):
        with create_table([[]]) as tbl:
            self.assertEqual(tbl.draw_table(), '')


@contextmanager
def create_table(data, border=True):
    tbl = Table(cell_bordered if border else cell_unborder)
    tbl.data = data

    yield tbl

def draw_cell_bordered(val):
    yield '+--+'
    yield '|%s|' % val
    yield '+--+'

def draw_cell_unborder(val):
    yield val

def getval(tbl, val, col=-1, row=-1):
    if val == 0:
        return '.'
    return '#'

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
