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
            self.houses = [[], [], []]
            base1 = range(9)
            base2 = [x * 9 for x in range(9)]
            base3 = [0, 1, 2, 9, 10, 11, 18, 19, 20]
            for i in range(9):
                self.houses[0].append([9 * i + x for x in base1])
                self.houses[1].append([i + x for x in base2])
                self.houses[2].append([3 * base3[i] + x for x in base3])
        else:
            # TODO: Enable custom housing
            pass

    def __getitem__(self, index):
        return self.table[index]

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
        for gr in self.houses:
            gr_re = []
            for house in gr:
                h_re = "";
                for index in house:
                    h_re += "{0:>2d}, ".format(index)
                gr_re.append(h_re[:-2])
            result.append(gr_re)
        return result
                    

if __name__ == "__main__":
    lines = "123456789,456789123,789123456,234567891,5678?1234,891234567,345678912,678912345,912345678".split(",")
    s = Sudoku(lines)
    for row in s.pr_table():
        print(row)
    for gr in s.pr_houses():
        print("House group:")
        for house in gr:
            print(house)
