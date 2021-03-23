import os
import unittest
import unittest.mock as mock

import gitcal


LOG_DIR = os.path.join(os.path.dirname(__file__), 'mocked_data')


class GitcalTest(unittest.TestCase):
    def test_draw_tables(self):
        self.assert_draw_tables('git-log', [], print_output=True, write_output=True)

    def test_draw_tables_two(self):
        self.assert_draw_tables('git-log', ['--table'], print_output=True, write_output=True)

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

            if write_output:
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
