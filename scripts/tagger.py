# -*- coding: utf-8 -*-
# prepare word from vary dictionaries
import os
import sys
import re
import json
from jieba_fast import Tokenizer
from prefixtree import PrefixSet
import subprocess
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
subprocess.check_call(["tar","-xzf","dictionaries.tar.gz","-C",root])

big_dict = os.path.join(os.path.dirname(__file__), "..", "bixin","data","dict.txt.big")
tokenizer = Tokenizer(big_dict)


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

pos_sentences = set()
neg_sentences = set()

places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")

with open(places) as f:
    tokenizer.load_userdict(f)

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
    elif tag == 'zg': # 状态语素
        return None
    elif tag == "f":
        return None
    elif tag.endswith("g"):  # 语素
        return None
    elif is_space(word):
        return None
    return True


stop_ns = ["安宁"]
maintained_dir = os.path.join(DICTIONARIES_DIR, "self_maintained")
preserve_pos_words = preserve_neg_words = stop_words = []

with open(os.path.join(maintained_dir, "pos.txt")) as f:
    preserve_pos_words = set([x.strip() for x in f])

with open(os.path.join(maintained_dir, "neg.txt")) as f:
    preserve_neg_words = set([x.strip() for x in f])

with open(os.path.join(maintained_dir, "stopwords.txt")) as f:
    stop_words = set([x.strip() for x in f])

def clean_words(s):
    text = re.sub(r'&#\d+;', "", s.strip())
    text = re.sub(r'[:：？。，\.#·、…]+$', "", text)
    text = re.sub('\w+·\w+', "", text)
    text = re.sub('.*\.', "", text).strip()  # for ntusd 与..脱离
    if not text or text in stop_words:
        return None
    if text != ':)' and re.match(r'^[^\w\s]', text):
        return None
    # elif re.match(r'\w[^\s\w]$',text): #they are 哼！干！呢！瘾？唉！醇? 醇？弇?
    #     return None
    words = list(tokenizer.tag(text))
    text_len = len(text)
    words_len = len(words)


    if words_len == 1:
        for word, tag in words:
            if tag == "n" and (text_len == 1 or text_len == 3):
                return None
            # nr 阴冷
            if tag.startswith('nr') or (tag.startswith('ns') and word not in stop_ns)or tag.startswith('nt') or tag.startswith('nz'):
                return None
            if not common_igrnoe(word, tag, text_len):
                return None
    elif words[words_len-1].flag in ["uj","uv"]:
        # [pair('有模有样', 'l'), pair('地', 'uv')]
        # [pair('阴冷', 'nr'), pair('的', 'uj')]
        content = "".join([x.word for x in words[:-1]])
        if  content in stop_words:
            return None
        return content
    elif words[0].word == "使":
        left_words = "".join([x.word for x in words[1:]])
        if left_words in stop_words:
            return None
        if tokenizer.find(left_words):
            return left_words
    # elif words[-1].word in ["的","地"]:
    #     left_words = "".join([x.word for x in words[:-1]])
    #     if left_words in stop_words:
    #         return None
    #     if left_words in vocs:
    #         return left_words
    elif all(y == list(words[0])[1] for x, y in words):
        return None

    return text

# def filter_line(line):
#     _words = line
#     the_words = None
#     if words_len == 2 or words_len == 3:
#         if _words[0] in ["有"]:
#             the_words = "".join(_words[1:])
#         elif _words[words_len-1] in ["的","地"]:
#             the_words = "".join(_words[:-1])
#         else:
#             the_words = text
#     elif _words[words_len-1] == "的":
#         the_words = "".join(_words[:-1])
#     elif _words[0] == "使":
#         the_words = "".join(_words[1:])
#
#     if the_words:
#         words = list(tokenizer.tag(the_words))
#         text_len = len(the_words)
#         words_len = len(words)

