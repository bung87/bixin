# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import jieba
import jieba.posseg as pseg
from prefixtree import PrefixSet

DICTIONARIES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "dictionaries")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

pos_result = os.path.join(DATA_DIR, "pos_combined.txt")

neg_result = os.path.join(DATA_DIR, "neg_combined.txt")

ntusd_dir = os.path.join(DICTIONARIES_DIR, "台湾大学NTUSD简体中文情感词典")

pos_file = os.path.join(ntusd_dir, "NTUSD_positive_simplified.txt")

neg_file = os.path.join(ntusd_dir, "NTUSD_negative_simplified.txt")

new_line = "%s\n"

ps = PrefixSet()

places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")

with open(places) as f:
    jieba.load_userdict(f)

    for line in f:
        s = line.strip().split()[0]
        ps.add(s)
    # print(pseg.lcut("大连"))
    # x, y = pseg.lcut("大连")[0]
    # assert y == "ns"


def is_space(word):
    l = list(ps.startswith(word))
    return len(l)


def common_igrnoe(word, tag, text_len):
    word_len = len(word)
    if word_len == 1:  # before accuracy: 0.663919
        return None
    elif tag.startswith('u'):  # u 助词
        return None
    elif tag == "d" and text_len == 1:  # d 副词
        return None
    elif tag == "r":  # 代词
        return None
    elif tag.startswith('c'):  # c 连词
        return None
    elif tag == "p":  # 介词
        return None
    elif tag == 'm':
        return None
    elif tag == 's':  # 处所词
        return None
    elif tag.startswith('x'):  # x 字符串 xx 非语素字 xu 网址URL
        return None
    elif tag == 'zg':
        return None
    elif tag == "f":
        return None
    elif tag.endswith("g"):  # 语素
        return None
    elif is_space(word):
        return None
    return True


stop_ns = ["安宁"]
preserve_words = ["真爱"]  # figure out which parts ignore this is complicated


def clean_word(s):
    text = re.sub(r'&#\d+;', "", s.strip())
    text = re.sub(r'[:：？。，\.#·、…]+$', "", text)
    text = re.sub('\w+·\w+', "", text)
    text = re.sub('.*\.', "", text)  # for ntusd 与..脱离
    if not text:
        return None
    if text != ':)' and re.match(r'^[^\w\s]', text):
        return None
    # elif re.match(r'\w[^\s\w]$',text): #they are 哼！干！呢！瘾？唉！醇? 醇？弇?
    #     return None
    if text in preserve_words:
        return text
    words = list(pseg.cut(text))
    text_len = len(text)
    if len(words) == 1:
        for word, tag in words:
            if tag == "n" and text_len == 1:
                return None
            if tag.startswith('nr') or (tag.startswith('ns') and word not in stop_ns)or tag.startswith('nt') or tag.startswith('nz'):
                return None
            if not common_igrnoe(word, tag, text_len):
                return None
    elif all(y == list(words[0])[1] for x, y in words):
        return None

    return text


def simple_write(pos_file, neg_file, start_line=0, mode='a', pos_result=pos_result, neg_result=neg_result):
    with open(pos_file) as f,\
            open(pos_result, mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)
        for line in f:
            if line.startswith("#"):
                continue
            word = clean_word(line)
            if word:
                f2.write(new_line % word)

    with open(neg_file) as f,\
            open(neg_result, mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)
        for line in f:
            if line.startswith("#"):
                continue
            word = clean_word(line)
            if word:
                f2.write(new_line % word)


#
if len(sys.argv) == 2 and sys.argv[1] == "eva":

    pos_result = os.path.join(DATA_DIR, "pos_eva.txt")

    neg_result = os.path.join(DATA_DIR, "neg_eva.txt")

    hownet_dir = os.path.join(DICTIONARIES_DIR, "知网Hownet情感词典")

    pos_file = os.path.join(hownet_dir, "正面评价词语（中文）.txt")

    neg_file = os.path.join(hownet_dir, "负面评价词语（中文）.txt")

    simple_write(pos_file, neg_file, start_line=3, mode='w',
                 pos_result=pos_result, neg_result=neg_result)
    exit()

if len(sys.argv) == 2 and sys.argv[1] == "neg":
    negations_file = os.path.join(DICTIONARIES_DIR, "否定词典", "否定.txt")

    with open(negations_file) as negations,\
            open(os.path.join(DATA_DIR, "negations.json"), 'w') as j,\
            open(os.path.join(DATA_DIR, "readme.txt"), 'a') as readme:
        negations_list = [line.strip() for line in negations.readlines()]
        readme.write(new_line % "Negations")
        readme.write(new_line % "=========")
        readme.write(new_line % str(negations_list))
        json.dump(negations_list, j)
    exit()

simple_write(pos_file, neg_file, mode='w')

hontai_file = os.path.join(DICTIONARIES_DIR, '情感词汇本体', "Sheet1-Table 1.csv")

