class Writer:
    def __init__(self, save, pr=False, save_as=None):
        self.pr = pr
        self.save = save
        self.save_as = save_as

    def writeline(self, line, *args, **kwargs):
        if args or kwargs:
            line = line.format(*args, **kwargs)
        if self.pr:
            print(line)
        with open(self.save, "a") as f:
            f.write(line + "\n")
        if self.save_as is not None:
            with open(self.save_as, "a") as f2:
                f2.write(line + "\n")

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)
