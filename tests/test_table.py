from contextlib import contextmanager
import os
import unittest

from table import Table, CellInfo


TABLES_DIR = os.path.join(os.path.dirname(__file__), 'tables')


class TableTest(unittest.TestCase):
    def test_empty_table(self):
        self.assert_from_file('empty')

    def test_2x2a_table(self):
        self.assert_from_file('2x2a')

    def test_2x2b_table(self):
        self.assert_from_file('2x2b')

    def test_6x4a_table(self):
        self.assert_from_file('6x4a')

    def assert_from_file(self, name, print_output=False):
        if print_output: #pragma: no cover
            print()
            print(name)

        fname = os.path.join(TABLES_DIR, name + '.txt')
        with open(fname, 'r') as file:
            data = list(map(
                lambda x: list(map(
                    lambda y: int(y),
                    x.split(',')
                )),
                file.readlines()
            ))
            with create_table(data, border=True) as tbl:
                if print_output:  #pragma: no cover
                    print(tbl.draw_table())
                with open(fname + '.border.output', 'r') as outfile:
                    self.assertEqual(tbl.draw_table(), outfile.read())
            with create_table(data, border=False) as tbl:
                if print_output:  #pragma: no cover
                    print(tbl.draw_table())
                with open(fname + '.output', 'r') as outfile:
                    self.assertEqual(tbl.draw_table(), outfile.read())

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
        return '..'
    return '%2d' % val

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