with open(hontai_file) as f,\
        open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg:
    next(f)
    for line in f:
        cols = line.split(",")
        word = clean_word(cols[0])
        if not word:
            continue
        polarity = int(cols[6])
        if polarity == 1:
            pos.write(new_line % word)
        elif polarity == 2:
            neg.write(new_line % word)


polarity_table = os.path.join(DICTIONARIES_DIR, '汉语情感词极值表', "汉语情感词极值表.txt")

with open(polarity_table) as f,\
        open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg:
    for x in range(14):
        next(f)
    for line in f:
        cols = line.split("\t")
        word = clean_word(cols[0])
        if not word:
            continue
        polarity = float(cols[1])
        if abs(polarity) <= 1.5:
            continue
        if polarity > 0:
            pos.write(new_line % word)
        elif polarity < 0:
            neg.write(new_line % word)

polarity_table = os.path.join(
    DICTIONARIES_DIR, 'BosonNLP_sentiment_score', "BosonNLP_sentiment_score.txt")

with open(polarity_table) as f,\
        open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg:

    for line in f:
        cols = line.split(" ")
        word = clean_word(cols[0])
        if not word:
            continue
        elif re.match('[0-9a-zA-Z：:]+', word):
            continue
        polarity = float(cols[1])
        if polarity > -1.25:  # 忽略大量社交媒体热词高频词
            break
        # if polarity > 0:
        #     pos.write(new_line % word)
        # elif polarity < 0:
        neg.write(new_line % word)

# 短语


def multi_write(words, result, sentence_file):
    if len(words) == 1:
        for x, tag in words:
            word = x.strip()
            if not word:
                continue
            result.write(new_line % word)
    else:
        sentence_file.write(new_line % "".join([x for x, i in words]))


polarity_table = os.path.join(
    DICTIONARIES_DIR, '情感词典及其分类', "情感词典及其分类_csv", "Sheet2-Table 1.csv")

pos_sentence = os.path.join(DATA_DIR, "pos_sentence.txt")

neg_sentence = os.path.join(DATA_DIR, "neg_sentence.txt")

with open(polarity_table) as f,\
        open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg,\
        open(pos_sentence, 'w') as pos_sentence,\
        open(neg_sentence, 'w') as neg_sentence:

    next(f)
    for line in f:
        cols = line.split(",")
        pos_sent = cols[1]
        neg_sent = cols[0]

        pos_words = list(pseg.cut(pos_sent)) if pos_sent else None
        neg_words = list(pseg.cut(neg_sent)) if neg_sent else None

        pos_words and multi_write(pos_words, pos, pos_sentence)
        neg_words and multi_write(neg_words, neg, neg_sentence)

tsinghua_dir = os.path.join(DICTIONARIES_DIR, "清华大学李军中文褒贬义词典")

pos_file = os.path.join(tsinghua_dir, "tsinghua.positive.gb.txt")

neg_file = os.path.join(tsinghua_dir, "tsinghua.negative.gb.txt")

simple_write(pos_file, neg_file, mode='a')


hownet_dir = os.path.join(DICTIONARIES_DIR, "知网Hownet情感词典")

pos_file = os.path.join(hownet_dir, "正面情感词语（中文）.txt")

neg_file = os.path.join(hownet_dir, "负面情感词语（中文）.txt")

simple_write(pos_file, neg_file, start_line=3, mode='a')


polarity_table = os.path.join(DICTIONARIES_DIR, '褒贬词及其近义词', "褒贬词及其近义词.csv")

with open(polarity_table) as f,\
        open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg:
    next(f)
    for line in f:
        cols = line.split(",")
        word = clean_word(cols[0])
        if not word:
            continue
        polarity = cols[2]
        if polarity == "褒义":
            pos.write(new_line % word)
        elif polarity == "贬义":
            neg.write(new_line % word)

with open(pos_result) as pos,\
        open(neg_result) as neg,\
        open(os.path.join(DATA_DIR, "readme.txt"), 'w') as readme:
    line = "Combined pos with results to %s lines" % sum(1 for line in pos)
    print(line)
    readme.write(new_line % line)
    line = "Combined neg with results to %s lines" % sum(1 for line in neg)
    print(line)
    readme.write(new_line % line)

import subprocess

uniq_io = "sort %s | uniq > %s"

pos_merged = os.path.join(DATA_DIR, "pos.txt")

neg_merged = os.path.join(DATA_DIR, "neg.txt")

subprocess.check_output(uniq_io % (pos_result, pos_merged), shell=True)

subprocess.check_output(uniq_io % (neg_result, neg_merged), shell=True)

with open(pos_merged) as pos,\
        open(neg_merged) as neg,\
        open(os.path.join(DATA_DIR, "readme.txt"), 'a') as readme:
    line = "Unified pos with results to %s lines" % sum(1 for line in pos)
    print(line)
    readme.write(new_line % line)
    line = "Unified neg with results to %s lines" % sum(1 for line in neg)
    print(line)
    readme.write(new_line % line)
