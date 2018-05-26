# -*- coding: utf-8 -*-
import re,os
import jieba.posseg as pseg
from functools import lru_cache
import pickle 

DATA_PATH = os.path.join(os.path.dirname(__file__),"data","dict.pkl")

@lru_cache(maxsize=None)
def load_data():
    print("load data")
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
        self.initialized = True

    def _initialize2(self):
        data = load_data()
        pos_emotion = data["pos_emotion"]
        pos_envalute = data["pos_envalute"]
        neg_emotion = data["neg_emotion"]
        neg_envalute = data["neg_envalute"]
        degrees = data["degrees"]
        negations = data["negations"]
        self._initialize(pos_emotion,pos_envalute,neg_emotion,neg_envalute,degrees,negations)

    def predict(self,news, debug=False):
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
            if (word in self.pos_emotion) or (word in self.pos_envalute):
                word_score += 1
                '''
                两种情况：
                1. 非常 不 好吃
                2. 不是 很 好吃
                需要极性反转
                '''
                if (index - 1 >= 0 and word_list[index - 1] in self.neg_degree) or (index - 2 >= 0 and word_list[index - 2] in self.neg_degree):
                    word_score = 0.25 * (word_score + (-1))
                debug and print("%s pos" % word)
            elif (word in self.neg_emotion) or (word in self.neg_envalute):
                word_score -= 1
                '''
                1. 不是 不好
                2. 不是 很 不好
                极性反转
                '''
                if (index - 1 >= 0 and word_list[index - 1] in self.neg_degree) or (index - 2 >= 0 and word_list[index - 2] in self.neg_degree):
                    word_score = 0.25 * (word_score + (-1))
                debug and print("%s neg" % word)
            # 判断程度词
            if index - 1 >= 0:
                # 赫夫曼二叉树，加权路径最小
                con = (index - 2 >= 0 and word_list[index - 2] in self.more_degree)
                if word_list[index - 1] in self.more_degree or con:
                    word_score = 0.25 * (word_score + 3)
                elif word_list[index - 1] in self.ish_degree or con:
                    word_score = 0.25 * (word_score + 2)
                elif word_list[index - 1] in self.very_degree or con:
                    word_score = 0.25 * (word_score + 4)
                elif word_list[index - 1] in self.least_degree or con:
                    word_score = 0.25 * (word_score + 1)
                elif word_list[index - 1] in self.most_degree or con:
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
 
def predict(x,debug=False):
    if  predict.classifier.initialized:
        return predict.classifier.predict(x,debug=debug)
    else:
        predict.classifier._initialize2()
        return predict.classifier.predict(x,debug=debug)

predict.classifier = Classifier()

if __name__ == "__main__":
    import sys
    if len(sys.argv) ==2:
        print(predict(sys.argv[1]))