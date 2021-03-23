import datetime
import unittest

import args


DELTA = 'delta'
MINCOL = 'mincol'
MAXCOL = 'maxcol'
RESULT = 'result'

GUESS_COL_COUNT = [
    {
        DELTA: datetime.timedelta(days=1),
        MINCOL: 4,
        MAXCOL: 12,
        RESULT: 7
    },
    {
        DELTA: datetime.timedelta(days=1),
        MINCOL: 1,
        MAXCOL: 12,
        RESULT: 7
    },
    {
        DELTA: datetime.timedelta(days=1),
        MINCOL: 1,
        MAXCOL: 5,
        RESULT: 1
    },
    {
        DELTA: datetime.timedelta(days=1),
        MINCOL: 4,
        MAXCOL: 5,
        RESULT: None
    },
    {
        DELTA: datetime.timedelta(hours=1),
        MINCOL: 4,
        MAXCOL: 12,
        RESULT: 6
    },
    {
        DELTA: datetime.timedelta(hours=3),
        MINCOL: 4,
        MAXCOL: 12,
        RESULT: 8
    },
]


class ArgsTest(unittest.TestCase):
    def test_guess_col_count(self):
        for entry in GUESS_COL_COUNT:
            self.assertEqual(args.guess_col_count(
                entry[DELTA],
                min_col=entry[MINCOL],
                max_col=entry[MAXCOL]
            ), entry[RESULT])
