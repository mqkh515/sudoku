import numpy as np
import itertools
from collections import defaultdict

v_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}


class Cell:
    def __init__(self, v, row, col):
        self.row = row
        self.col = col
        self.name = str(row) + str(col)
        self.block_row = None
        self.block_col = None
        self.block_square = None
        self.potential_v = set() if v == 0 else {v}  # all the values this cell can take given current fixed cells

    def get_val(self):
        if self.is_fixed():
            return list(self.potential_v)[0]
        else:
            raise Exception('requesting value of a non-fixed cell')

    def is_fixed(self):
        return len(self.potential_v) == 1

    def update(self):
        """remove all fixed values in all blocks it belongs to"""
        if self.is_fixed():
            return
        existing_val = set()
        for b in (self.block_row, self.block_col, self.block_square):
            for c in b.cells:
                if c.is_fixed():
                    existing_val.add(c.get_val())
        self.potential_v = v_set - existing_val


class Block:
    """any collection of 9 cells which should takes values 1-9 by rule. 
       i.e. a row, a col or a square by specific position"""
    def __init__(self, name, cells):
        self.name = name
        self.cells = cells
        self.cell_names = set([c.name for c in self.cells])
        self.potential_pos = {}  # for each one of 1 - 9, which positions it can take in the block
        # update each cell's block
        for c in self.cells:
            if self.name.split('_')[0] == 'row':
                c.block_row = self
            elif self.name.split('_')[0] == 'col':
                c.block_col = self
            elif self.name.split('_')[0] == 'square':
                c.block_square = self
            else:
                raise Exception('unexpected block name')

    def update(self):
        """re-structure cell-potential-val-set to potential val-pos map"""
        for c in self.cells:
            for v in c.potential_v:
                if v not in self.potential_pos:
                    self.potential_pos[v] = {c.name}
                else:
                    self.potential_pos[v].add(c.name)


class TrialStatus:
    def __init__(self, start_point, tar_cell):
        """start_point: in Problem.get_status_str() format.
           tar_cell: a '%d%d' % (row_idx, col_idx) str."""
        self.start_point = start_point
        self.tar_cell = tar_cell
        # get potential values of tar_cell at start_point
        row_idx = int(tar_cell[0]) - 1
        row = start_point.split('\n')[row_idx]
        col_idx = int(tar_cell[1]) - 1
        cell = row.split(',')[col_idx].strip()
        self.tar_cell_potential_vals = set([int(v) for v in cell])
        self.tar_cell_val = None
        self.tar_cell_tried_vals = set()
        self.try_next_val()  # setup a trial value upon construction

    def try_next_val(self):
        available_vals = [v for v in self.tar_cell_potential_vals if v not in self.tar_cell_tried_vals]
        if not available_vals:
            return 'exhausted'
        self.tar_cell_val = available_vals[0]
        self.tar_cell_tried_vals.add(available_vals[0])
        print('trying: cell_%s: %d out of {%s}' % (self.tar_cell, self.tar_cell_val, ''.join(sorted([str(v) for v in self.tar_cell_potential_vals]))))
        return 'success'


