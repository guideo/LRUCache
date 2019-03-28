import unittest

from guilherme_deo_question_a import *


class Tests(unittest.TestCase):

    def test_if_argparse_works(self):
        line1, line2 = parse_input(['1', '2', '3', '4'])
        self.assertEqual((1, 2), line1)
        self.assertEqual((3, 4), line2)

    def test_if_overlap_function_works_overlap_case_1(self):
        # OVERLAP: end of line 1 - beginning of line 2
        self.assertTrue(do_overlap((0, 4), (2, 6)))

    def test_if_overlap_function_works_overlap_case_line_inside_another(self):
        # OVERLAP: line 1 is inside line 2
        self.assertTrue(do_overlap((0, 4), (-2, 8)))

    def test_if_overlap_function_works_overlap_case_2(self):
        # OVERLAP: beginning of line 1 - end of line 2 -> with lines values backwards (bigger X before smaller)
        self.assertTrue(do_overlap((10, 5), (7, 4)))

    def test_if_not_overlap_case_1(self):
        # DO NOT OVERLAP
        self.assertFalse(do_overlap((0, 4), (5, 8)))

    def test_if_not_overlap_when_sharing_one_single_point(self):
        # DO NOT OVERLAP: only 'touches' (considering that sharing a point is not overlapping)
        self.assertFalse(do_overlap((0, 4), (4, 8)))


if __name__ == '__main__':
    unittest.main()
