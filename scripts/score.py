# -*- coding: utf-8 -*-

import os
import sys
import re
import jieba
import json
# some codes adapt from https://github.com/godbmw/various-codes/blob/master/DictEmotionAlgorithm/Main.py

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

pos_envalute = neg_envalute = []
pos_emotion = []
c = []

most_degree = very_degree = more_degree = ish_degree = least_degree = []

neg_degree = []

negations = json.load(open(os.path.join(DATA_DIR, 'negations.json')))

with open(os.path.join(DATA_DIR, "degrees.json")) as f:
    d = json.load(f)
    most_degree = d.get("1")
    very_degree = d.get("2")
    more_degree = d.get("3")
    ish_degree = d.get("4")
    least_degree = d.get("5")
    neg_degree = d.get("6") + negations

# jieba.load_userdict(pos_emotion + pos_emotion)

with open(os.path.join(DATA_DIR, 'pos.txt')) as f:
    pos_emotion = [x.strip() for x in f.readlines()]

with open(os.path.join(DATA_DIR, 'neg.txt')) as f:
    neg_emotion = [x.strip() for x in f.readlines()]


def get_partial_score(news, debug=False):

    word_list = [x for x in jieba.cut(news) if not re.match("\W", x)]
    print(word_list)
    print('*' * 8)
    pos_dict = {'times': 0, 'score': 0, 'words': []}
    neg_dict = {'times': 0, 'score': 0, 'words': []}

    for index, word in enumerate(word_list):
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

        elif (word in neg_emotion) or (word in neg_envalute):
            word_score -= 1
            '''
            1. 不是 不好
            2. 不是 很 不好
            极性反转
            '''
            if (index - 1 >= 0 and word_list[index - 1] in neg_degree) or (index - 2 >= 0 and word_list[index - 2] in neg_degree):
                word_score = 0.25 * (word_score + (-1))
        # 判断程度词
        if index - 1 >= 0:
            # 赫夫曼二叉树，加权路径最小
            if word_list[index - 1] in more_degree or (index - 2 >= 0 and word_list[index - 2] in more_degree):
                word_score = 0.25 * (word_score + 3)
            elif word_list[index - 1] in ish_degree or (index - 2 >= 0 and word_list[index - 2] in more_degree):
                word_score = 0.25 * (word_score + 2)
            elif word_list[index - 1] in very_degree or (index - 2 >= 0 and word_list[index - 2] in more_degree):
                word_score = 0.25 * (word_score + 4)
            elif word_list[index - 1] in least_degree or (index - 2 >= 0 and word_list[index - 2] in more_degree):
                word_score = 0.25 * (word_score + 1)
            elif word_list[index - 1] in most_degree or (index - 2 >= 0 and word_list[index - 2] in more_degree):
                word_score = 0.25 * (word_score + 5)

        if word_score > 0:
            # print(word,index)
            debug and pos_dict['words'].append(word)
            pos_dict['times'] += 1
            pos_dict['score'] += word_score
        elif word_score < 0:
            debug and neg_dict['words'].append(word)
            neg_dict['times'] += 1
            neg_dict['score'] += word_score

    return (pos_dict, neg_dict)


if __name__ == "__main__":
    p, n = get_partial_score(sys.argv[1], debug=True)
    print(p, n)
