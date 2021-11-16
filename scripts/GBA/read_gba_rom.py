# A python script that pulls data from main series GBA ROMs and outputs it as a JSON.
import commentjson
import os
import itertools as it

# custom to_json method
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

# compute index ranges
def getIndices(indices_str):
    index_ranges = indices_str.split(", ")
    valid_indices = it.chain()
    for r in index_ranges:
        extrema = [int(x) for x in r.split('-')]
        if('-' not in r):
            valid_indices = it.chain(valid_indices, range(extrema[0], extrema[0]+1))
        else:
            valid_indices = it.chain(valid_indices, range(extrema[0], extrema[1]+1))
    return valid_indices

# pk3 char encoding -> unicode
def encodeName(id, offset, length):
    name = ""
    for x in range(length):
        char = char_enc[str(rom[offset + id*length + x])]
        if(char == '\u0000'):
            break
        name += char_enc[str(rom[offset + id*length + x])]
    return name

# grab species data (name, ability slots)
def getSpeciesData(profile_name):
    output = {}
    name_offset = profiles[profile_name]["Species Data"]["Names Offset"]
    table_offset = profiles[profile_name]["Species Data"]["Table Offset"]
    valid_indices = getIndices(profiles[profile_name]["Species Data"]["Valid Indices"])
    for id in valid_indices:
        species = {}
        species["name"] = encodeName(id, name_offset, 11)
        species["slot 1"] = rom[table_offset + id*28 + 22]
        species["slot 2"] = rom[table_offset + id*28 + 23]
        output[id] = species
    return output

# grab move data (name, base pp)
def getMoveData(profile_name):
    output = {}
    name_offset = profiles[profile_name]["Move Data"]["Names Offset"]
    table_offset = profiles[profile_name]["Move Data"]["Table Offset"]
    valid_indices = getIndices(profiles[profile_name]["Move Data"]["Valid Indices"])
    for id in valid_indices:
        move = {}
        move["name"] = encodeName(id, name_offset, 13)
        move["base pp"] = rom[table_offset + id*12 + 4]
        output[id] = move
    return output


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

# generate output
output = {}
output["Species"] = getSpeciesData(profile_name)
output["Moves"] = getMoveData(profile_name)

# all done, write file
with open(os.path.join(root,'out.json'), 'w', encoding='utf-8') as f:
    f.write(to_json(output))
input("...Finished reading ROM!")