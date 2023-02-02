import csv
import os
import json
import utils

def read_metadata(metadata):
    # split the string by '/'
    class_ids = []
    test_ids = []
    for ind in metadata:
        class_id = ind.split('/')[1]
        test_id = ind.split('/')[2]
        # remove '[', ']' and 'class:' in class_id
        class_id = class_id.split(':')[1][:-1]
        # remove '[', ']' and 'method:' in test_id
        test_id = test_id.split(':')[1][:-1]
        test_id = test_id.split('(')[0] + '('
        class_ids.append(class_id)
        test_ids.append(test_id)
    return class_ids, test_ids

def test_extract(student_id, class_id, test_id):
    """Extract the test from the data"""
    test = ''
    class_path = class_id.replace('.', '/') + '.java'
    f = open(f'{repo_path}/{student_id}/src/test/java/{class_path}', 'r')
    # extract the test code
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        if '{' in lines[i] and test_id in lines[i]:
            for j in range(i, len(lines)-1):
                if lines[j].strip().startswith('@Tag'):
                    break
                test += lines[j]
            test = test.strip().replace('\n', ' ')
            test = ' '.join(test.split())
            return test

def method_extract(student_id, test):
    """extract all the method code the test invokes"""
    method_set = json.load(open(f'./real_data_gen/method_set.json', 'r'))
    visited = []
    method = ''
    for token in test.split():
        if '(' not in token:
            continue
        token = token.split('(')[0].split('.')[-1]
        if token in method_set and token not in visited:
            visited.append(token)
            f = open(method_set[token], 'r')
            lines = f.readlines()
            f.close()
            for i in range(len(lines)):
                if utils.is_method_sig(lines[i]) and token in lines[i]:
                    method += lines[i]
                    for j in range(i+1, len(lines)-1):
                        if utils.is_method_sig(lines[j]):
                            break
                        method += lines[j]
                    # split method by the last '}'
                    method = method.rsplit('}', 1)[0] + '}'
                    break
    method = method.strip().replace('\n', ' ')
    method = ' '.join(method.split())
    return method


student_id = 'bkwak'
repo_path = './repositories'
methods = []
tests = []
labels = []
for filename in ['public-tests.tsv', 'hidden-tests.tsv']:
    f = open(f'{repo_path}/{student_id}/{filename}', 'r')
    reader = csv.reader(f, delimiter='\t')
    metadata = reader.__next__()
    class_ids, test_ids = read_metadata(metadata)
    labels += reader.__next__()
    f.close()

    for i in range(len(class_ids)):
        test = test_extract(student_id, class_ids[i], test_ids[i])
        tests.append(test)
        # print(class_ids[i])
        # print(test_ids[i])
        method = method_extract(student_id, test)
        # print(test)
        methods.append(method)

# construct triplets
triplets = []
for i in range(len(methods)):
    tripet = {}
    tripet[str(i)] = {}
    tripet[str(i)]['dataset'] = "COMP 3021"
    tripet[str(i)]['project'] = student_id
    tripet[str(i)]['bug_id'] = str(i)
    tripet[str(i)]['T'] = tests[i]
    tripet[str(i)]['C'] = methods[i]
    tripet[str(i)]['label'] = 'P' if labels[i] == 1 else 'F'
    triplets.append(tripet)
outputFile = f'./real_data_gen/triplets.json'
with open(outputFile, 'w') as f:
    json.dump(triplets, f, indent=4)
