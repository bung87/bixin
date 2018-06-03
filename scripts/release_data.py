import os
import json
import pickle
from pickletools import optimize

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "bixin", "data")

output_path = os.path.join(OUTPUT_DIR, "dict.pkl")

MAINTAINED_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "dictionaries", "self_maintained")

MAINTAINED_POS = os.path.join(MAINTAINED_DATA_DIR, "pos.txt")
MAINTAINED_NEG = os.path.join(MAINTAINED_DATA_DIR, "neg.txt")


def prepare(obj):
    picklestring = pickle.dumps(obj)
    return optimize(picklestring)


def pos_eva():
    with open(os.path.join(DATA_DIR, 'pos_eva.txt')) as f:
        words = set([x.strip() for x in f])
        return words


def neg_eva():
    with open(os.path.join(DATA_DIR, 'neg_eva.txt')) as f:
        words = set([x.strip() for x in f])
        return words


def release():
    with open(output_path, "wb") as output:
        result = {}
        with open(os.path.join(DATA_DIR, 'pos.txt')) as f, \
                open(MAINTAINED_POS) as maintained_pos:
            pos_emotion = set([x.strip() for x in f]).union(
                [x.strip() for x in maintained_pos])

            result["pos_emotion"] = pos_emotion

        with open(os.path.join(DATA_DIR, 'neg.txt')) as f, \
                open(MAINTAINED_NEG) as maintained_neg:
            neg_emotion = set([x.strip() for x in f]).union(
                [x.strip() for x in maintained_neg])

            result["neg_emotion"] = neg_emotion

        with open(os.path.join(DATA_DIR, 'pos_tc.txt')) as f:
            pos_emotion = set([x.strip() for x in f])

            result["pos_emotion_tc"] = pos_emotion

        with open(os.path.join(DATA_DIR, 'neg_tc.txt')) as f:
            neg_emotion = set([x.strip() for x in f])

            result["neg_emotion_tc"] = neg_emotion

        with open(os.path.join(DATA_DIR, 'pos_sentence.txt')) as f:
            pos_sentence = set([x.strip() for x in f])
            result["pos_sentence"] = pos_sentence

        with open(os.path.join(DATA_DIR, 'neg_sentence.txt')) as f:
            neg_sentence = set([x.strip() for x in f])

            result["neg_sentence"] = neg_sentence

        result["pos_evaluation"] = pos_eva()
        result["neg_evaluation"] = neg_eva()

        with open(os.path.join(DATA_DIR, "degrees.json")) as f:
            degrees = json.load(f)
            result["degrees"] = degrees

        negations = set(
            json.load(open(os.path.join(DATA_DIR, 'negations.json'))))

        result["negations"] = negations
        # places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")
        # result["places"] = set(places)

        pickle.dump(result, output)


if __name__ == "__main__":
    release()