def simple_write(pos_file, neg_file, start_line=0, mode='a', pos_result=pos_result, neg_result=neg_result):
    with open(pos_file) as f,\
            open(pos_result, mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)

        for line_raw in f:
            line = line_raw.strip()
            if line.startswith("#"):
                continue
            if re.search("[你我他]|自己",line) and len(line) > 4:
                pos_sentences.add(line)
                continue
            if re.search("\W",line):
                pos_sentences.add(line)
                continue
            word = clean_words(line)
            if word:
                f2.write(new_line % word)

    with open(neg_file) as f,\
            open(neg_result, mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)
        isNTUSD = os.path.basename(neg_file).startswith("NTUSD")
        for line_raw in f:
            line =line_raw.strip()
            if isNTUSD and line.startswith("使"):
                continue
            if isNTUSD and line.find("..") != -1:
                neg_sentences.add(line)
                continue
            if line.startswith("#"):
                continue
            if re.search("[你我他]|自己", line) and len(line) > 4:
                neg_sentences.add(line)
                continue
            if re.search("\W",line):
                neg_sentences.add(line)
                continue
            word = clean_words(line)
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
        polarity = int(cols[6])
        if re.search("[你我他]|自己", cols[0]) and len(cols[0]) > 4:
            if polarity == 1:
                pos_sentences.add(cols[0])
            elif polarity == 2:
                neg_sentences.add(cols[0])
            continue
        if re.search("\W",cols[0]):
            if polarity == 1:
                pos_sentences.add(cols[0])
            elif polarity == 2:
                neg_sentences.add(cols[0])
            continue
        word = clean_words(cols[0])
        
        if not word:
            continue
        
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
        polarity = float(cols[1])
        if abs(polarity) <= 1.5:
            continue
        if re.search("[你我他]|自己", cols[0]) and len(cols[0]) > 4:
            if polarity > 0:
                pos_sentences.add(cols[0])
            elif polarity < 0:
                neg_sentences.add(cols[0])
            continue
        if re.search("\W",cols[0]):
            if polarity > 0:
                pos_sentences.add(cols[0])
            elif polarity < 0:
                neg_sentences.add(cols[0])
            continue
        word = clean_words(cols[0])
        if not word:
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
        word = clean_words(cols[0])
        if not word:
            continue
        elif re.match('[0-9a-zA-Z：:]+', word):
            continue
        polarity = float(cols[1])
        if polarity > -1.29249906329:  # 忽略大量社交媒体热词高频词
            break
        # if polarity > 0:
        #     pos.write(new_line % word)
        # elif polarity < 0:
        neg.write(new_line % word)



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
        word = clean_words(cols[0])
        if not word:
            continue
        polarity = cols[2]
        if polarity == "褒义":
            pos.write(new_line % word)
        elif polarity == "贬义":
            neg.write(new_line % word)

with open(pos_result, 'a') as pos,\
        open(neg_result, 'a') as neg:
    for x in preserve_pos_words:
        pos.write(new_line % x)
    for x in preserve_neg_words:
        neg.write(new_line % x)

# 短语


def multi_write(words, result, sentence_file,tag):
    if len(words) == 1:
        for x, tag in words:
            word = x.strip()
            if not word:
                continue
            result.write(new_line % word)
    else:
        if tag =="pos":
            pos_sentences.add("".join([x for x, i in words]))
        else:
            neg_sentences.add("".join([x for x, i in words]))


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

        pos_words = list(tokenizer.tag(pos_sent)) if pos_sent else None
        neg_words = list(tokenizer.tag(neg_sent)) if neg_sent else None

        pos_words and multi_write(pos_words, pos, pos_sentence,"pos")
        neg_words and multi_write(neg_words, neg, neg_sentence,"neg")
    for word in pos_sentences:
        pos_sentence.write(new_line % word)
    for word in neg_sentences:
        neg_sentence.write(new_line % word)


with open(pos_result) as pos,\
        open(neg_result) as neg,\
        open(os.path.join(DATA_DIR, "readme.txt"), 'w') as readme:
    line = "Combined pos with results to %s lines" % sum(1 for line in pos)
    print(line)
    readme.write(new_line % line)
    line = "Combined neg with results to %s lines" % sum(1 for line in neg)
    print(line)
    readme.write(new_line % line)



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
