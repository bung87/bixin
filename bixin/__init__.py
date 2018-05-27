# -*- coding: utf-8 -*-
import re,os
# import jieba_fast.posseg as pseg
import jieba_fast
# from functools import lru_cache
import math
import pickle 
from collections import Counter

DATA_PATH = os.path.join(os.path.dirname(__file__),"data","dict.pkl")

FIXED_PA = 0.25

# @lru_cache(maxsize=None)
def load_data():
    with open(DATA_PATH,"rb") as f:
        return pickle.load(f)

class Classifier():
    def __init__(self,*args):
        self.initialized = False
        if len(args):
            self._initialize(*args)
       
    def _initialize(self,pos_emotion,pos_envalute,neg_emotion,neg_envalute,degrees,negations):
        self.pos_emotion = pos_emotion
        self.pos_envalute = pos_envalute
        self.neg_emotion = neg_emotion
        self.neg_envalute = neg_envalute
        # self.negations = negations
        # self.degrees = degrees
        self.most_degree = set(degrees.get("1"))
        self.very_degree = set(degrees.get("2"))
        self.more_degree = set(degrees.get("3"))
        self.ish_degree = set(degrees.get("4"))
        self.least_degree = set(degrees.get("5"))
        self.neg_degree = set(degrees.get("6")).union(negations)
        
        # all_dgrees = self.most_degree\
        #     .union(self.very_degree)\
        #     .union(self.more_degree)\
        #     .union(self.ish_degree)\
        #     .union(self.least_degree)\
        #     .union(self.neg_degree)\

        pos_neg = self.pos_emotion.union(self.neg_emotion)
        # pos_neg_eva = pos_envalute.union(neg_envalute)
        jieba_fast.load_userdict(pos_neg)

        self.initialized = True

    def initialize(self):
        data = load_data()
        pos_emotion = data["pos_emotion"]
        pos_envalute = data["pos_envalute"]
        neg_emotion = data["neg_emotion"]
        neg_envalute = data["neg_envalute"]
        degrees = data["degrees"]
        negations = data["negations"]
        # places = data["places"]
        self._initialize(pos_emotion,pos_envalute,neg_emotion,neg_envalute,degrees,negations)

    def predict(self,news, debug=False):
        news = re.sub(
            '\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', news)
        news = re.sub("@[^\s]+", "", news)
        news = re.sub("“[^”]+”","",news) # remove quote
        # news = re.sub("【[^】]+】","",news) # remove quote
        news = re.sub("《[^》]+》","",news) # title
        news = re.sub("#[^#]+#","",news) # topic
        news = re.sub("分享自\s@[\w]+","",news) # speed up
        news = re.sub("转自[\w]+","",news) # speed up
        text_len = len(news)
        if not text_len:
            return 0
        word_list = [x  for x in jieba_fast.cut(news)if not re.match("\W", x)]
        if not word_list:
            return 0
        word_scored = set()
        counter = Counter(word_list)
        pos_dict = {'times': 0, 'score': 0, 'words': [], 'index': []}
        neg_dict = {'times': 0, 'score': 0, 'words': [], 'index': []}

        for index, word in enumerate(word_list):
            word_score = 0
            pre_word = index - 1 >= 0 and word_list[index - 1]
            next_word = index - 2 >= 0 and word_list[index - 2]
            base_score = .1 + math.log(1+counter[word])
            # 判断极性
            if (word in self.pos_emotion) or (word in self.pos_envalute):
                word_mark = "+" + word
                if word_mark in word_scored:
                    continue
                word_score += base_score
                '''
                两种情况：
                1. 非常 不 好吃
                2. 不是 很 好吃
                需要极性反转
                '''
                if (pre_word in self.neg_degree) or (next_word in self.neg_degree):
                    word_score = base_score * -1
                debug and print("%s pos" % word)
                word_scored.add(word_mark)
            elif (word in self.neg_emotion) or (word in self.neg_envalute):
                word_mark = "-" + word
                if word_mark in word_scored:
                    continue
                word_score -= base_score
                '''
                1. 不是 不好
                2. 不是 很 不好
                极性反转
                '''
                if (pre_word in self.neg_degree) or (next_word in self.neg_degree):
                    word_score = base_score * -1
                debug and print("%s neg" % word)
                word_scored.add(word_mark)
            # 判断程度词
            if index - 1 >= 0:
                # 赫夫曼二叉树，加权路径最小
                con = (next_word in self.more_degree)
                if pre_word in self.more_degree or con:
                    word_score = word_score  * (FIXED_PA + .3)
                elif pre_word in self.ish_degree or con:
                    word_score = word_score  * (FIXED_PA + .2)
                elif pre_word in self.very_degree or con:
                    word_score = word_score  * (FIXED_PA + .4)
                elif pre_word in self.least_degree or con:
                    word_score = word_score  * (FIXED_PA + .1)
                elif pre_word in self.most_degree or con:
                    word_score = word_score  * (FIXED_PA + .5)

            if word_score > 0:
                if debug:
                    pos_dict['words'].append(word)
                    pos_dict['index'].append(index)
                    pos_dict['times'] += 1
                pos_dict['score'] += word_score
            elif word_score < 0:
                if debug:
                    neg_dict['words'].append(word)
                    neg_dict['index'].append(index)
                    neg_dict['times'] += 1
                neg_dict['score'] += word_score
            

        debug and print(str(pos_dict)+"\n"+str(neg_dict))

        return pos_dict['score'] - abs(neg_dict['score'])
 
def predict(x,debug=False):
    if  predict.classifier.initialized:
        return predict.classifier.predict(x,debug=debug)
    else:
        predict.classifier.initialize()
        return predict.classifier.predict(x,debug=debug)

predict.classifier = Classifier()

if __name__ == "__main__":
    import sys
    if len(sys.argv) ==2:
        print(predict(sys.argv[1]))