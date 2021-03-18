#!/usr/bin/env python3

class Table:
    def __init__(self, cell_info):
        self.data = [[]]
        self.cell_info = cell_info

    def set_table_data(self, data):
        self.data = data

    def draw_table(self):
        row_count = len(self.data)
        table = ""
        idx = 0
        row = 1

        for result in self.draw_table_iter():
            idx += 1
            if idx == self.cell_info.height and row < row_count:
                row += 1
                idx = 0
                if self.cell_info.has_border:
                    continue

            table += result + '\n'
        return table

    def draw_table_iter(self):
        for row in self.data:
            for char_row in self.draw_row_iter(row):
                yield char_row

    def draw_row(self, row):
        return '\n'.join(self.draw_row_iter(row))

    def draw_row_iter(self, row):
        gen_list = [ self.draw_cell_iter(row[i]) for i in range(len(row)) ]

        for _ in range(self.cell_info.height):
            chars = ''
            first = True

            for gen in gen_list:
                res = next(gen)
                if not first and self.cell_info.has_border:
                    chars += res[1:]
                else:
                    chars += res

                first = False
            yield chars

    def draw_cell_iter(self, val):
        for res in self.cell_info.fnc_draw_cell(self.cell_info.fnc_getval(val)):
            yield res

class CellInfo:
    def __init__(self, **kwargs):
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.has_border = kwargs['has_border']

        self.fnc_draw_cell = kwargs['drawcell']
        self.fnc_getval = kwargs.get('getval', lambda x: x)


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

    tbl = Table(cell_unborder)
    tbl.set_table_data([
        [1, 0, 1, 1],
        [1, 1, 0, 0],
        [1, 0, 1, 0]
    ])
    print(tbl.draw_table(), end='')

if __name__ == '__main__':
    main()
