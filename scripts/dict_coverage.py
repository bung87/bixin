import os
import sys
from jieba_fast import Tokenizer

big_dict = os.path.join(os.path.dirname(__file__), "..", "bixin", "data", "dict.txt.big")
tokenizer = Tokenizer(big_dict)

DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TMP = os.path.join(os.path.dirname(__file__), "..", "tmp")

if __name__ == "__main__":

    name = sys.argv[1]
    filename = os.path.join(DIR, name + ".txt")
    with open(filename) as f,open(os.path.join(TMP, name+ "_missed.txt"),"w") as tmp:
        hits = 0
        miss = 0
        for l in f:
            line = l.strip()
            if tokenizer.find(line):
                hits = hits + 1
            else:
                miss = miss +1
                tmp.write("%s\n" % line)
        print("%f" % (hits/(hits+miss)) )
