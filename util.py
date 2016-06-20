__author__ = 'Michael'


def unique(li):
    return list(set(li))


def union(l1, l2):
    return unique(l1 + l2)


def difference(l1, l2):
    return [i for i in l1 if i not in l2]
    # return list(set(l1).difference(l2))


def intersect(l1, l2):
    return [i for i in l1 if i in l2]
    # return list(set(l1).intersection(l2))
