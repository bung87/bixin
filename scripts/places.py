# -*- coding: utf-8 -*-

import json
import os
import re
from prefixtree import PrefixSet

file = os.path.join(os.path.dirname(__file__), "../dictionaries/areas.json")
places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")

import ast
ps = PrefixSet()
with open(file, 'r') as f,\
        open(places, 'w') as out:
    content = f.read()
    spaces = re.findall('"[^"]+"', content)
    for s in spaces:
        space = ast.literal_eval(s)
        ps.add(space)
        out.write("%s 30000 ns\n" % space)  # 北京 34488 ns


assert "大连" not in ps

assert ps.startswith("大连")

for x in ps.startswith("大连"):
    print(x)
