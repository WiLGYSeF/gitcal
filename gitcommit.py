import datetime
import subprocess

from table import Table


def create_table_from_commits(cell_info, commits, **kwargs):
    delta = kwargs.get('delta', datetime.timedelta(days=1))
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    make_labels = kwargs.get('make_labels', True)
    col_count = kwargs.get('col_count', 7)
    filter_names = kwargs.get('filter_names')
    if filter_names is not None and not isinstance(filter_names, list):
        filter_names = [ filter_names ]

    tbl = Table(cell_info)

    data = []
    row = []
    labels = []
    start_idx = 0
    counter = 0

    if start_date is not None:
        while start_idx < len(commits) and commits[start_idx]['datetime'] < start_date:
            start_idx += 1

    first_date = commits[start_idx]['datetime']
    curdate = datetime.datetime(first_date.year, first_date.month, first_date.day)
    if make_labels:
        labels.append(shortdate(curdate, delta))
    curdate += delta

    def append(val):
        nonlocal curdate, row

        row.append(val)

        if len(row) == col_count:
            data.append(row)
            row = []

            if make_labels:
                labels[-1] += ' - %s' % shortdate(curdate - delta, delta)
                labels.append(shortdate(curdate, delta))

        curdate += delta

    for idx in range(start_idx, len(commits)):
        commit = commits[idx]
        if start_date is not None and commit['datetime'] < start_date:
            continue
        if end_date is not None and commit['datetime'] > end_date:
            break
        if filter_names is not None and commit['name'] not in filter_names:
            continue

        if curdate < commit['datetime']:
            append(counter)
            while curdate < commit['datetime']:
                append(0)

            counter = 1
        else:
            counter += 1

    if counter != 0:
        append(counter)

    if len(row) != 0:
        data.append(row)
        for _ in range(col_count - len(row)):
            append(0)

        data.pop()
        if make_labels:
            labels.pop()

    tbl.set_table_data(data)
    if make_labels:
        tbl.row_labels = labels

    return tbl

def shortdate(dtime, delta):
    if delta == datetime.timedelta(days=1):
        return '%04d-%02d-%02d' % (dtime.year, dtime.month, dtime.day)
    if delta == datetime.timedelta(hours=1):
        return '%04d-%02d-%02d %02dh' % (dtime.year, dtime.month, dtime.day, dtime.hour)
    return str(dtime)

def get_commit_data():
    output = subprocess.check_output([
        'git', 'log',
        '--pretty=format:%h %ad %an',
        '--date=format:%Y%m%d%H%M%S'
    ])
    commits = []

    for line in output.split(b'\n'):
        line = line.decode('utf-8')

        spl = line.split(' ')
        shorthash = spl[0]
        dtime = datetime.datetime.strptime(spl[1], '%Y%m%d%H%M%S')
        name = ' '.join(spl[2:])

        commits.append({
            'shorthash': shorthash,
            'datetime': dtime,
            'name': name
        })
    return commits
