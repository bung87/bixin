import os
import sys
import jieba_fast
from jieba_fast import dt,default_logger
default_logger.disabled = True

big_dict = os.path.join(os.path.dirname(__file__), "..", "bixin", "data", "dict.txt.big")
jieba_fast.set_dictionary(big_dict)
jieba_fast.initialize()

DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TMP = os.path.join(os.path.dirname(__file__), "..", "tmp")

if __name__ == "__main__":
    vocabulary_size = len(dt.FREQ)
    vocs = set(dt.FREQ.keys())
    name = sys.argv[1]
    filename = os.path.join(DIR, name + ".txt")
    with open(filename) as f,open(os.path.join(TMP, name+ "_missed.txt"),"w") as tmp:
        hits = 0
        miss = 0
        for l in f:
            line = l.strip()
            if line in vocs:
                hits = hits + 1
            else:
                miss = miss +1
                tmp.write("%s\n" % line)
        print("%f" % (hits/(hits+miss)) )
