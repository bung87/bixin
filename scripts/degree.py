# -*- coding: utf-8 -*-

import os,re
import json

DICTIONARIES_DIR = os.path.join(os.path.dirname(__file__),"..","dictionaries")

DATA_DIR = os.path.join(os.path.dirname(__file__),"..","data")

file_path = os.path.join(DICTIONARIES_DIR,"知网Hownet情感词典","程度级别词语（中文）.txt")

result = {}

with open(file_path) as f,\
    open(os.path.join(DATA_DIR,'degrees.json'),'w') as f2:
    next(f)
    next(f)
    mark_num = None
    for line in f:
        text = line.strip()
        if not text:
            continue
        matched = re.match("^([\d])\.",text)
        if matched:
            mark_num = matched.group(1)
            continue
        l = result.get(mark_num,[])
        l.append(text)
        result.update({
            mark_num:l
        })
    print(result.keys())
    print(result)
    json.dump(result,f2)