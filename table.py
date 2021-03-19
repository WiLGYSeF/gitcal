class Table:
    def __init__(self, cell_info):
        self.data = [[]]
        self.cell_info = cell_info

        self.row_labels = {}

    def set_table_data(self, data):
        self.data = data

    def draw_table(self):
        return Table.draw_tables( (self,) )

    def draw_table_iter(self):
        row_idx = 0
        for row in self.data:
            for char_row in self.draw_row_iter(row, row_idx):
                yield char_row
            row_idx += 1

    def draw_row(self, row, row_idx=-1):
        return '\n'.join(self.draw_row_iter(row, row_idx))

    def draw_row_iter(self, row, row_idx=-1):
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

            if row_idx != -1:
                label = self.get_row_label(row_idx)
                if label is not None:
                    chars += ' ' + label
            yield chars

    def draw_cell_iter(self, val):
        for res in self.cell_info.fnc_draw_cell(self.cell_info.fnc_getval(val)):
            yield res

    def get_row_label(self, row_idx):
        if isinstance(self.row_labels, dict):
            return self.row_labels.get(row_idx)

        if len(self.row_labels) <= row_idx:
            return None
        return self.row_labels[row_idx]

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
        tbl_count = len(tablelist)
        spacing = kwargs.get('spacing', 2)
        row_counter = [ 0 ] * tbl_count
        lne_counter = [ 0 ] * tbl_count
        result = ''
        last_result_len = 0

        gen_list = [ tbl.draw_table_iter() for tbl in tablelist ]
        gen_done = set()

        while len(gen_done) != tbl_count:
            draws_done = 0

            for gidx in range(tbl_count): # pylint: disable=consider-using-enumerate
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

                                if tbl.cell_info.has_border \
                                 and tbl.row_count() != row_counter[gidx]:
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

                if gidx != tbl_count - 1:
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
