import commentjson
import os

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

# initialize
DEX_NAME = "Move"
FORMAT_NAME = "Showdown"
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
dex_path = os.path.join(root, "showdown", f'showdown{DEX_NAME}Dex.json')

dex = commentjson.load(open(dex_path, encoding="utf8"))
for key in dex:
  dex[key]["Indices"] = {
    FORMAT_NAME: key
  }

# merging complete, write file
with open(dex_path, 'w', encoding='utf-8') as f:
  f.write(to_json(dex))

input("\nOutputted modified dex...")