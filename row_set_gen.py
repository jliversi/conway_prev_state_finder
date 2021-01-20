import json
import pickle
import os.path

# Step 1, pre-process all possible 3x3 grids, for each determine:
# 1. Whether the center cell is ON or OFF in next gen
# 2. All possible merge-able right neighbors (sorted by prev property)

# To do this, represent each 3x3 as a binary number btwn 0 and 511
# each digit represents whether a cell is full
# b876543210
# 8 5 2
# 7 4 1
# 6 3 0

# helper function, appropriately named (counts from right, starting at 0, b876543210)
def nth_bin_dig(num, n):
    return (num >> n) & 1

# Determine center cell of next gen (True for OFF, False for OFF)
def next_gen_center(num):
    # determine middle bit (currently OFF or OFF)
    mid_bit = nth_bin_dig(num, 4)
    # clever solution for finding num set bits in bin int (credit: Brian Kernighan)
    count = 0
    n = num
    while n:
        n = n & (n-1)
        count += 1
    # all of the rules of conway happen here
    if (mid_bit and count in [3,4]) or (not mid_bit and count == 3):
        return True
    else:
        return False

# Sort ints btwn 0 and 512 into those which leave on, or leave off
ON = []
OFF = []
for i in range(512):
    ON.append(i) if next_gen_center(i) else OFF.append(i)

# key insight here: representing 3x3s as binary integers means we can
    # determine potential right neighbors as ranges
def calc_right_neighbors(num):
    # right neighbors are easier because the bottom three bits are free
    # therefore can be represented as some range of length 8
    # to determine bottom bound:
        # bitwise AND with 63 to wipe top 3 bits, then bitshift 3
        # ex. ABCDEFGHI -> DEFGHI000
    neighbor_lower_bound = (num & 63) << 3
    return range(neighbor_lower_bound, neighbor_lower_bound + 8)


# Associate each 3x3 int with its possible ON and OFF right neighbors
NBR_DICT = dict()
for i in range(512):
    nbr_range = calc_right_neighbors(i)
    on_nbrs, off_nbrs = [], []
    for nbr in nbr_range:
        on_nbrs.append(nbr) if next_gen_center(nbr) else off_nbrs.append(nbr)
    NBR_DICT[i] = {'ON': tuple(on_nbrs), 'OFF': tuple(off_nbrs)}


def sqrs_to_rows(num_list):
    # first, determine the total number of bits needed
    total_bits = 3 * len(num_list) + 6
    row_len = total_bits // 3
    # build up each row, starting with first 2 cols of num_list[0]
    first = num_list[0]
    row1 = (2 * nth_bin_dig(first, 8)) + nth_bin_dig(first, 5)
    row2 = (2 * nth_bin_dig(first, 7)) + nth_bin_dig(first, 4)
    row3 = (2 * nth_bin_dig(first, 6)) + nth_bin_dig(first, 3)
    rows = [row3, row2, row1]
    # then add on additional digits
    for num in num_list:
        for i in range(3):
            rows[i] = (rows[i] << 1) + nth_bin_dig(num,i)

    # build final result
    result = rows[0]
    result += rows[1] << row_len
    result += rows[2] << (row_len * 2)
    return result


# everything so far comes together here
# takes a row pattern of ONs and OFFs (iterable of truthy/falsey)
# returns a list of possible 3xNs, as returned by `sqrs_to_rows`
# Strategy: recursively loop through possiblities, restricting search space
# in each step to neighbors of previous step (except first which is all ONs or OFFs)
def poss_row_patterns(row, cur_idx=0, prev_cells=[]):
    if cur_idx > 0:
        # determine next set and store in `next_cells`
        on_or_off = 'ON' if row[cur_idx] else 'OFF'
        next_cells = NBR_DICT[prev_cells[-1]][on_or_off]

        # base case, if on final cell, yield a each poss pattern from this chain
        if cur_idx == len(row) - 1:
            for next_cell in next_cells:
                yield sqrs_to_rows(prev_cells + [next_cell])
        # otherwise continue the chain
        else:
            for next_cell in next_cells:
                yield from poss_row_patterns(row, cur_idx + 1, prev_cells + [next_cell])
    else: 
        # if on first cell, start with all of OFF or all of ON
        next_cells = ON if row[0] else OFF
        for next_cell in next_cells:
            yield from poss_row_patterns(row, cur_idx + 1, [next_cell])


# Run it 
with open('i_o/input.json') as f:
    input_grid = json.load(f)


for i, row in enumerate(input_grid):
    row_name = ''.join([str(x) for x in row])
    print(f'Processing {row_name}')
    file_name = f'obj_files/{row_name}.obj'
    if os.path.isfile(file_name):
        print(f'File for {row_name} already exists')
        continue

    result = [x for x in poss_row_patterns(row)]
    # sort here by top n digts 
    row_len = len(row) + 2
    tops_dict = dict()
    for num in result:
        top = num >> row_len
        if top in tops_dict:
            tops_dict[top].append(num)
        else:
            tops_dict[top] = [num]

    print(f'Pickling {len(result)} possible patterns into {file_name}\n')
    with open(file_name, 'xb') as row_file:
        pickle.dump(tops_dict, row_file)