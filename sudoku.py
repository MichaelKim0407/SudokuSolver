import util

class Sudoku:
    def __init__(self, lines, houses=None):
        self.table = []
        for y in range(9):
            line = lines[y]
            for x in range(9):
                item = line[x]
                if item in "123456789":
                    self.table.append([int(item)])
                else:
                    self.table.append([1, 2, 3, 4, 5, 6, 7, 8, 9])

        self.housegroups = []
        if houses is None:
            self.houses = []
            base1 = range(9)
            base2 = [x * 9 for x in range(9)]
            base3 = [0, 1, 2, 9, 10, 11, 18, 19, 20]
            for i in range(9):
                self.houses.append([9 * i + x for x in base1])
                self.houses.append([i + x for x in base2])
                self.houses.append([3 * base3[i] + x for x in base3])
        else:
            # TODO: Enable custom housing
            pass

    def __getitem__(self, index):
        return self.table[index]

    def __setitem__(self, index, item):
        self.table[index] = item

    def pr_table(self):
        result = []
        for y in range(9):
            row = ""
            for x in range(9):
                item = self.table[y * 9 + x]
                if len(item) == 1:
                    row += str(item[0])
                else:
                    row += " "
            result.append(row)
        return result

    def pr_houses(self):
        result = []
        for house in self.houses:
            h_re = "";
            for index in house:
                h_re += "{0:>2d}, ".format(index)
            result.append(h_re[:-2])
        return result

    def is_completed(self):
        for item in self.table:
            if len(item) != 1:
                return False
        else:
            return True

    def get_numbers(self, tiles):
        result = []
        for t in tiles:
            result += self[t]
        return util.unique(result)

    def remove_numbers(self, index, numbers):
        l = len(self[index])
        self[index] = util.difference(self[index], numbers)
        return len(self[index]) < l

    @staticmethod
    def other(numbers):
        return util.difference(range(1, 10), numbers)

    def settled_tiles(self, house):
        return [i for i in house if len(self.table[i]) == 1]

    def unsettled_tiles(self, house):
        return [i for i in house if len(self.table[i]) != 1]
        
    def settled_numbers(self, house):
        # return get_numbers(self.settled_tiles(house))
        return [self.table[i][0] for i in house if len(self.table[i]) == 1]

    def unsettled_numbers(self, house):
        # return get_numbers(self.unsettled_tiles(house))
        return Sudoku.other(self.settled_numbers(house))

if __name__ == "__main__":
    from sys import argv
    if len(argv) <= 1:
        lines = "123456789,456789123,789123456,234567891,5678?1234,891234567,345678912,678912345,912345678".split(",")
    else:
        import os
        with open(os.path.join("in", argv[1])) as f:
            lines = f.readlines()
    s = Sudoku(lines)
    for row in s.pr_table():
        print(row)
    for house in s.pr_houses():
        print(house)
