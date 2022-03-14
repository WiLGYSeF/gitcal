from datetime import datetime, timedelta
import subprocess
import typing

from .table import CellInfo, Table

class Commit:
    def __init__(self, shorthash: str, dtime: datetime, name: str):
        self.shorthash: str = shorthash
        self.datetime: datetime = dtime
        self.author_name: str = name

    def json(self) -> dict:
        return {
            'shorthash': self.shorthash,
            'datetime': str(self.datetime),
            'author_name': self.author_name
        }

def create_table_from_commits(cell_info: CellInfo, commits: typing.List[Commit], **kwargs) -> Table:
    col_count: int = kwargs.get('col_count', 7)
    make_labels: bool = kwargs.get('make_labels', True)
    labels_inclusive: bool = kwargs.get('labels_inclusive', True)
    long_labels: bool = kwargs.get('long_labels', True)

    delta: timedelta = kwargs.get('delta', timedelta(days=1))
    start_date: typing.Optional[datetime] = kwargs.get('start_date')
    end_date: typing.Optional[datetime] = kwargs.get('end_date')

    filter_names: typing.Optional[typing.List[str]] = kwargs.get('filter_names')
    if filter_names is None:
        filter_names = []

    tbl = Table(cell_info)

    data = []
    row = []
    labels = []
    start_idx = 0
    counter = 0

    first_date = commits[0].datetime

    if start_date is None:
        ideal_date = get_ideal_startdate(first_date, delta)
        if ideal_date is not None and (end_date is None or ideal_date < end_date):
            start_date = ideal_date

    if start_date is not None:
        if start_date > first_date:
            while start_idx < len(commits) and commits[start_idx].datetime < start_date:
                start_idx += 1
            if start_idx == len(commits):
                return tbl
            first_date = commits[start_idx].datetime
        else:
            first_date = start_date

    curdate = datetime(first_date.year, first_date.month, first_date.day)
    if make_labels:
        labels.append(shortdate(
            curdate,
            delta,
            include_year=long_labels,
        ))
    curdate += delta

    def append(val: int) -> None:
        nonlocal curdate, row

        row.append(val)
        if len(row) == col_count:
            data.append(row)
            row = []

            if make_labels:
                labels[-1] += ' - %s' % shortdate(
                    (curdate - delta) if labels_inclusive else curdate,
                    delta,
                    include_year=long_labels,
                )
                labels.append(shortdate(
                    curdate,
                    delta,
                    include_year=long_labels,
                ))

        curdate += delta

    if start_date is not None:
        while curdate < commits[0].datetime:
            append(0)

    for idx in range(start_idx, len(commits)):
        commit = commits[idx]
        if end_date is not None and commit.datetime > end_date:
            break
        if len(filter_names) != 0 and commit.author_name not in filter_names:
            continue

        if curdate < commit.datetime:
            append(counter)
            while curdate < commit.datetime:
                append(0)

            counter = 1
        else:
            counter += 1

    if counter != 0:
        append(counter)

    if end_date is not None:
        while curdate < end_date:
            append(0)

    if len(row) != 0:
        data.append(row)
        for _ in range(col_count - len(row)):
            append(0)

        data.pop()
        if make_labels:
            labels.pop()

    tbl.data = data
    if make_labels:
        tbl.row_labels = labels

    return tbl

def get_ideal_startdate(start_date: datetime, delta: timedelta) -> typing.Optional[datetime]:
    if delta == timedelta(days=1):
        dtime = datetime(start_date.year, start_date.month, start_date.day)
        while dtime.weekday() != 6:
            dtime -= delta
        return dtime
    if delta == timedelta(hours=1):
        return datetime(start_date.year, start_date.month, start_date.day)
    return None

def shortdate(dtime: datetime, delta: timedelta, include_year: bool = True) -> str:
    if delta.seconds % 86400 == 0:
        if include_year:
            return '%04d-%02d-%02d' % (dtime.year, dtime.month, dtime.day)
        return '%02d-%02d' % (dtime.month, dtime.day)
    if delta.seconds % 3600 == 0:
        if include_year:
            return '%04d-%02d-%02d %02dh' % (dtime.year, dtime.month, dtime.day, dtime.hour)
        return '%02d-%02d %02dh' % (dtime.month, dtime.day, dtime.hour)
    return str(dtime)

def get_commit_data() -> typing.List[Commit]:
    output = subprocess.check_output([
        'git', 'log',
        '--pretty=format:%h %ad %an',
        '--date=format:%Y%m%d%H%M%S'
    ])
    commits: typing.List[Commit] = []

    for line in filter(lambda x: len(x) > 0, map(lambda x: x.decode('utf-8'), output.split(b'\n'))):
        spl = line.split(' ')
        shorthash = spl[0]
        dtime = datetime.strptime(spl[1], '%Y%m%d%H%M%S')
        name = ' '.join(spl[2:])

        commits.append(Commit(shorthash, dtime, name))
    return commits

def get_users_from_commits(commits: typing.List[Commit]) -> typing.Set[str]:
    return set(map(lambda c: c.author_name, commits))
