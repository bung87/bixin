# -*- coding: utf-8 -*-
import re
import os
import math
import pickle
from collections import Counter
from jieba_fast import Tokenizer
import tempfile

big_dict = os.path.join(os.path.dirname(__file__), "data","dict.txt.big")
tokenizer = Tokenizer(big_dict)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "dict.pkl")

FIXED_PA = 1.6

def load_data():
    with open(DATA_PATH, "rb") as f:
        return pickle.load(f)

class Classifier():
    def __init__(self, *args,**argv):
        self.initialized = False
        if len(args):
            self.initialize(*args,**argv)

    def _initialize(self, pos_emotion, pos_evaluation, neg_emotion, neg_evaluation, degrees, negations):
        self.pos_emotion = pos_emotion
        self.neg_emotion = neg_emotion
        pos_neg_eva = set()
        if self.include_evalution_dict:
            self.pos_evaluation = pos_evaluation
            self.neg_evaluation = neg_evaluation
            pos_neg_eva = pos_evaluation.union(neg_evaluation)
        else:
            self.pos_evaluation = self.pos_emotion
            self.neg_evaluation = self.neg_emotion

        self.most_degree = set(degrees.get("1"))
        self.very_degree = set(degrees.get("2"))
        self.more_degree = set(degrees.get("3"))
        self.ish_degree = set(degrees.get("4"))
        self.least_degree = set(degrees.get("5"))
        self.neg_degree = set(degrees.get("6")).union(negations)

        self.all_degrees = self.most_degree\
            .union(self.very_degree)\
            .union(self.more_degree)\
            .union(self.ish_degree)\
            .union(self.least_degree)

        pos_neg = self.pos_emotion.union(self.neg_emotion)
        with tempfile.NamedTemporaryFile(suffix=".txt",mode="w",encoding="utf-8") as f:
            f.write("\n".join(pos_neg.union(pos_neg_eva)))
            tokenizer.load_userdict(f.name)

        self.initialized = True

    def initialize(self,include_evalution_dict=False,include_tc=False):
        self.include_evalution_dict = include_evalution_dict
        data = load_data()
        pos_emotion = data["pos_emotion"].union(data["pos_sentence"])
        pos_evaluation = data["pos_evaluation"]
        neg_emotion = data["neg_emotion"].union(data["neg_sentence"])
        if include_tc:
            pos_emotion = pos_emotion.union(data["pos_emotion_tc"])
            neg_emotion = neg_emotion.union(data["neg_emotion_tc"])
        neg_evaluation = data["neg_evaluation"]
        degrees = data["degrees"]
        negations = data["negations"]
        # places = data["places"]
        self._initialize(pos_emotion, pos_evaluation, neg_emotion,
                         neg_evaluation, degrees, negations)

    def predict(self, news, debug=False):
        news = re.sub(
            '\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', news)
        news = re.sub("@[^\s]+", "", news)
        news = re.sub("“[^”]+”", "", news)  # remove quote
        # news = re.sub("【[^】]+】","",news) # remove quote
        news = re.sub("《[^》]+》", "", news)  # title
        news = re.sub("#[^#]+#", "", news)  # topic
        news = re.sub("分享自\s@[\w]+", "", news)  # speed up
        news = re.sub("转自[\w]+", "", news)  # speed up
        text_len = len(news)
        if not text_len:
            return 0
        word_list = list(filter(lambda x: re.match("\w", x),
                                tokenizer.cut(news)))
        if not word_list:
            return 0
        word_scored = set()
        counter = Counter(word_list)
        pos_dict = {'times': 0, 'score': 0,'scores':[], 'words': [], 'index': []}
        neg_dict = {'times': 0, 'score': 0,'scores':[], 'words': [], 'index': []}

        for index, word in enumerate(word_list):
            word_score = 0
            pre_word = index - 1 >= 0 and word_list[index - 1]
            pre2_word = index - 2 >= 0 and word_list[index - 2]
            pre_word_neg = pre_word in self.neg_degree
            pre2_word_neg = pre2_word in self.neg_degree
            base_score = math.log1p(counter[word])
            # 判断极性
            if (word in self.pos_evaluation) or (word in self.pos_emotion) :
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
                if pre_word_neg or pre2_word_neg:
                    word_score = base_score * -1
                debug and print("%s pos" % word)
                word_scored.add(word_mark)
            elif (word in self.neg_evaluation) or (word in self.neg_emotion) :
                word_mark = "-" + word
                if word_mark in word_scored:
                    continue
                word_score -= base_score
                '''
                1. 不是 不好
                2. 不是 很 不好
                极性反转
                '''
                if pre_word_neg or pre2_word_neg:
                    word_score = base_score * -1
                debug and print("%s neg" % word)
                word_scored.add(word_mark)
            # 判断程度词
            if index - 1 >= 0 and word_score != 0:
                word_set = set([pre_word])
                if pre2_word:
                    word_set.add(pre2_word)
                has_degree = word_set.intersection(self.all_degrees)
                if has_degree:
                    if word_set.intersection(self.more_degree) :
                        word_score = word_score * (FIXED_PA + 0.3)
                    elif  word_set.intersection(self.ish_degree) :
                        word_score = word_score * (FIXED_PA + 0.2)
                    elif  word_set.intersection(self.very_degree ):
                        word_score = word_score * (FIXED_PA + 0.4)
                    elif  word_set.intersection(self.least_degree) :
                        word_score = word_score * (FIXED_PA + 0.1)
                    elif  word_set.intersection(self.most_degree) :
                        word_score = word_score * (FIXED_PA + 0.5)

            if word_score > 0:
                # if debug:
                    # pos_dict['words'].append(word)
                    # pos_dict['index'].append(index)
                    # pos_dict['times'] += 1
                pos_dict['score'] += word_score
                # pos_dict['scores'].append(word_score)
            elif word_score < 0:
                # if debug:
                    # neg_dict['words'].append(word)
                    # neg_dict['index'].append(index)
                    # neg_dict['times'] += 1
                neg_dict['score'] += word_score
                # neg_dict['scores'].append(word_score)

        debug and print(str(pos_dict)+"\n"+str(neg_dict))
        neg_sum = neg_dict['score']
        pos_sum = pos_dict['score']
        all_sum = pos_sum + abs(neg_sum)
        if all_sum == 0:
            return 0

        r = (pos_sum + neg_sum) /all_sum
        return float(format(r,".2f"))


def predict(x, include_evalution_dict=False,include_tc=False,debug=False):
    if predict.classifier.initialized:
        return predict.classifier.predict(x, debug=debug)
    else:
        predict.classifier.initialize(include_evalution_dict=include_evalution_dict,include_tc=include_tc)
        return predict.classifier.predict(x, debug=debug)

def cut(*args,**argv):
    if predict.classifier.initialized:
        return tokenizer.cut(*args,**argv)
    else:
        predict.classifier.initialize()
        return tokenizer.cut(*args,**argv)


predict.classifier = Classifier()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        print(predict(sys.argv[1],debug=True))
