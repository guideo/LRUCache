import unittest

from guilherme_deo_question_b import *


class Tests(unittest.TestCase):

    def test_if_argparse_works(self):
        version1, version2 = parse_input(['123.45b-asd_7,5', 'Abc,123.45-_10'])
        self.assertEqual('123.45b-asd_7,5', version1)
        self.assertEqual('Abc,123.45-_10', version2)

    # Considering the same rules as Python for checking if bigger or small,
    # which means that small case letters are bigger than upper case, and that numbers are smaller than letters.
    # 'z' > 'a' > 'Z' > 'A' > '1' --- 0-9,A-Z,a-z
    def test_if_version_check_function_works_case_1(self):
        self.assertEqual('Version 1 is GREATER than Version 2', check_version('1.2-a5_6,2', '1.2-a5_6,1'))

    def test_if_version_check_function_works_case_2(self):
        self.assertEqual('Version 1 is SMALLER than Version 2', check_version('1.2-a5_6,2', '1.2-a5_6,3'))

    def test_if_version_check_function_works_case_3(self):
        self.assertEqual('Both versions are EQUAL', check_version('1.2-a5_6,2', '1.2-a5_6,2'))

    def test_if_version_check_function_works_case_4(self):
        self.assertEqual('Version 1 is GREATER than Version 2', check_version('1.2-a5_6,2', '1.2-a5_6'))

    def test_if_version_check_function_works_case_5(self):
        self.assertEqual('Version 1 is SMALLER than Version 2', check_version('1.2-a5_6,2', '1.2-a5_6,2z'))

    def test_if_version_check_function_works_case_6(self):
        self.assertEqual('Version 1 is SMALLER than Version 2', check_version('A10-7.75_b2', 'a10-7.75_b2'))

    def test_if_version_check_function_works_case_7(self):
        self.assertEqual('Version 1 is GREATER than Version 2', check_version('1.2-a6_6,2', '1.2-a5_6,3'))


if __name__ == '__main__':
    unittest.main()
