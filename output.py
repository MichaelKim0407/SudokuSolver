class Writer:
    def __init__(self, save, pr=False, saveas=None):
        self.pr = pr
        self.save = save
        self.saveas = saveas

    def writeline(self, line, *args):
        if args:
            line = line.format(*args)
        if self.pr:
            print(line)
        with open(self.save, "a") as f:
            f.write(line + "\n")
        if self.saveas is not None:
            with open(self.saveas, "a") as f2:
                f2.write(line + "\n")

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)
