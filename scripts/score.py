# -*- coding: utf-8 -*-

import os
import sys
import re
import jieba_fast
import jieba_fast.posseg as pseg
import json

aaa = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(aaa)
from bixin import Classifier,load_data,predict
# some codes adapt from https://github.com/godbmw/various-codes/blob/master/DictEmotionAlgorithm/Main.py

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

pos_envalute = neg_envalute = []
pos_emotion = []
c = []

most_degree = very_degree = more_degree = ish_degree = least_degree = []


negations = set(json.load(open(os.path.join(DATA_DIR, 'negations.json'))))

with open(os.path.join(DATA_DIR, "degrees.json")) as f:
    degrees = json.load(f)


with open(os.path.join(DATA_DIR, 'pos.txt')) as f:
    pos_emotion = set([x.strip() for x in f.readlines()])

with open(os.path.join(DATA_DIR, 'neg.txt')) as f:
    neg_emotion = set([x.strip() for x in f.readlines()])

# with open(os.path.join(DATA_DIR, 'pos_eva.txt')) as f:
#     pos_envalute = set([x.strip() for x in f.readlines()])

# with open(os.path.join(DATA_DIR, 'neg_eva.txt')) as f:
#     neg_envalute = set([x.strip() for x in f.readlines()])
# jieba_fast.enable_parallel(4)
places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")
jieba_fast.load_userdict(places)


with open(os.path.join(DATA_DIR, 'pos_sentence.txt')) as f1,\
        open(os.path.join(DATA_DIR, 'neg_sentence.txt')) as f2:
    s1 = set([x.strip() for x in f1.readlines()])
    s2 = set([x.strip() for x in f2.readlines()])
    pos_emotion.union(s1)
    neg_emotion.union(s2)
    pos_neg = pos_emotion.union(neg_emotion)
    # pos_neg_eva = pos_envalute.union(neg_envalute)
    jieba_fast.load_userdict(s1.union(s2).union(pos_neg))


if __name__ == "__main__":
    # classifier = Classifier(pos_emotion,pos_envalute,neg_emotion,neg_envalute,degrees,negations)
    if len(sys.argv) > 1:
        flag = predict(sys.argv[1], debug=True)
        print(flag)
    else:
        from os import walk

        DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")
        N = os.path.abspath(DIR)
        files = []
        for (dirpath, dirnames, filenames) in walk(N):
            files.extend([os.path.join(dirpath, x)
                          for x in filenames if x.endswith(".txt")])

        count = 0
        right = 0.0
        zero = 0.0
        for file in files:
            with open(file) as f:
                for line in f:
                    count += 1
                    sp = re.split('\t', line, maxsplit=1)
                    flag = sp[1].strip()
                    r = predict(sp[0])

                    if r == 0:
                        zero += 1
                        continue
                    if flag == "p" and r > 0:
                        right += 1
                    elif flag == "n" and r < 0:
                        right += 1
                    else:
                        print(sp[0])
                        print(flag, r)

        print("Total :%s" % count)

        print("Total Zero:%d ,percent:%f" % (zero, zero/count))

        count -= zero
        print("Total without Zero:%d ,percent:%f" % (count, zero/count))

        # 0.6248134726071201 0.629716 accuracy: 0.624813 accuracy: 0.612663 downwith evalute list 0.624813
        print("accuracy: %f" % (right/count))
        # print(load_data.cache_info())
