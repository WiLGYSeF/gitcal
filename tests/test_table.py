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

    def test_6x4a_label_some_table(self):
        self.assert_from_file('6x4a-label-some')

    def test_6x4a_label_some_label_left_table(self):
        self.assert_from_file('6x4a-label-some-label-left')

    def test_6x4a_label_some_label_left_lpad_table(self):
        self.assert_from_file('6x4a-label-some-label-left-lpad')

    def test_6x4a_name_label_some_table(self):
        self.assert_from_file('6x4a-name-label-some')

    def test_2x2a_4x3a_6x4a_tables(self):
        self.assert_from_file([
            '2x2a',
            '4x3a',
            '6x4a',
        ])

    def test_4x3a_2x2a_6x4a_tables(self):
        self.assert_from_file([
            '4x3a',
            '2x2a',
            '6x4a',
        ])

    def test_6x4a_4x3a_2x2a_tables(self):
        self.assert_from_file([
            '6x4a',
            '4x3a',
            '2x2a',
        ])

    def test_2x2a_4x3a_6x4a_labels_tables(self):
        self.assert_from_file([
            '2x2a',
            '4x3a-label',
            '6x4a-label-some',
        ])

        self.assert_from_file([
            '2x2a',
            '4x3a-label',
            '6x4a-label-some-label-left',
        ])

    def test_4x3a_2x2a_6x4a_labels_tables(self):
        self.assert_from_file([
            '4x3a-label',
            '2x2a',
            '6x4a-label-some',
        ])

        self.assert_from_file([
            '4x3a-label',
            '2x2a',
            '6x4a-label-some-label-left',
        ])

    def test_4x3a_6x4a_with_name_and_labels(self):
        self.assert_from_file([
            '4x3a-name-label',
            '6x4a-name-label-some',
        ])

    def test_2x2a_4x3a_6x4a_with_name_and_labels(self):
        self.assert_from_file([
            '2x2a',
            '4x3a-name-label',
            '6x4a-name-label-some',
        ])

    def test_4x3a_2x2a_6x4a_with_name_and_labels(self):
        self.assert_from_file([
            '4x3a-name-label',
            '2x2a',
            '6x4a-name-label-some',
        ])

    def test_6x4a_4x3a_2x2a_with_name_and_labels(self):
        self.assert_from_file([
            '6x4a-name-label-some',
            '4x3a-name-label',
            '2x2a',
        ])

        self.assert_from_file([
            '6x4a-name-label-some-label-left',
            '4x3a-name-label',
            '2x2a',
        ])

    def assert_from_file(self, names, **kwargs):
        if kwargs.get('print_output', False): #pragma: no cover
            print()
            print(names)

        if not isinstance(names, list):
            names = [ names ]

        tables = []
        for tblname in names:
            fname = os.path.join(TABLES_DIR, tblname + '.txt')
            tables.append(create_table_from_file(fname, border=True))

        fname = os.path.join(TABLES_DIR, ','.join(names) + '.txt.border.output')
        self.assert_file(fname, tables, **kwargs)

        for tbl in tables:
            tbl.cell_info = cell_unborder

        fname = os.path.join(TABLES_DIR, ','.join(names) + '.txt.output')
        self.assert_file(fname, tables, **kwargs)

    def assert_file(self, fname, tables, **kwargs):
        if isinstance(tables, list):
            output = Table.draw_tables(tables)
        else:
            output = tables.draw_table()

        if kwargs.get('print_output', False):
            print(output)

        with open(fname, 'r') as outfile:
            self.line_comparison(output, outfile.read())

    def line_comparison(self, first, second):
        alines = first.split('\n')
        blines = second.split('\n')

        self.assertEqual(len(alines), len(blines))

        for i in range(len(alines)): #pylint: disable=consider-using-enumerate
            self.assertEqual(alines[i].rstrip(), blines[i].rstrip())

def create_table_from_file(fname, **kwargs):
    with open(fname, 'r') as file:
        data = []
        labels = []
        has_labels = False

        opts = {
            'name': None,
            'label_left': False,
            'label_lpad': False
        }

        for line in file:
            if line.startswith('#'):
                modifier = line[1:].strip()
                if modifier.startswith('name='):
                    opts['name'] = modifier.split('=')[1]
                elif modifier == 'label_left':
                    opts['label_left'] = True
                elif modifier == 'label_lpad':
                    opts['label_lpad'] = True
                continue

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

        return create_table(data, labels=labels, **opts, **kwargs)

def create_table(data, **kwargs):
    labels = kwargs.get('labels')
    border = kwargs.get('border', True)

    tbl = Table(cell_bordered if border else cell_unborder)
    tbl.table_name = kwargs.get('name')
    tbl.data = data
    tbl.left_label = kwargs.get('label_left', False)
    tbl.label_lpad = kwargs.get('label_lpad', False)

    if labels is not None:
        tbl.row_labels = labels

    return tbl

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
