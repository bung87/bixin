# -*- coding: utf-8 -*-

import os
import sys
import re
import jieba
import jieba.posseg as pseg
import json
# some codes adapt from https://github.com/godbmw/various-codes/blob/master/DictEmotionAlgorithm/Main.py

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

pos_envalute = neg_envalute = []
pos_emotion = []
c = []

most_degree = very_degree = more_degree = ish_degree = least_degree = []

neg_degree = []

negations = set(json.load(open(os.path.join(DATA_DIR, 'negations.json'))))

with open(os.path.join(DATA_DIR, "degrees.json")) as f:
    d = json.load(f)
    most_degree = set(d.get("1"))
    very_degree = set(d.get("2"))
    more_degree = set(d.get("3"))
    ish_degree = set(d.get("4"))
    least_degree = set(d.get("5"))
    neg_degree = set(d.get("6")).union(negations)


with open(os.path.join(DATA_DIR, 'pos.txt')) as f:
    pos_emotion = set([x.strip() for x in f.readlines()])

with open(os.path.join(DATA_DIR, 'neg.txt')) as f:
    neg_emotion = set([x.strip() for x in f.readlines()])

# with open(os.path.join(DATA_DIR, 'pos_eva.txt')) as f:
#     pos_envalute = set([x.strip() for x in f.readlines()])

# with open(os.path.join(DATA_DIR, 'neg_eva.txt')) as f:
#     neg_envalute = set([x.strip() for x in f.readlines()])
# jieba.enable_parallel(4)
places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")
jieba.load_userdict(places)


with open(os.path.join(DATA_DIR, 'pos_sentence.txt')) as f1,\
        open(os.path.join(DATA_DIR, 'neg_sentence.txt')) as f2:
    s1 = set([x.strip() for x in f1.readlines()])
    s2 = set([x.strip() for x in f2.readlines()])
    pos_emotion.union(s1)
    neg_emotion.union(s2)
    pos_neg = pos_emotion.union(neg_emotion)
    # pos_neg_eva = pos_envalute.union(neg_envalute)
    jieba.load_userdict(s1.union(s2).union(pos_neg))


def get_partial_score(news, debug=False):
    news = re.sub(
        r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', news)
    news = re.sub("@[^\s]+", "", news)
    text_len = len(news)
    if not text_len:
        return 0
    word_list = [(x, y) for x, y in pseg.cut(news)if not re.match("\W", x)]

    word_scored = set()
    # print(word_list)
    pos_dict = {'times': 0, 'score': 0, 'words': [], 'index': []}
    neg_dict = {'times': 0, 'score': 0, 'words': [], 'index': []}

    for index, t in enumerate(word_list):
        word, tag = t
        if len(word) > 1 and tag == "n" and word in word_scored:
            continue
        word_score = 0
        # 判断极性
        if (word in pos_emotion) or (word in pos_envalute):
            word_score += 1
            '''
            两种情况：
            1. 非常 不 好吃
            2. 不是 很 好吃
            需要极性反转
            '''
            if (index - 1 >= 0 and word_list[index - 1] in neg_degree) or (index - 2 >= 0 and word_list[index - 2] in neg_degree):
                word_score = 0.25 * (word_score + (-1))
            debug and print("%s pos" % word)
        elif (word in neg_emotion) or (word in neg_envalute):
            word_score -= 1
            '''
            1. 不是 不好
            2. 不是 很 不好
            极性反转
            '''
            if (index - 1 >= 0 and word_list[index - 1] in neg_degree) or (index - 2 >= 0 and word_list[index - 2] in neg_degree):
                word_score = 0.25 * (word_score + (-1))
            debug and print("%s neg" % word)
        # 判断程度词
        if index - 1 >= 0:
            # 赫夫曼二叉树，加权路径最小
            con = (index - 2 >= 0 and word_list[index - 2] in more_degree)
            if word_list[index - 1] in more_degree or con:
                word_score = 0.25 * (word_score + 3)
            elif word_list[index - 1] in ish_degree or con:
                word_score = 0.25 * (word_score + 2)
            elif word_list[index - 1] in very_degree or con:
                word_score = 0.25 * (word_score + 4)
            elif word_list[index - 1] in least_degree or con:
                word_score = 0.25 * (word_score + 1)
            elif word_list[index - 1] in most_degree or con:
                word_score = 0.25 * (word_score + 5)

        if word_score > 0:
            debug and pos_dict['words'].append(word)
            pos_dict['index'].append(index)
            pos_dict['times'] += 1
            pos_dict['score'] += word_score
        elif word_score < 0:
            debug and neg_dict['words'].append(word)
            neg_dict['index'].append(index)
            neg_dict['times'] += 1
            neg_dict['score'] += word_score
        word_scored.add(word)

    debug and print(str(pos_dict)+"\n"+str(neg_dict))

    pos_len = pos_dict['index']
    neg_len = neg_dict['index']
    pos_max = max(pos_dict['index']) if pos_len else 0
    neg_max = max(neg_dict['index']) if neg_len else 0

    pos_min = min(pos_dict['index']) if pos_len else 0
    neg_min = min(neg_dict['index']) if neg_len else 0

    pos_range = pos_max - pos_min
    neg_range = neg_max - neg_min

    pos_per = pos_range/text_len
    neg_per = neg_range/text_len

    wei = abs(pos_per-neg_per) / text_len
    pos_wei = wei if pos_max > neg_max and pos_per > 0.1 else 0
    neg_wei = wei if neg_max > pos_max and neg_per > 0.1 else 0

    return pos_dict['score']*pos_per + pos_wei - (abs(neg_dict['score']*neg_per) + neg_wei)
    # return (pos_dict, neg_dict)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        flag = get_partial_score(sys.argv[1], debug=True)
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
                    r = get_partial_score(sp[0])

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
