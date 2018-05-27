import os
import json
import pickle 
from  pickletools import optimize

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "bixin","data")

output_path = os.path.join(OUTPUT_DIR,"dict.pkl")

def prepare(obj):
    picklestring = pickle.dumps(obj)
    return optimize(picklestring)

with open(output_path,"wb") as output:
    result = {}
    with open(os.path.join(DATA_DIR, 'pos.txt')) as f:
        pos_emotion = set([x.strip() for x in f.readlines()])
        # picklestring = prepare(pos_emotion)
        # output.write(picklestring )
        # pickle.dump(picklestring,output)
        result["pos_emotion"] = pos_emotion

    with open(os.path.join(DATA_DIR, 'neg.txt')) as f:
        neg_emotion = set([x.strip() for x in f.readlines()])
        # picklestring = prepare(pos_emotion)
        # output.write(picklestring)
        # pickle.dump(picklestring,output)
        result["neg_emotion"] = neg_emotion

    result["pos_envalute"] = []
    result["neg_envalute"] = []
    # picklestring = prepare([])
    # pickle.dump(picklestring,output) # pos eva
    # pickle.dump(picklestring,output) # neg eva
    # output.write(picklestring)
    # output.write(picklestring)

    with open(os.path.join(DATA_DIR, "degrees.json")) as f:
        degrees = json.load(f)
        # picklestring = prepare(degrees)
        # pickle.dump(picklestring,output)
        # output.write( prepare(degrees) )
        result["degrees"] = degrees

    negations = set(json.load(open(os.path.join(DATA_DIR, 'negations.json'))))
    # picklestring = prepare(negations) 
    # output.write(picklestring)
    # pickle.dump(picklestring,output)
    result["negations"] = negations

    # places = os.path.join(os.path.dirname(__file__), "../dictionaries/places.txt")
    # result["places"] = set(places)

    pickle.dump(result,output)
    