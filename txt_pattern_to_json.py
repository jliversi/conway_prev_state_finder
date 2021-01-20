import json
from sys import argv

if len(argv) == 1:
    print("No pattern filename provided")
    quit()

pattern_file = f'pattern_parsing/input_patterns/{argv[1]}'
with open(pattern_file) as f:
    input_pattern = [line.replace('\n','') for line in f]

arr = []

for l in input_pattern:
    l_arr = []
    for char in l:
        l_arr.append(int(char))
    arr.append(l_arr)

# remove extension
output_filename = argv[1].split('/')[-1].split('.')[0]
output_path = f'pattern_parsing/output_patterns/{output_filename}.json'
open(output_path,'x')

with open(output_path,'w') as json_f:
    json.dump(arr,json_f)