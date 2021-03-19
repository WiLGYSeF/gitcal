#!/usr/bin/env python3

class Table:
    def __init__(self, cell_info):
        self.data = [[]]
        self.cell_info = cell_info

    def set_table_data(self, data):
        self.data = data

    def draw_table(self):
        table = ""
        idx = 0
        row = 1

        for result in self.draw_table_iter():
            idx += 1
            if idx == self.cell_info.height and row < self.row_count():
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

    def row_length(self):
        if self.cell_info.has_border:
            return self.col_count() * self.cell_info.width - self.col_count() + 1
        return self.col_count() * self.cell_info.width

    def row_count(self):
        return len(self.data)

    def col_count(self):
        return len(self.data[0])

    @staticmethod
    def draw_tables(tablelist, **kwargs):
        spacing = kwargs.get('spacing', 2)
        row_counter = [ 0 ] * len(tablelist)
        lne_counter = [ 0 ] * len(tablelist)
        result = ''
        last_result_len = 0

        gen_list = [ tbl.draw_table_iter() for tbl in tablelist ]
        gen_done = set()

        while len(gen_done) != len(gen_list):
            draws_done = 0

            for gidx in range(len(gen_list)): # pylint: disable=consider-using-enumerate
                gen = gen_list[gidx]
                tbl = tablelist[gidx]
                do_draw = gidx not in gen_done

                if do_draw:
                    while True:
                        try:
                            res = next(gen)
                            lne_counter[gidx] += 1
                            if lne_counter[gidx] == tbl.cell_info.height:
                                row_counter[gidx] += 1
                                lne_counter[gidx] = 0

                                if tbl.cell_info.has_border and tbl.row_count() != row_counter[gidx]:
                                    do_draw = True
                                    continue
                        except StopIteration:
                            do_draw = False
                            gen_done.add(gidx)
                        break

                if do_draw:
                    result += res
                    draws_done += 1
                else:
                    result += ' ' * (tbl.row_length())

                if gidx != len(gen_list) - 1:
                    result += ' ' * spacing

            if draws_done == 0:
                result = result[:last_result_len]
            else:
                result += '\n'
            last_result_len = len(result)

        return result

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

    tbl = Table(cell_bordered)
    tbl.set_table_data([
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]
    ])

    tbl2 = Table(cell_bordered)
    tbl2.set_table_data([
        [0, 1, 1, 1],
        [0, 1, 0, 0],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
    ])

    print(tbl.draw_table())

    print(Table.draw_tables( (tbl, tbl2) ))

if __name__ == '__main__':
    main()
