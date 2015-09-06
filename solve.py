import os

PATH = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(PATH, "in")
OUT = os.path.join(PATH, "out")

import util
from sudoku import Sudoku

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
    return result

def _check_house(s, h):
    # Within a house, remove numbers already settled from unsettled tiled
    changed = section_remove(s, s.unsettled_tiles(h), s.settled_numbers(h)) == 2
    if changed:
        # New settled numbers added
        _check_house(s, h)
    return changed
                
@solve_method(0)
def check_house(s):
    changed = False
    for h in s.houses:
        changed = changed or _check_house(s, h)
    if changed:
        raise Changed(0)

def get_subsets(st):
    # Returns a list of all subsets
    result = [[]]
    for i in st:
        result += [s + [i] for s in result]
    return result

def _check_group(s, h):
    # Within a house, find groups for unsettled numbers
    # A group is N tiles where only N unsettled numbers can exist
    # Thus these N unsettled numbers cannot be on any other tile
    # For example, if there are three unsettled tiles in a house
    # [4, 7], [4, 7], [4, 6, 7]
    # Then the first two tiles make a group, and the third one can only be [6]
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
                changed = max(changed, section_remove(s, util.difference(unsettled_tiles, subset), all_numbers))
    if changed > 0:
        # New group(s) were found
        # We should do the whole _check_group thing again
        # instead of waiting for another run in check_group
        changed = max(changed, _check_group(s, h))
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

def _check_intersect(s, h1, h2):
    inter = util.intersect(h1, h2) # intersection
    h1u = util.difference(h1, h2) # h1 unique tiles
    h2u = util.difference(h2, h1) # h2 unique tiles
    h1un = s.get_numbers(h1u) # h1 unique numbers
    h2un = s.get_numbers(h2u) # h2 unique numbers
    h1i = Sudoku.other(h1un) # h1 intersect-only numbers
    h2i = Sudoku.other(h2un) # h2 intersect-only numbers
    changed = max(section_remove(s, h2u, h1i), section_remove(s, h1u, h2i))
    if changed > 0:
        changed = max(_check_intersect(s, h1, h2))
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

def main(infile, outfile):
    with open(infile) as f:
        s = Sudoku([line for line in f.readlines()])
    for row in s.pr_table():
        print(row)
    solved = solve(s)
    for row in s.pr_table():
        print(row)

if __name__ == "__main__":
    from sys import argv
    if len(argv) <= 1:
        print("README")
    else:
        import time
        infile = os.path.join(IN, argv[1])
        outfile = os.path.join(OUT, argv[2] if len(argv) > 2 else time.strftime("%Y%m%d%H%M%S.txt"))
        main(infile, outfile)
