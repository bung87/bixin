from os import path
from opencc import OpenCC

DIR = path.join(path.dirname(__file__), "..", "data")

POS = path.join(DIR, "pos.txt")
NEG = path.join(DIR, "neg.txt")


def convert1():
    pos_hk = path.join(DIR, "pos_hk.txt")
    neg_hk = path.join(DIR, "neg_hk.txt")

    pos_tw = path.join(DIR, "pos_tw.txt")
    neg_tw = path.join(DIR, "neg_tw.txt")

    with open(POS) as pos, \
            open(NEG) as neg, \
            open(pos_hk, "w") as pos_hk, \
            open(neg_hk, "w") as neg_hk, \
            open(pos_tw, "w") as pos_tw, \
            open(neg_tw, "w") as neg_tw:
        pos = pos.read()
        neg = neg.read()
        s2hk = OpenCC('s2hk')

        pos_converted = s2hk.convert(pos)
        neg_converted = s2hk.convert(neg)

        pos_hk.write(pos_converted)
        neg_hk.write(neg_converted)

        s2tw = OpenCC('s2tw')
        pos_converted = s2tw.convert(pos)
        neg_converted = s2tw.convert(neg)

        pos_tw.write(pos_converted)
        neg_tw.write(neg_converted)


def convert2():
    pos_tc_path = path.join(DIR, "pos_tc.txt")
    neg_tc_path = path.join(DIR, "neg_tc.txt")

    with open(POS) as pos, \
            open(NEG) as neg, \
            open(pos_tc_path, "w") as pos_tc, \
            open(neg_tc_path, "w") as neg_tc:
        pos = pos.read()
        neg = neg.read()

        pos_set = pos.split("\n")
        neg_set = neg.split("\n")

        s2hk = OpenCC('s2hk')

        pos_converted_hk = s2hk.convert(pos)
        neg_converted_hk = s2hk.convert(neg)

        s2tw = OpenCC('s2tw')

        pos_converted = s2tw.convert(pos)
        neg_converted = s2tw.convert(neg)

        pos = set(pos_converted_hk.split("\n")).union(pos_converted.split("\n"))
        neg = set(neg_converted_hk.split("\n")).union(neg_converted.split("\n"))

        pos_tc.write("\n".join(sorted(pos.difference(pos_set))))
        neg_tc.write("\n".join(sorted(neg.difference(neg_set))))


if __name__ == "__main__":
    convert2()
