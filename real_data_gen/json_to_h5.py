import json
import tables as tb
import numpy as np
from tqdm import tqdm


class Particle(tb.IsDescription):
    length = tb.UInt32Col(shape=(), dflt=0, pos=0)
    pos = tb.UInt32Col(shape=(), dflt=0, pos=1)


def json_to_h5(type, fold, model):
    """
        this function converts json file to h5 file for phase 1 of model training.
        the logic stays the same for phase 2 as well with a few changes.
    """
    code_h5 = tb.open_file(f"./real_data_gen/fold{fold}/code_{type}.h5", mode="w")
    test_h5 = tb.open_file(f"./real_data_gen/fold{fold}/test_{type}.h5", mode="w")
    label_h5 = tb.open_file(f"./real_data_gen/fold{fold}/label_{type}.h5", mode="w")

    code_table = code_h5.create_table(code_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_e_array = code_h5.create_earray(code_h5.root, 'phrases', tb.Int64Atom(), (0,))



    test_table = test_h5.create_table(test_h5.root, 'indices', Particle, 'a table of indices and lengths')
    test_e_array = test_h5.create_earray(test_h5.root, 'phrases', tb.Int64Atom(), (0,))

    label_e_array = label_h5.create_earray(label_h5.root, 'labels', tb.Int8Atom(), (0,))

    if model == 'JointEmbedder':
        with open('./real_data_gen/vocab_real_data.json') as fr:
            vocab_code = json.load(fr)
            vocab_test = vocab_code
    else:
        with open('./real_data_gen/vocab_code.json') as fr:
            vocab_code = json.load(fr)

        with open('./real_data_gen/vocab_test.json') as fr:
            vocab_test = json.load(fr)

    if type == 'test':
        with open(f'./real_data_gen/triplets.json', "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)
    else:
        with open(f'./real_data_gen/fold{fold}/{type}{fold}.json', "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)

    codeitive_curr_pos = 0
    test_curr_pos = 0
    
    pbar = tqdm(tuples)
    c = 0
    # print(tuples)
    for _id in pbar:
        c += 1
        pbar.set_description('Processing {}'.format(c))
        code = tuples[_id]['C'].split()
        test_code = tuples[_id]['T'].split()
        label = tuples[_id]['label']

        particle = test_table.row
        particle['length'] = len(test_code)
        particle['pos'] = test_curr_pos
        particle.append()

        for token in test_code:
            token = token.strip().replace('\\', '')
            test_e_array.append(np.array([vocab_test[token]]))
        
        test_curr_pos += len(test_code)

        particle = code_table.row
        particle['length'] = len(code)
        particle['pos'] = codeitive_curr_pos
        particle.append()

        for token in code:
            token = token.strip().replace('\\', '')            
            code_e_array.append(np.array([vocab_code[token]]))
        
        codeitive_curr_pos += len(code)


        if label == 'P':
            label_e_array.append(np.array([1]))
        else:
            label_e_array.append(np.array([0]))
        
        code_table.flush()
        test_table.flush()

    code_table.close()
    test_table.close()

if __name__ == '__main__':
    json_to_h5('test', 0, 'JointEmbedder')