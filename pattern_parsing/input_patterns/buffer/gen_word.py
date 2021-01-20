from sys import argv
import os.path

input_word = argv[1]

def create_file(word):
    file_name = f'{word}.txt'
    if os.path.exists(file_name):
        print(file_name, 'already exists')
        return
    
    with open(file_name,'a') as output_file:
        output_file.write('0000000')
        output_file.write('\n')
        for char in word:
            with open(f'alphabet/{char}.txt') as char_file:
                for l in char_file.readlines()[1:]:
                    output_file.write(l)
            output_file.write('\n')

create_file(input_word)
