import os

import util
from output import Writer
from solve_log import Log
from sudoku import Sudoku

__author__ = 'Michael'

PATH = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(PATH, "in")
OUT = os.path.join(PATH, "out")

log = Log()
writer = None


class Changed(Exception):
    def __init__(self, moveto):
        self.moveto = moveto


solve_methods = dict()


def solve_method(index):
    def decor(func):
        solve_methods[index] = func
        return func

    return decor


def section_remove(s, sec, numbers):
    result = 0
    for i in sec:
        if s.remove_numbers(i, numbers):
            result = max(result, 1)
            if len(s[i]) == 1:
                result = 2
                log.append("Filled item[{0}] = {1}", i, s[i][0])
            else:
                log.append("Reduced item[{0}] to {1}", i, s[i])
    return result


@log.rollback
def _check_house(s, h):
    # Within a house, remove numbers already settled from unsettled tiled
    log.append("In House {0}:", h)
    log.indent()
    changed = section_remove(s, s.unsettled_tiles(h), s.settled_numbers(h))
    log.dedent()
    if changed == 2:
        # New settled numbers added
        log.indent()
        _check_house(s, h)
        log.dedent()
    return changed


@solve_method(0)
def check_house(s):
    changed = 0
    for h in s.houses:
        changed = max(changed, _check_house(s, h))
    if changed == 2:
        raise Changed(0)


def get_subsets(st):
    # Returns a list of all subsets
    result = [[]]
    for i in st:
        result += [s + [i] for s in result]
    return result


@log.rollback
def _check_group(s, h):
    # Within a house, find groups for unsettled numbers
    # A group is N tiles where only N unsettled numbers can exist
    # Thus these N unsettled numbers cannot be on any other tile
    # For example, if there are three unsettled tiles in a house
    # [4, 7], [4, 7], [4, 6, 7]
    # Then the first two tiles make a group, and the third one can only be [6]
    log.append("In House {0}:", h)
    changed = 0
    unsettled_tiles = s.unsettled_tiles(h)
    subsets = get_subsets(unsettled_tiles)
    for size in range(2, len(unsettled_tiles)):
        for subset in subsets:
            if len(subset) != size:
                continue
            all_numbers = s.get_numbers(subset)
            if len(all_numbers) == size:
                # Group found!
                @log.rollback
                def rem():
                    log.indent()
                    log.append("Group {0} contains {1}", subset, all_numbers)
                    log.indent()
                    result = section_remove(s, util.difference(unsettled_tiles, subset), all_numbers)
                    log.dedent(2)
                    return result

                changed = max(changed, rem())
    if changed > 0:
        # New group(s) were found
        # We should do the whole _check_group thing again
        # instead of waiting for another run in check_group
        log.indent()
        changed = max(changed, _check_group(s, h))
        log.dedent()
        # Note that this is recursive,
        # so there should be no more new groups by now
    return changed


@solve_method(1)
def check_group(s):
    changed = 0
    for h in s.houses:
        changed = max(changed, _check_group(s, h))
    if changed == 1:
        raise Changed(1)
    elif changed == 2:
        raise Changed(0)


@log.rollback
def _check_intersect(s, h1, h2):
    # Example:
    # 123***ABC
    # ***4*****
    # DEF***GHI
    # In the left 3x3 block, one of DEF must be 4
    # Thus, in the 3rd row, GHI cannot be 4
    # Thus, we can know that one of ABC must be 4
    # (Note that this conclusion cannot be reached
    # if we only look at the first row or the right 3x3 block)
    #
    # When two houses intersect,
    # some numbers cannot at the same time be outside of the intersection
    # Thus they must be inside the intersection
    changed = 0
    log.append("In House {0} & {1}:", h1, h2)
    h1u = util.difference(h1, h2)  # h1 unique tiles
    h2u = util.difference(h2, h1)  # h2 unique tiles
    h1un = s.get_numbers(h1u)  # h1 unique numbers
    h2un = s.get_numbers(h2u)  # h2 unique numbers
    h1i = Sudoku.other(h1un)  # h1 intersect-only numbers
    h2i = Sudoku.other(h2un)  # h2 intersect-only numbers
    hi = util.union(h1i, h2i)  # intersect-only numbers
    if len(hi) > 0:
        @log.rollback
        def rem():
            log.indent()
            log.append("Intersection contains {0}", hi)
            log.indent()
            result = max(section_remove(s, h2u, h1i), section_remove(s, h1u, h2i))
            log.dedent(2)
            return result

        changed = rem()
    return changed


@solve_method(2)
def check_intersect(s):
    changed = 0
    for h1 in s.houses:
        for h2 in s.houses:
            if h1 != h2:
                changed = max(changed, _check_intersect(s, h1, h2))
    if changed == 1:
        raise Changed(1)
    elif changed == 2:
        raise Changed(0)


def solve_methods_call(s, index):
    for i in range(index, len(solve_methods)):
        solve_methods[i](s)


def solve(s):
    index = 0
    while True:
        try:
            solve_methods_call(s, index)
        except Changed as c:
            index = c.moveto
        else:
            return s.is_completed()


def main(s):
    writer.writeline("# Input")
    writer.writelines(s.pr_table())
    writer.writeline("")
    solved = solve(s)
    writer.pr = True
    writer.writeline("# Result ({0})", "successful" if solved else "unsuccessful")
    writer.writelines(s.pr_table())
    writer.writeline("")
    writer.pr = False
    writer.writeline("# Log")
    writer.writelines(log.l)


if __name__ == "__main__":
    from sys import argv

    if len(argv) <= 1:
        print("python solve.py $infile [$outfile]")
        print("$infile: input file under in\\")
        print("$outfile: output file under out\\, will be time by default")
    else:
        infile = os.path.join(IN, argv[1])
        with open(infile) as f:
            s = Sudoku([line for line in f.readlines()])
        import time

        outfile = os.path.join(OUT, argv[2] if len(argv) > 2 else time.strftime("%Y%m%d%H%M%S.txt"))
        if os.path.exists(outfile):
            os.remove(outfile)
        writer = Writer(outfile)
        main(s)
