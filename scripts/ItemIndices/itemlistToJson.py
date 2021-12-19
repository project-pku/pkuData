# Script that formats a list of items (input.txt) to an itemDex (output.json)
# Item id # is its line number. Empty ids should have empty lines.
# replacements.json has a dict of item name replacements to make (eg. Parlyz Heal -> Paralyze Heal)
import os
import commentjson

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
    if(o == "\u0000"): # properly escape null terminator
      ret += '"\\u0000"'
    else:
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

# start
FORMAT = input("What's the name of the format? ")
root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
replacements = commentjson.load(open(os.path.join(root, "replacements.json"), encoding="utf8"))
with open(os.path.join(root, "input.txt"), encoding="utf8") as f:
  lines = f.readlines()

final = {}
count = 0
for line in lines:
  #remove extra "\n"
  if line[-1] == "\n":
    line = line[0:-1]
  #skip empty strings
  if line == "":
    continue
  #replace old spellings with new canonical ones
  if line in replacements:
    line = replacements[line]
  #alert if duplicate found
  if line in final:
    raise Exception("Duplicate item found: " + line)

  final[line] = {
    "Indices": {
      FORMAT: count
    },
    "Exists in": [FORMAT]
  }
  count += 1

with open(os.path.join(root,'output.json'), 'w', encoding='utf-8') as f:
  f.write(to_json(final))
input("Wrote to output.json. Press enter to finish...")