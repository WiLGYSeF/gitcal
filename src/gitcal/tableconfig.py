class TableConfig:
    def __init__(self, **kwargs):
        self.tbl_name = kwargs.get('tbl_name')
        self.color = kwargs.get('color')
        self.border = kwargs.get('border')
        self.col = kwargs.get('col')
        self.delta = kwargs.get('delta')
        self.filter_names = kwargs.get('filter_names')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')

        self.collapse = kwargs.get('collapse')
        self.collapse_flag = kwargs.get('collapse_flag')

        self.label_left = kwargs.get('label_left')
        self.label_sep = kwargs.get('label_sep')
        self.label = kwargs.get('label')
        self.label_inclusive = kwargs.get('label_inclusive')
        self.long_label = kwargs.get('long_label')

        self.threshold = kwargs.get('threshold')
        self.num = kwargs.get('num')
