import sys
import argparse
# Question A asks to check if two lines in the X Axis overlap


def parse_input(args):
    parser = argparse.ArgumentParser(description='Process two lines and see if they overlap.')
    parser.add_argument('line_1', nargs=2, type=int, help='Tuple representing line 1')
    parser.add_argument('line_2', nargs=2, type=int, help='Tuple representing line 2')

    parsed = parser.parse_args(args)
    return tuple(parsed.line_1), tuple(parsed.line_2)


def do_overlap(line_1, line_2):
    # Making sure that the line[0] is less than line[1]
    ordered_line_1 = (min(line_1), max(line_1))
    ordered_line_2 = (min(line_2), max(line_2))

    # Getting the 'biggest start of a line' and the 'minor end of a line'
    overlap_start = max(ordered_line_1[0], ordered_line_2[0])
    overlap_end = min(ordered_line_1[1], ordered_line_2[1])

    # If the minor end is after the max start, then we have a overlap
    if overlap_end > overlap_start:
        return True
    return False


if __name__ == "__main__":
    lines = parse_input(sys.argv[1:])
    print(do_overlap(lines[0], lines[1]))
