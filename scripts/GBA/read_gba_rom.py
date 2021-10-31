# A python script that pulls data from main series GBA ROMs and outputs it as a JSON.
import commentjson
import os
import itertools as it

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

# initialize
root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
profiles = commentjson.load(open(os.path.join(root, 'rom_profiles.json'), encoding="utf8"))
char_enc = commentjson.load(open(os.path.join(root, "../../main-series/gen-3/pk3FormatDex.json"), encoding="utf8"))["pk3"]["Character Encoding"]["English"]
profile_name = input("Enter the ROM profile to be used:\n")

# read rom
with open(os.path.join(root, profiles[profile_name]["ROM"]), 'rb') as f:
    rom = f.read()

# compute index ranges
index_ranges = profiles[profile_name]["Valid Indices"].split(", ")
valid_indices = it.chain()
for r in index_ranges:
    extrema = [int(x) for x in r.split('-')]
    if('-' not in r):
        valid_indices = it.chain(valid_indices, range(extrema[0], extrema[0]+1))
    else:
        valid_indices = it.chain(valid_indices, range(extrema[0], extrema[1]+1))

# generate output
output = {}
name_offset = profiles[profile_name]["Species Names Offset"]
table_offset = profiles[profile_name]["Species Table Offset"]
for id in valid_indices:
    species = {}
    species["name"] = ""
    for x in range(11):
        char = char_enc[str(rom[name_offset + id*11 + x])]
        if(char == '\u0000'):
            break
        species["name"] += char_enc[str(rom[name_offset + id*11 + x])]
    species["slot 1"] = rom[table_offset + id*28 + 22]
    species["slot 2"] = rom[table_offset + id*28 + 23]
    output[id] = species

# all done, write file
with open(os.path.join(root,'out.json'), 'w', encoding='utf-8') as f:
    f.write(to_json(output))
input("...Finished reading ROM!")