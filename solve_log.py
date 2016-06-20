__author__ = 'Michael'


class Log(object):
    def __init__(self):
        self.l = []
        self.tabs = 0

    def append(self, line, *args, **kwargs):
        if args or kwargs:
            line = line.format(*args, **kwargs)
        self.l.append("\t" * self.tabs + line)

    def indent(self, i=1):
        self.tabs += i

    def dedent(self, i=1):
        self.tabs -= i

    def backup(self):
        result = Log()
        result.l = list(self.l)
        result.tabs = self.tabs
        return result

    def restore(self, backup):
        self.l = backup.l
        self.tabs = backup.tabs

    def rollback(self, func):
        def log_safe(*args):
            backup = self.backup()
            _changed = func(*args)
            if _changed == 0:
                self.restore(backup)
            return _changed

        return log_safe
