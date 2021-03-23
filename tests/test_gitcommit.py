import datetime
import unittest

import gitcommit


def mkdtime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


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
    }
]


class GitCommitTest(unittest.TestCase):
    def test_shortdate(self):
        for entry in SHORTDATE:
            self.assertEqual(gitcommit.shortdate(
                entry[DTIME],
                entry[DELTA],
                include_year=entry[INCLUDE_YEAR],
            ), entry[RESULT])
