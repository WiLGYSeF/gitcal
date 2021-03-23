import os
import unittest
import unittest.mock as mock

import gitcal


LOG_DIR = os.path.join(os.path.dirname(__file__), 'mocked_data')


class GitcalTest(unittest.TestCase):
    def test_draw_tables(self):
        self.assert_draw_tables('git-log', [])

    def test_draw_tables_two(self):
        self.assert_draw_tables('git-log', ['--table'])

    def test_draw_tables_name(self):
        self.assert_draw_tables('git-log', ['--tbl-name', 'here is a name'])

    def test_draw_tables_one_name(self):
        self.assert_draw_tables('git-log', ['--tbl-name', 'master', '-T'])

    def test_draw_tables_name_long(self):
        self.assert_draw_tables('git-log', [
            '--tbl-name', 'here is a much longer name that is longer than the table'
        ])

    def test_draw_tables_name_long_two(self):
        self.assert_draw_tables('git-log', [
            '--tbl-name', 'here is a much longer name that is longer than the table',
            '--table'
        ])

    def test_draw_tables_no_border(self):
        self.assert_draw_tables('git-log', ['-B'])

    def test_draw_tables_no_color(self):
        self.assert_draw_tables('git-log', ['--no-color'])

    def test_draw_tables_no_border_color(self):
        self.assert_draw_tables('git-log', ['-B', '--no-color'])

    def test_draw_tables_col(self):
        self.assert_draw_tables('git-log', ['-c', '4'])

    def test_draw_tables_col_guess(self):
        self.assert_draw_tables('git-log', ['-c', 'guess'])

    def test_draw_tables_col_fail(self):
        with self.assertRaises(ValueError):
            self.assert_draw_tables('git-log', ['-c', 'asdf'])

    def test_draw_tables_delta_1h(self):
        self.assert_draw_tables('git-log', ['-d', '1h'])

    def test_draw_tables_delta_2h(self):
        self.assert_draw_tables('git-log', ['-d', '2h'])

    def test_draw_tables_delta_3h(self):
        self.assert_draw_tables('git-log', ['-d', '3h'])

    def test_draw_tables_delta_4h(self):
        self.assert_draw_tables('git-log', ['-d', '4h'])

    def test_draw_tables_delta_9h(self):
        self.assert_draw_tables('git-log', ['-d', '9h'])

    def test_draw_tables_delta_1h_24col(self):
        self.assert_draw_tables('git-log', ['-d', '1h', '-c', '24'])

    def test_draw_tables_delta_2(self):
        self.assert_draw_tables('git-log', ['-d', '2'])

    def test_draw_tables_delta_2d(self):
        self.assert_draw_tables('git-log', ['-d', '2d'])

    def test_draw_tables_delta_2day(self):
        self.assert_draw_tables('git-log', ['-d', '2day'])

    def test_draw_tables_delta_2days(self):
        self.assert_draw_tables('git-log', ['-d', '2 days'])

    def test_draw_tables_delta_30m(self):
        self.assert_draw_tables('git-log', ['-d', '30m'])

    def test_draw_tables_delta_fail(self):
        with self.assertRaises(ValueError):
            self.assert_draw_tables('git-log', ['-d', 'asdf'])
        with self.assertRaises(ValueError):
            self.assert_draw_tables('git-log', ['-d', '1h 30m'])

    def test_draw_tables_filter_wilgysef(self):
        self.assert_draw_tables('git-log-multi', ['-f', 'WiLGYSeF'])

    def test_draw_tables_filter_aaasdf(self):
        self.assert_draw_tables('git-log-multi', ['-f', 'aaasdf'])

    def test_draw_tables_filter_total_wilgysef_aaasdf(self):
        self.assert_draw_tables('git-log-multi', [
            '-T',
            '-f', 'WiLGYSeF',
            '-T',
            '-f', 'aaasdf'
        ])

    def test_draw_tables_filter_total_wilgysef_aaasdf_named(self):
        self.assert_draw_tables('git-log-multi', [
            '--tbl-name', 'total',
            '-T',
            '--tbl-name', 'WiLGYSeF',
            '-f', 'WiLGYSeF',
            '-T',
            '--tbl-name', 'aaasdf',
            '-f', 'aaasdf'
        ])

    def test_draw_cell_bordered(self):
        for i in range(5):
            val = 'a' * i
            gen = gitcal.draw_cell_bordered(val)

            self.assertEqual(next(gen), '+--+')
            self.assertEqual(next(gen), '|%s|' % val)
            self.assertEqual(next(gen), '+--+')
            self.assertRaises(StopIteration, next, gen)

    def test_draw_cell_unborder(self):
        for i in range(5):
            val = 'a' * i
            gen = gitcal.draw_cell_unborder(val)

            self.assertEqual(next(gen), val)
            self.assertRaises(StopIteration, next, gen)

    def assert_draw_tables(self, name, args, print_output=False, write_output=False):
        fname = os.path.join(LOG_DIR, name + '.txt')

        def get_data(args):
            with open(fname, 'rb') as file:
                return file.read()

        with mock.patch('subprocess.check_output', get_data):
            result = gitcal.draw_tables_from_args(args)

            if print_output: #pragma: nocover
                print(name, args)
                print(result)

            outfname = '%s[%s].output' % (fname, ','.join(args))

            if write_output: #pragma: nocover
                with open(outfname, 'w') as file:
                    file.write(result)

            with open(outfname, 'r') as file:
                self.line_comparison(result, file.read())

    def line_comparison(self, first, second):
        alines = first.split('\n')
        blines = second.split('\n')

        self.assertEqual(len(alines), len(blines))

        for i in range(len(alines)): #pylint: disable=consider-using-enumerate
            self.assertEqual(alines[i].rstrip(), blines[i].rstrip())