class Problem:
    def __init__(self, f_name='sample'):
        self.f_name = f_name
        f = open('problems/' + f_name + '.txt')
        lines = f.read()
        f.close()
        self.status = 'run'  # run / trial / solved / dead_end; dead_end is a sub-status of trail
        self.trail_status = []  # a list of TrialStatus object

        # 81 cells
        self.cells = {}
        for r_idx, row in enumerate(lines.split('\n')):
            for c_idx, v in enumerate(row):
                # 0 value meaning empty cell
                cell_name = '%d%d' % (r_idx + 1, c_idx + 1)
                self.cells[cell_name] = Cell(int(v), r_idx + 1, c_idx + 1)
        # 27 blocks
        self.blocks = []
        for idx in range(9):
            self.blocks.append(Block('col_%d' % (idx + 1), [self.cells['%d%d' % (i, idx + 1)] for i in range(1, 10)]))
            self.blocks.append(Block('row_%d' % (idx + 1), [self.cells['%d%d' % (idx + 1, i)] for i in range(1, 10)]))
        for start_pos in ('11', '14', '17', '41', '44', '47', '71', '74', '77'):
            pos_row = int(start_pos[0])
            pos_col = int(start_pos[1])
            square_block_cell_list = []
            for i in range(3):
                for j in range(3):
                    square_block_cell_list.append(self.cells['%d%d' % (pos_row + i, pos_col + j)])
            self.blocks.append(Block('square_%s' % start_pos, square_block_cell_list))
        self.assert_no_conflict()

        # init cell potentials
        for c in self.cells.values():
            c.update()

    def __str__(self):
        return self.get_status_str()

    def apply_trial_status(self, trial_status):
        self.recover_from_status_str(trial_status.start_point)
        self.cells[trial_status.tar_cell].potential_v = {trial_status.tar_cell_val}

    def get_trial_tar_cell(self):
        # find the cell with least number of potential values to start a trial
        potential_n_vals = {}
        for c in self.cells.values():
            n_val = len(c.potential_v)
            if n_val == 1:
                continue
            if n_val not in potential_n_vals:
                potential_n_vals[n_val] = [c.name]
            else:
                potential_n_vals[n_val].append(c.name)
        min_n_val = np.min(list(potential_n_vals.keys()))
        # randomly pick one
        return potential_n_vals[min_n_val][0]

    def get_status_str(self):
        """get unique string of current status, also print-friendly"""
        s_list = []
        for row_idx in range(1, 10):
            row_s_list = []
            for col_idx in range(1, 10):
                c_str = ''.join(sorted([str(v) for v in self.cells['%d%d' % (row_idx, col_idx)].potential_v]))
                row_s_list.append('%9s' % c_str)
            s_list.append(','.join(row_s_list))
        return '\n'.join(s_list)

    def recover_from_status_str(self, status_str):
        for row_idx, row_str in enumerate(status_str.split('\n')):
            for col_idx, cell_str in enumerate(row_str.split(',')):
                cell_str = cell_str.strip()
                self.cells['%d%d' % (row_idx + 1, col_idx + 1)].potential_v = set([int(v) for v in cell_str])

    def assert_no_empty_potential(self):
        """no cell should have empty potential value;
           no block should have a value with empty potential pos"""
        empty_cell = []
        for c in self.cells.values():
            if not c.potential_v:
                empty_cell.append(c.name)
        empty_pos = []
        for b in self.blocks:
            for v in v_set:
                if not b.potential_pos[v]:
                    empty_pos.append('%s-%d' % (b.name, v))

        if empty_cell:
            print('empty_cell_list: %s', ','.join(empty_cell))
        if empty_pos:
            print('empty_pos_list: %s', ','.join(empty_pos))
        if empty_cell or empty_pos:
            if self.status == 'run':
                raise Exception('empty cell / pos in regular run')
            else:
                self.status = 'dead_end'

    def assert_no_conflict(self):
        """for each block, cells with only one potential should have no duplicated value"""
        conflict_blocks = []
        for b in self.blocks:
            val_count = defaultdict(int)
            for c in b.cells:
                if c.is_fixed():
                    val_count[c.get_val()] += 1
            max_val = max(list(val_count.values()))
            if max_val > 1:
                conflict_blocks.append(b.name)
        if conflict_blocks:
            print(self.get_status_str())
            print("conflict blocks: %s" % ', '.join(conflict_blocks))
            raise Exception('conflict blocks')

    def assert_solved(self):
        return np.all([c.is_fixed() for c in self.cells.values()])

    def update_one_iter(self):
        """update for one iteration:
           1, update cells.
           2, update blocks.
           3, cross reference cells and blocks.
        """
        for c in self.cells.values():
            c.update()
        for b in self.blocks:
            b.update()
        # for a given block, if a potential value takes more than one potential position
        # and these positions all belong to some other block,
        # we can update the other positions of this other block.
        for b in self.blocks:
            for v, pos in b.potential_pos.items():
                if len(pos) > 1:
                    for b_other in self.blocks:
                        if b_other.name == b.name:
                            continue
                        if np.all([p in b_other.cell_names for p in pos]):
                            for c in b_other.cells:
                                if c.name not in pos and v in c.potential_v:
                                    c.potential_v.remove(v)
        # for a given block,
        # if any group of cells takes the same potential values, and number of potential_v equals number of cells,
        # we can remove these values from all other cells of this block
        # let's only try n up to 3
        self.check_block_exclusive_combination(2)
        self.check_block_exclusive_combination(3)
        self.assert_no_empty_potential()
        self.assert_no_conflict()

    def check_block_exclusive_combination(self, n_size):
        for b in self.blocks:
            tar_cell_groups = []
            candidate_cells = [c for c in b.cells if len(c.potential_v) == n_size]
            for c_group in itertools.combinations(candidate_cells, n_size):
                all_same = True
                ref_c = c_group[0]
                for c in c_group[1:]:
                    if sorted(list(c.potential_v)) != sorted(list(ref_c.potential_v)):
                        all_same = False
                        break
                if all_same:
                    tar_cell_groups.append(c_group)
            for c_group in tar_cell_groups:
                tar_cell_name_set = set([c.name for c in c_group])
                tar_cell_val_set = c_group[0].potential_v
                for c in b.cells:
                    if c.is_fixed() or c.name in tar_cell_name_set:
                        continue
                    c.potential_v -= tar_cell_val_set

    def update(self):
        self.update_one_iter()
        if self.status == 'dead_end':
            return
        status_changed = True
        n_iter = 0
        while status_changed:
            start_status = self.get_status_str()
            self.update_one_iter()
            if self.status == 'dead_end':
                return
            end_status = self.get_status_str()
            status_changed = start_status != end_status
            n_iter += 1
            if n_iter % 5 == 0:
                print('%d iter taken;' % n_iter)
        print('no more status update after %d simple iter' % (n_iter - 1))

    def solve(self):
        self.update()
        # if not finished in one update, trial started
        self.status = 'trial'
        while not self.assert_solved():
            if self.status == 'dead_end':
                # try next value with last trial status
                next_val_status = self.trail_status[-1].try_next_val()
                if next_val_status != 'success':
                    # exhausted, now last trial can be removed
                    self.trail_status.pop()
                    if not self.trail_status:
                        # all trial failed, not expected to happen
                        raise Exception('no trial succeed, no solution for the game')
                    # try next value with the second to the last trial status
                    continue
                else:
                    # got next trial value, good to go with update
                    pass
            else:
                # need to add new trail status
                self.trail_status.append(TrialStatus(self.get_status_str(), self.get_trial_tar_cell()))  # next value already init
                print('trial status depth: %d' % (len(self.trail_status)))

            self.status = 'trial'  # change dead_end to trial again
            self.apply_trial_status(self.trail_status[-1])
            self.update()

        # solved
        self.assert_no_conflict()
        self.status = 'solved'
        print('problem solved!')
        status_str = self.get_status_str()
        print(status_str)
        f = open('problems/' + self.f_name + '_out.txt', 'w')
        f.write(status_str)
        f.close()




