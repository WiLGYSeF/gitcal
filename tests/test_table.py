from contextlib import contextmanager
import os
import re
import unittest

from table import Table, CellInfo


TABLES_DIR = os.path.join(os.path.dirname(__file__), 'tables')

LABEL_REGEX = re.compile(r'^([A-Za-z0-9 ]+): *')


class TableTest(unittest.TestCase):
    def test_empty_table(self):
        self.assert_from_file('empty')

    def test_2x2a_table(self):
        self.assert_from_file('2x2a')

    def test_2x2b_table(self):
        self.assert_from_file('2x2b')

    def test_6x4a_table(self):
        self.assert_from_file('6x4a')

    def test_6x4a_label_table(self):
        self.assert_from_file('6x4a-label')

    def assert_from_file(self, name, print_output=False):
        if print_output: #pragma: no cover
            print()
            print(name)

        fname = os.path.join(TABLES_DIR, name + '.txt')
        with open(fname, 'r') as file:
            data = []
            labels = []
            has_labels = False

            for line in file:
                match = LABEL_REGEX.match(line)
                if match is not None:
                    labels.append(match[1])
                    has_labels = True

                    line = line[match.end(0):]
                else:
                    labels.append('')

                data.append(list(map(
                    lambda x: int(x),
                    line.lstrip().split(',')
                )))

            if not has_labels:
                labels = None

            with create_table(data, labels=labels, border=True) as tbl:
                if print_output:  #pragma: no cover
                    print(tbl.draw_table())
                with open(fname + '.border.output', 'r') as outfile:
                    self.line_comparison(tbl.draw_table(), outfile.read())
            with create_table(data, labels=labels, border=False) as tbl:
                if print_output:  #pragma: no cover
                    print(tbl.draw_table())
                with open(fname + '.output', 'r') as outfile:
                    self.line_comparison(tbl.draw_table(), outfile.read())

    def line_comparison(self, first, second):
        alines = first.split('\n')
        blines = second.split('\n')

        self.assertEqual(len(alines), len(blines))

        for i in range(len(alines)): #pylint: disable=consider-using-enumerate
            self.assertEqual(alines[i].rstrip(), blines[i].rstrip())

@contextmanager
def create_table(data, labels=None, border=True):
    tbl = Table(cell_bordered if border else cell_unborder)
    tbl.data = data

    if labels is not None:
        tbl.row_labels = labels

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
