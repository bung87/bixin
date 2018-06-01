import os
import json
import pickle
from pickletools import optimize

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "bixin", "data")

output_path = os.path.join(OUTPUT_DIR, "dict.pkl")

MAINTAINED_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "self_maintained")

MAINTAINED_POS = os.path.join(MAINTAINED_DATA_DIR, "pos.txt")
MAINTAINED_NEG = os.path.join(MAINTAINED_DATA_DIR, "neg.txt")


def prepare(obj):
    picklestring = pickle.dumps(obj)
    return optimize(picklestring)


def release():
    with open(output_path, "wb") as output:
        result = {}
        with open(os.path.join(DATA_DIR, 'pos.txt')) as f,\
                open(MAINTAINED_POS) as maintained_pos:
            pos_emotion = set([x.strip() for x in f]).union(
                [x.strip() for x in maintained_pos])

            result["pos_emotion"] = pos_emotion

        with open(os.path.join(DATA_DIR, 'neg.txt')) as f,\
                open(MAINTAINED_NEG) as maintained_neg:
            neg_emotion = set([x.strip() for x in f]).union(
                [x.strip() for x in maintained_neg])

            result["neg_emotion"] = neg_emotion

        result["pos_envalute"] = []
        result["neg_envalute"] = []

        with open(os.path.join(DATA_DIR, "degrees.json")) as f:
            degrees = json.load(f)
            result["degrees"] = degrees

        negations = set(
            json.load(open(os.path.join(DATA_DIR, 'negations.json'))))

        result["negations"] = negations

        # places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")
        # result["places"] = set(places)

        pickle.dump(result, output)
