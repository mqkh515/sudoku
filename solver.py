import numpy as np

v_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}

class Cell:
    def __init__(self, v, row, col):
        self.v = v
        self.row = row
        self.col = col
        self.name = str(row) + str(col)
        self.block_row = None
        self.block_col = None
        self.block_square = None
        self.potential_v = set()  # all the values this cell can take given current fixed cells

    def update(self):
        pass


class Block:
    def __init__(self, name, cells):
        self.name = name
        self.cells = cells
        # for each one of 1 - 9, which positions it can take in the block
        self.potential_v = {}
        for i in range(1, 10):
            self.potential_v[i] = set()
        # update each cell's block
        for c in self.cells:
            if self.name.split('_')[0] == 'row':
                c.block_row = self
            elif self.name.split('_')[0] == 'col':
                c.block_col = self
            elif self.name.split('_')[0] == 'square':
                c.block_square = self
        # for cell with given value, update block's potential v
        for c in self.cells:
            if c.v != 0:
                self.potential_v[c.v] = {c.name}

    def update(self):
        pass


class Problem:
    def __init__(self, f_name='sample'):
        f = open(f_name + '.txt')
        lines = f.read()
        f.close()
        # 81 cells
        self.cells = np.empty((9, 9)).astype(np.object)
        for r_idx, l in enumerate(lines.split('\n')):
            for c_idx, v in enumerate(l):
                self.cells[r_idx, c_idx] = Cell(int(v), r_idx + 1, c_idx + 1)
        # 27 blocks
        self.blocks = []
        for idx in range(9):
            self.blocks.append(Block('col_%d' % (idx + 1), list(self.cells[:, idx])))
            self.blocks.append(Block('row_%d' % (idx + 1), list(self.cells[idx, :])))
        for start_pos in ('11', '14', '17', '41', '44', '47', '71', '74', '77'):
            pos_row = int(start_pos[0]) - 1
            pos_col = int(start_pos[1]) - 1
            square_block_cell_list = []
            for i in range(3):
                for j in range(3):
                    square_block_cell_list.append(self.cells[pos_row + i, pos_col + j])
            self.blocks.append(Block('square_%s' % start_pos, square_block_cell_list))
        # update all potential vs


    def print(self):
        for b in self.blocks:
            block_s = b.name + ': '
            cell_info = []
            for c in b.cells:
                cell_info.append('%s-%d' % (c.name, c.v))
            print(block_s + ', '.join(cell_info))

    def update(self):
        pass

    def solver(self):
        pass



