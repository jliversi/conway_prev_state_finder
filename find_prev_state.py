import pickle
import json
from datetime import datetime
# Now that we've found all possible patterns for any given row,
# we can take multiple rows and then just need to find a path through their possiblities

# Here we go!
# After each row has been processed by `row_set_gen.py`, we'll pass the 
# possibilties to `find_grid_pattern` along with the row_length of our input
# `find_grid_pattern` will recursively search for mergable path through 
# that list, eventually returning a new list of ints constituting the found pattern 
def find_grid_pattern(row_len,poss_per_row_list, current_posses=None, depth=0):
    # if on first level, options aren't filtered yet, so just grab options for top row
    if depth == 0:
        a = poss_per_row_list[0]
        current_posses = [poss for poss_key in a for poss in a[poss_key]]

    # if reached bottom level (!!!), let's hope possiblities are non-empty...
    # if so, just return first option
    if depth == len(poss_per_row_list) - 1:
        for el in current_posses:
            return [el]

    # iterate current options
    for top_poss in current_posses:
        # filter next set of possibilites:
        # possiblities are already sorted under their top x digits, 
        # so we only recurse with options that match our current top_poss's 
        # bottom x digits
        bottom_two_of_top_poss = top_poss & (2**(row_len * 2) - 1)
        if bottom_two_of_top_poss not in poss_per_row_list[depth + 1]: continue
        poss_next = poss_per_row_list[depth + 1][bottom_two_of_top_poss]
        
        # recurse with those possibilties
        subresult = find_grid_pattern(row_len,poss_per_row_list, poss_next, depth + 1)
        # if subresult is truthy, we found it! send it up!!!!
        if subresult:
            return [top_poss] + subresult
        # otherwise continue to next iteration of current_posses

    # if never found, return None for recursive results
    return None



# The hard work done, parse the result of `find_grid_pattern` into
# a 2D array of 1s and 0s, ready for JSONificiation
def format_results(grid_pattern, row_length):
    first = grid_pattern[0]
    # convert first row-integer into binary string for first 2 rows
    first_2_rows = format((first >> row_length), f'0{row_length * 2}b')
    # then turn them into arrays of 1s and 0s and begin result
    row1 = [int(char) for char in first_2_rows[:row_length]]
    row2 = [int(char) for char in first_2_rows[row_length:]]
    result = [row1, row2]
    # add rest of the third row of the rest of the results in grid_pattern
    for row_trio in grid_pattern:
        # for these we only care about the final {row_length} digits
        third_row = row_trio & (2**row_length - 1)
        row_str = format(third_row, f'0{row_length}b')
        result.append([int(char) for char in row_str])

    return result

# some helper methods for solve
def print_time(time):
    print(time.strftime("%H:%M:%S"))

def time_since(time):
    return (datetime.now() - time).seconds

# returns fetched rows and number of rows fetched
def fetch_row_possiblities(grid):
    all_poss_row_patterns = []
    fetched = {}
    for row in input_grid:
        row_name = ''.join([str(x) for x in row])
        if row_name in fetched:
            all_poss_row_patterns.append(fetched[row_name])
        else:
            file_name = f'obj_files/{row_name}.obj'
            with open(file_name,'rb') as row_file:
                row_posses = pickle.load(row_file) 
                fetched[row_name] = row_posses
                all_poss_row_patterns.append(row_posses)
    return (all_poss_row_patterns, len(fetched))

def print_solution(solution):
    for line in solution:
        print(''.join(['.' if x == 0 else '#' for x in line]))
    print('\n')

def save_results(results):
    with open('i_o/output.json','w') as json_f:
            json.dump(results,json_f)


# bring it all together, takes a 2D array (N x N) of desired pattern
# returns 2D array (N+2 x N+2) of prev state
def solve(input_grid):
    row_length = len(input_grid[0])
    start_time = datetime.now()
    print_time(start_time)

    print(f'Fetching partial solutions per row...')
    all_poss_row_patterns, num_rows = fetch_row_possiblities(input_grid)

    finish_fetch_time = datetime.now()
    print(num_rows,f'rows fetched after {time_since(start_time)} secs')

    print('Searching for full solution...')
    found_pattern = find_grid_pattern(row_length + 2, all_poss_row_patterns)

    print(f'Solution found after {time_since(finish_fetch_time)} secs')

    print('Formatting results...')
    formatted = format_results(found_pattern, row_length + 2)

    print('\nSolution:')
    print_solution(formatted)

    print('Storing solution in i_o/output.json...')
    save_results(formatted)

    end_time = datetime.now()
    print(f'Finished at {print_time(end_time)}')
    print(f'Total time, {time_since(start_time)} sec')


# MAKE IT HAPPEN

with open('i_o/input.json') as f:
    input_grid = json.load(f)


solve(input_grid)



# Display methods, for testing
def num_to_3x3_display(num):
    print(num)
    num = format(num, '09b')
    print(num)
    print(num[0],num[3],num[6])
    print(num[1],num[4],num[7])
    print(num[2],num[5],num[8])

def rows_int_to_display(num, row_len):
    print(num)
    num = format(num, f'0{row_len * 3}b')
    print(num)
    rows = ['','','']
    for i in range(row_len * 3):
        row_idx = i // row_len
        rows[row_idx] += num[i]
    for el in rows:
        print(el)