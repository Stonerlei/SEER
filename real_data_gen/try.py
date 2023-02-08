import os
import csv
import json

triples = json.load(open('./real_data_gen/triplets.json', 'r'))
for i in triples:
    print(i)
    print(triples[i])
    print()
