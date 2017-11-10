import numpy as np


class cell:
    def __init__(self, v, row, col):
        self.v = v
        self.row = row
        self.col = col
        self.block_row = None
        self.block_col = None
        self.block_square = None
        self.potential_v = set()


class block:
    def __init__(self, name, cells):
        self.name = name
        self.cells = cells
        for c in self.cells:
            if self.name.split('_')[0] == 'row':
                c.block_row = self
            elif self.name.split('_')[0] == 'col':
                c.block_col = self
            elif self.name.split('_')[0] == 'square':
                c.block_square = self


def solve(f_name='sample'):
    f = open(f_name + '.txt')

