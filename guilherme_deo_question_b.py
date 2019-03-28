import sys
import argparse
import re
# Question B asks to implement some code which checks whether the input version_1 is bigger, smaller or equal to the
# second input version_2


def parse_input(args):
    parser = argparse.ArgumentParser(description='Process two strings (considered as version) and check if the first ' +
                                                 'one is bigger, equal or smaller than the second one. \n' +
                                                 'Letters and numbers are considered for comparison while . , - and _' +
                                                 ' are considered as version separators.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('version_1', type=str, help='String representing first version to compare')
    parser.add_argument('version_2', type=str, help='String representing second version to compare')

    parsed = parser.parse_args(args)
    return parsed.version_1, parsed.version_2


def check_version(v_1, v_2):
    """
    This function checks the relation between version_1 and version_2 (bigger, smaller, equal)
    This function is considering the same rules as Python for checking if bigger or small,
    which means that small case letters are bigger than upper case, and that numbers are smaller than letters.
    'z' > 'a' > 'Z' > 'A' > '1' --- 0-9,A-Z,a-z
    :param v_1: The version which the result will correspond to
    :param v_2: The version to be compared agains
    :return: A string saying if version_1 is either bigger, smaller or equal to version_2
    """
    version_1_pieces = re.split(r'[\.,\-_]', v_1)
    version_2_pieces = re.split(r'[\.,\-_]', v_2)
    max_comparison = min(len(version_1_pieces), len(version_2_pieces))
    for idx in range(max_comparison):
        if version_1_pieces[idx] > version_2_pieces[idx]:
            return 'Version 1 is GREATER than Version 2'
        elif version_1_pieces[idx] < version_2_pieces[idx]:
            return 'Version 1 is SMALLER than Version 2'
    if len(version_1_pieces) > len(version_2_pieces):
        return 'Version 1 is GREATER than Version 2'
    elif len(version_1_pieces) < len(version_2_pieces):
        return 'Version 1 is SMALLER than Version 2'
    return 'Both versions are EQUAL'


if __name__ == "__main__":
    version_1, version_2 = parse_input(sys.argv[1:])
    print(check_version(version_1, version_2))
