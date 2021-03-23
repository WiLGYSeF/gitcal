import unittest

import gitcal


class GitcalTest(unittest.TestCase):
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
