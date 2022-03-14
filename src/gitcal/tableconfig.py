from datetime import datetime, timedelta
import typing

class TableConfig:
    def __init__(self, **kwargs):
        self.tbl_name: str = kwargs.get('tbl_name')
        self.color: bool = kwargs.get('color')
        self.border = kwargs.get('border')
        self.col: int = kwargs.get('col')
        self.delta: timedelta = kwargs.get('delta')
        self.filter_names: typing.List[str] = kwargs.get('filter_names')
        self.start: datetime = kwargs.get('start')
        self.end: datetime = kwargs.get('end')

        self.collapse: int = kwargs.get('collapse')
        self.collapse_flag: int = kwargs.get('collapse_flag')

        self.label_left: bool = kwargs.get('label_left')
        self.label_sep: str = kwargs.get('label_sep')
        self.label: bool = kwargs.get('label')
        self.label_inclusive: bool = kwargs.get('label_inclusive')
        self.long_label: bool = kwargs.get('long_label')

        self.threshold: int = kwargs.get('threshold')
        self.num: bool = kwargs.get('num')
