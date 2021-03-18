#!/usr/bin/env python3

class Table:
    def __init__(self):
        self.cell_data = [[]]

        self.cell_height = 3
        self.cell_width = 4
        self.cell_has_border = True

    def draw_table(self):
        table = ""
        idx = 0
        row = 1

        for result in self.draw_table_iter():
            idx += 1
            if idx == self.cell_height and row < len(self.cell_data):
                row += 1
                idx = 0
                if self.cell_has_border:
                    continue

            table += result + '\n'
        return table

    def draw_table_iter(self):
        for row in range(len(self.cell_data)):
            for char_row in self.draw_row_iter(self.cell_data[row]):
                yield char_row

    def draw_row(self, row):
        return '\n'.join(self.draw_row_iter(row))

    def draw_row_iter(self, row):
        gen_list = [ self.draw_cell_iter(row[i]) for i in range(len(row)) ]

        for _ in range(self.cell_height):
            chars = ''
            first = True

            for gen in gen_list:
                res = next(gen)
                if not first and self.cell_has_border:
                    chars += res[1:]
                else:
                    chars += res

                first = False
            yield chars

    def draw_cell_iter(self, val):
        yield '+--+'
        yield '|%s|' % self.getval(val)
        yield '+--+'
        #yield self.getval(val)

    def getval(self, val):
        if val == 0:
            return '  '
        return '\x1b[42m  \x1b[0m'


tbl = Table()
tbl.cell_data = [
    [1, 0, 1, 1],
    [1, 1, 0, 0],
    [1, 0, 1, 0]
]
print(tbl.draw_table(), end='')
