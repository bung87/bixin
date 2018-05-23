# -*- coding: utf-8 -*-

import os,re

DICTIONARIES_DIR = os.path.join(os.path.dirname(__file__),"..","dictionaries")

DATA_DIR = os.path.join(os.path.dirname(__file__),"..","data")

pos_result = os.path.join(DATA_DIR,"pos_combined.txt")

neg_result = os.path.join(DATA_DIR,"neg_combined.txt")

ntusd_dir = os.path.join(DICTIONARIES_DIR,"台湾大学NTUSD简体中文情感词典")

pos_file = os.path.join(ntusd_dir,"NTUSD_positive_simplified.txt")

neg_file = os.path.join(ntusd_dir,"NTUSD_negative_simplified.txt")

new_line = "%s\n"

def clean_word(s):
    return re.sub('&#\d+;',"",s)

def simple_write(pos_file,neg_file,start_line=0,mode='a',pos_result=pos_result,neg_result=neg_result):
    with open(pos_file) as f,\
        open(pos_result,mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)
        for line in f :
            if line.startswith("#"):
                continue
            word = clean_word(line)
            if word:
                f2.write(word)

    with open(neg_file) as f,\
        open(neg_result,mode) as f2:
        if start_line:
            for x in range(start_line):
                next(f)
        for line in f :
            if line.startswith("#"):
                continue
            word = clean_word(line)
            if word:
                f2.write(word)

simple_write(pos_file,neg_file,mode='w')

hontai_file = os.path.join(DICTIONARIES_DIR,'情感词汇本体',"Sheet1-Table 1.csv")

with open(hontai_file) as f,\
    open(pos_result,'a') as pos,\
    open(neg_result,'a') as neg:
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


polarity_table = os.path.join(DICTIONARIES_DIR,'汉语情感词极值表',"汉语情感词极值表.txt")

with open(polarity_table) as f,\
    open(pos_result,'a') as pos,\
    open(neg_result,'a') as neg:
    for x in range(14):
        next(f)
    for line in f:
        cols = line.split("\t")
        word = clean_word(cols[0])
        if not word :
            continue
        polarity = float(cols[1])
        if polarity > 0:
            pos.write(new_line % word)
        elif polarity < 0:
            neg.write(new_line % word)

tsinghua_dir = os.path.join(DICTIONARIES_DIR,"清华大学李军中文褒贬义词典")

pos_file = os.path.join(tsinghua_dir,"tsinghua.positive.gb.txt")

neg_file = os.path.join(tsinghua_dir,"tsinghua.negative.gb.txt")

simple_write(pos_file,neg_file,mode='a')


hownet_dir = os.path.join(DICTIONARIES_DIR,"知网Hownet情感词典")

pos_file = os.path.join(hownet_dir,"正面情感词语（中文）.txt")

neg_file = os.path.join(hownet_dir,"负面情感词语（中文）.txt")

simple_write(pos_file,neg_file,start_line=3,mode='a')

polarity_table = os.path.join(DICTIONARIES_DIR,'褒贬词及其近义词',"褒贬词及其近义词.csv")

with open(polarity_table) as f,\
    open(pos_result,'a') as pos,\
    open(neg_result,'a') as neg:
    next(f)
    for line in f:
        cols = line.split(",")
        word = clean_word(cols[0])
        if not word:
            continue
        polarity = cols[2]
        if polarity =="褒义":
            pos.write(new_line % word)
        elif polarity =="贬义":
            neg.write(new_line % word)

with open(pos_result) as pos,\
    open(neg_result) as neg,\
    open(os.path.join(DATA_DIR,"readme.txt"),'w') as readme:
    line = "Combined pos with results to %s lines" % sum(1 for line in pos)
    print(line)
    readme.write(new_line % line)
    line = "Combined neg with results to %s lines" % sum(1 for line in neg) 
    print(line)
    readme.write(new_line % line)

import subprocess

uniq_io = "sort %s | uniq > %s"

pos_merged = os.path.join(DATA_DIR,"pos.txt")

neg_merged = os.path.join(DATA_DIR,"neg.txt")

subprocess.check_output(uniq_io % (pos_result,pos_merged), shell=True)

subprocess.check_output(uniq_io % (neg_result,neg_merged), shell=True)

with open(pos_merged) as pos,\
    open(neg_merged) as neg,\
    open(os.path.join(DATA_DIR,"readme.txt"),'a') as readme:
    line = "Unified pos with results to %s lines" % sum(1 for line in pos)
    print(line)
    readme.write(new_line % line)
    line = "Unified neg with results to %s lines" % sum(1 for line in neg) 
    print(line)
    readme.write(new_line % line)
