import os

__author__ = 'Michael'

file = os.path.abspath(__file__)

for f in os.listdir(os.path.dirname(file)):
    if os.path.isfile(f) and not f.endswith(".py"):
        os.remove(f)
