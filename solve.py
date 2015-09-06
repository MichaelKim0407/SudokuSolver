import os

PATH = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(PATH, "in")
OUT = os.path.join(PATH, "out")

log = []

def log_rollback(func):
    def log_safe(*args):
        global log
        backup = list(log)
        _changed = func(*args)
        if _changed == 0:
            log = backup
        return _changed
    return log_safe

def log_append(line, tabs):
    log.append("\t" * tabs + line)

class Writer:
    def __init__(self, outfile):
        self.out = outfile
        self.pr = False

    def writeline(self, line, *args):
        if args:
            line = line.format(*args)
        if self.pr:
            print(line)
        with open(self.out, "a") as f:
            f.write(line + "\n")

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

writer = None

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

def section_remove(s, sec, numbers, tabs):
    result = 0
    for i in sec:
        if s.remove_numbers(i, numbers):
            result = max(result, 1)
            if len(s[i]) == 1:
                result = 2
                log_append("Filled item[{0}] = {1}".format(i, s[i][0]), tabs)
            else:
                log_append("Reduced item[{0}] to {1}".format(i, s[i]), tabs)
    return result

@log_rollback
def _check_house(s, h, tabs=0):
    # Within a house, remove numbers already settled from unsettled tiled
    log_append("In House {0}:".format(h), tabs)
    changed = section_remove(s, s.unsettled_tiles(h), s.settled_numbers(h), tabs+1)
    if changed == 2:
        # New settled numbers added
        _check_house(s, h, tabs+1)
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

@log_rollback
def _check_group(s, h, tabs=0):
    # Within a house, find groups for unsettled numbers
    # A group is N tiles where only N unsettled numbers can exist
    # Thus these N unsettled numbers cannot be on any other tile
    # For example, if there are three unsettled tiles in a house
    # [4, 7], [4, 7], [4, 6, 7]
    # Then the first two tiles make a group, and the third one can only be [6]
    log_append("In House {0}:".format(h), tabs)
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
                @log_rollback
                def rem():
                    log_append("Group {0} contains {1}".format(subset, all_numbers), tabs+1)
                    return section_remove(s, util.difference(unsettled_tiles, subset), all_numbers, tabs+2)
                changed = max(changed, rem())
    if changed > 0:
        # New group(s) were found
        # We should do the whole _check_group thing again
        # instead of waiting for another run in check_group
        changed = max(changed, _check_group(s, h), tabs+1)
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

@log_rollback
def _check_intersect(s, h1, h2, tabs=0):
    changed = 0
    log_append("In House {0} & {1}:".format(h1, h2), tabs)
    inter = util.intersect(h1, h2) # intersection
    h1u = util.difference(h1, h2) # h1 unique tiles
    h2u = util.difference(h2, h1) # h2 unique tiles
    h1un = s.get_numbers(h1u) # h1 unique numbers
    h2un = s.get_numbers(h2u) # h2 unique numbers
    h1i = Sudoku.other(h1un) # h1 intersect-only numbers
    h2i = Sudoku.other(h2un) # h2 intersect-only numbers
    hi = util.union(h1i, h2i) # intersect-only numbers
    if len(hi) > 0:
        @log_rollback
        def rem():
            log_append("Intersection contains {0}".format(hi), tabs+1)
            return max(section_remove(s, h2u, h1i, tabs+2), section_remove(s, h1u, h2i, tabs+2))
        changed = rem()
#   if changed > 0:
#       changed = max(_check_intersect(s, h1, h2, tabs+1))
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
    writer.writelines(log)

if __name__ == "__main__":
    from sys import argv
    if len(argv) <= 1:
        print("README")
    else:
        infile = os.path.join(IN, argv[1])
        with open(infile) as f:
            s = Sudoku([line for line in f.readlines()])
        import time
        outfile = os.path.join(OUT, argv[2] if len(argv) > 2 else time.strftime("%Y%m%d%H%M%S.txt"))
        writer = Writer(outfile)
        main(s)
