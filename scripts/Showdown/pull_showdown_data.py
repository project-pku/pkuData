# A python script that pulls item, ability, and move data from
# the Showdown Github repo and outputs it as a JSON.
import os
from urllib.request import urlopen

def repo_to_list(url):
    text = urlopen(url).read().decode('utf-8') # download file
    marker = "name: \""
    err = [n for n in range(len(text)) if text.find(marker, n) == n] # find all marker indices
    names = []
    for n in err:
        end = text.find('\"', len(marker)+n+1)
        names.append(text[len(marker)+n:end])
    return names

def list_to_json(list):
    jobj = {}
    for name in list:
        temp = {}
        temp["Exists in"] = ["Showdown"]
        jobj[name] = temp
    return jobj

def to_json(o, level=0):
    INDENT = 2
    SPACE = " "
    NEWLINE = "\n"
    ret = ""
    if isinstance(o, dict):
        ret += "{" + NEWLINE
        comma = ""
        for k, v in o.items():
            ret += comma
            comma = ",\n"
            ret += SPACE * INDENT * (level + 1)
            ret += '"' + str(k) + '":' + SPACE
            ret += to_json(v, level + 1)

        ret += NEWLINE + SPACE * INDENT * level + "}"
    elif isinstance(o, str):
        ret += '"' + o + '"'
    elif isinstance(o, list):
        ret += "[" + ", ".join([to_json(e, level + 1) for e in o]) + "]"
    # Tuples are interpreted as lists
    elif isinstance(o, tuple):
        ret += "[" + ", ".join(to_json(e, level + 1) for e in o) + "]"
    elif isinstance(o, bool):
        ret += "true" if o else "false"
    elif isinstance(o, int):
        ret += str(o)
    elif isinstance(o, float):
        ret += '%.7g' % o
    elif o is None:
        ret += 'null'
    else:
        raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))
    return ret

# ----------------
## Begin Script
# ----------------

## Constants
BASE = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/text/"
MOVES = "moves.ts"
ABILITIES = "abilities.ts"
ITEMS = "items.ts"
root = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------
## Process Moves
print("Downloading moves...")
names = repo_to_list(BASE+MOVES)

# remove hidden power types
HP_NAME = "Hidden Power"
names = [x for x in names if not (x.startswith(HP_NAME) and len(x) > len(HP_NAME))]

with open(os.path.join(root,'moves.json'), 'w', encoding='utf-8') as f:
     f.write(to_json(list_to_json(names)))

# -----------------------------
## Process Items
print("Downloading items...")
names = repo_to_list(BASE+ITEMS)

with open(os.path.join(root,'items.json'), 'w', encoding='utf-8') as f:
     f.write(to_json(list_to_json(names)))

# -----------------------------
## Process Abilities
print("Downloading abilities...")
names = repo_to_list(BASE+ABILITIES)
names.remove("No Ability") # remove "No Ability", empty abilities handled differently
with open(os.path.join(root,'abilities.json'), 'w', encoding='utf-8') as f:
     f.write(to_json(list_to_json(names)))

# -----------------------------
input("Download complete, Showdown data outputted!")