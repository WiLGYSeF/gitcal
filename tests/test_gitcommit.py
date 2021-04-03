import datetime
import os
import unittest
import unittest.mock as mock

import gitcommit


def mkdtime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


LOG_DIR = os.path.join(os.path.dirname(__file__), 'mocked_data')

DTIME = 'dtime'
DELTA = 'delta'
INCLUDE_YEAR = 'include_year'
RESULT = 'result'

SHORTDATE = [
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(days=1),
        INCLUDE_YEAR: True,
        RESULT: '2021-03-23'
    },
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(days=1),
        INCLUDE_YEAR: False,
        RESULT: '03-23'
    },
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(hours=4),
        INCLUDE_YEAR: True,
        RESULT: '2021-03-23 10h'
    },
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(hours=4),
        INCLUDE_YEAR: False,
        RESULT: '03-23 10h'
    },
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(hours=4, minutes=18),
        INCLUDE_YEAR: True,
        RESULT: '2021-03-23 10:24:12'
    },
    {
        DTIME: mkdtime('2021-03-23 10:24:12'),
        DELTA: datetime.timedelta(hours=4, minutes=18),
        INCLUDE_YEAR: False,
        RESULT: '2021-03-23 10:24:12'
    },
]


class GitCommitTest(unittest.TestCase):
    def test_shortdate(self):
        for entry in SHORTDATE:
            self.assertEqual(gitcommit.shortdate(
                entry[DTIME],
                entry[DELTA],
                include_year=entry[INCLUDE_YEAR],
            ), entry[RESULT])

    def test_get_commit_data(self):
        logfile = os.path.join(LOG_DIR, 'git-log.txt')

        def get_data(args):
            with open(logfile, 'rb') as file:
                return file.read()

        with open(logfile + '.commits.output', 'r') as file:
            with mock.patch('subprocess.check_output', get_data):
                commits = gitcommit.get_commit_data()
            self.assertEqual(file.read().rstrip('\n'), str(commits))

    def test_get_users_from_commits(self):
        logfile = os.path.join(LOG_DIR, 'git-log-multi.txt')

        def get_data(args):
            with open(logfile, 'rb') as file:
                return file.read()

        with mock.patch('subprocess.check_output', get_data):
            users = gitcommit.get_users_from_commits()
        self.assertEqual(users, set(['WiLGYSeF', 'aaasdf']))
