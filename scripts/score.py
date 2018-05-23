# -*- coding: utf-8 -*-

import os
import jieba
# some codes adapt from https://github.com/godbmw/various-codes/blob/master/DictEmotionAlgorithm/Main.py

DATA_DIR = os.path.join(os.path.dirname(__file__),"..","data")

pos_envalute = neg_envalute = []
pos_emotion = []
c = []

most_degree = very_degree = more_degree = ish_degree = least_degree = []

neg_degree = []

negations = []

jieba.load_userdict(pos_emotion + pos_emotion)

with open(os.path.join(DATA_DIR,'pos.txt')) as f:
    pos_emotion = [x.strip() for x in f.readlines()]
    
with open(os.path.join(DATA_DIR,'neg.txt')) as f:
    neg_emotion = [x.strip() for x in f.readlines()]

def get_partial_score(news,weight=1):

    word_list = list(jieba.cut(news))

    pos_dict = {'times':0,'score':0}
    neg_dict = {'times':0,'score':0}

    for (index,word) in enumerate(word_list):
        word_score = 0
        #判断极性
        if (word in pos_emotion) or (word in pos_envalute):
            word_score+=weight
            '''
            两种情况：
            1. 非常 不 好吃
            2. 不是 很 好吃
            需要极性反转
            '''
            if (index-1>=0 and word_list[index-1] in neg_degree) or ( index-2>=0 and word_list[index-2] in negations ):
                word_score = word_score*(-1)

        elif (word in neg_emotion) or (word in neg_envalute):
            word_score-=1
            '''
            1. 不是 不好
            2. 不是 很 不好
            极性反转
            '''
            if (index-1>=0 and word_list[index-1] in neg_degree) or ( index-2>=0 and word_list[index-2] in negations ):
                word_score = word_score*(-1)
        #判断程度词
        if index-1>=0:
            #赫夫曼二叉树，加权路径最小
            if word_list[index-1] in more_degree or (index-2>=0 and word_list[index-2] in more_degree):
                    word_score = word_score*2
            elif word_list[index-1] in ish_degree or (index-2>=0 and word_list[index-2] in more_degree):
                    word_score = word_score*1.5
            elif word_list[index-1] in very_degree or (index-2>=0 and word_list[index-2] in more_degree):
                    word_score = word_score*2.5
            elif word_list[index-1] in least_degree or (index-2>=0 and word_list[index-2] in more_degree):
                    word_score = word_score*1.1
            elif word_list[index-1] in most_degree or (index-2>=0 and word_list[index-2] in more_degree):
                    word_score = word_score*3

        if word_score>0:
            #print(word,index)
            pos_dict['times']+=1
            pos_dict['score']+=word_score
        elif word_score<0:
            neg_dict['times'] += 1
            neg_dict['score'] += word_score
        
    return (pos_dict, neg_dict)