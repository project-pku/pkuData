# A script that compiles a speciesDex from a uranium species dump.
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

# ----------------
## Begin Script
# ----------------
appToBaseForm = {
  "Halloween": "",
  "Christmas": "",
  "Easter": "",
  "Anniversary": "",
  "Halloween Mega": "Mega",
  "Christmas Mega": "Mega",
  "Easter Mega": "Mega",
}
baseToMega = {
  "": "Mega",
  "Nuclear": "Nuclear Mega",
}
renameMap = {
  "Nuclear Mega": "Mega|Nuclear",
  "Halloween Mega": "Halloween",
  "Christmas Mega": "Christmas",
  "Easter Mega": "Easter",
}

# read data
root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FORMATNAME = "pkeUranium"
LINES_PER_SPECIES = 11
#mainseriesDex = commentjson.load(open(os.path.join(root, "../../main-series/main-seriesSpeciesDex.json"), encoding="utf8"))
uraniumAbilityDex = commentjson.load(open(os.path.join(root, "../../essentials/uranium/pkeUraniumAbilityDex.json"), encoding='utf-8'))
uraniumItemDex = commentjson.load(open(os.path.join(root, "../../essentials/uranium/pkeUraniumItemDex.json"), encoding='utf-8'))
speciesDump = commentjson.load(open(os.path.join(root, "species.json"), encoding='utf-8'))

# define growthrate + gender rate maps
growth = ["Medium Fast", "Erratic", "Fluctuating", "Medium Slow", "Fast", "Slow"]
gender = {
  0: "All Male",
  31: "Male 7 Female 1",
  63: "Male 3 Female 1",
  127: "Male 1 Female 1",
  191: "Male 1 Female 3",
  225: "Male 1 Female 7",
  254: "All Female",
  255: "All Genderless",
}

#get cannon ability name
def getAbility(ind):
  return list(uraniumAbilityDex)[ind]

#get cannon item name
def getItem(ind):
  return list(uraniumItemDex)[ind]

#rename form to cannonical name
def renameForm(form):
  if form in renameMap:
    return renameMap[form]
  else:
    return form

# read lang data
languages = ["French", "German", "Spanish", "Portuguese", "Chinese Simplified"]
langDict = {}
for lang in languages:
  langDict[lang] = commentjson.load(open(os.path.join(root, f"species-{lang}.json"), encoding='utf-8'))

# ##test uniqueness of a language
# for x in speciesDump:
#   if speciesDump[x]["Species"] != langDict["German"][x]["Species"]:
#     raise Exception(f"{x} is different")
# raise Exception("NONE")

# compile dex
uraniumdex = {}
for x in speciesDump:
  dataEntry = speciesDump[x]
  species = dataEntry["Species"]

  #species index
  uraniumdex[species] = {
    "Indices": {
      FORMATNAME: int(x)
    }
  }
  dexEntry = uraniumdex[species]

  #default ability slots
  defslots = []
  validSlots = dataEntry["Valid Slots"]
  for s in range(0, max(validSlots)+1):
    if s in validSlots:
      defslots.append(getAbility(dataEntry["Abilities at Slots"][validSlots.index(s)]))
    else:
      defslots.append(None)
  dexEntry["Ability Slots"] = {
    "pkeUranium": defslots
  }

  ## Forms
  dataEntryForms = dataEntry["Form Names"]
  forms = {}
  first = True
  for form in dataEntryForms:
    #ensure this is a cannonical form
    if form == None or form in appToBaseForm:
      continue

    formindex = dataEntryForms.index(form)
    cannonName = renameForm(form)
    forms[cannonName] = {
      "Form Indices": {
        "pkeUranium": formindex
      },
      "Exists in": [FORMATNAME]
    }

    #add ability slots if they differ from default
    rawSlots = dataEntry["Alt Form Abilities"][formindex]
    if rawSlots is not None:
      #ensure form ability overrides ALL abilities
      if rawSlots.count(rawSlots[0]) != len(rawSlots):
        raise Exception(f"{species}'s form '{form}' has non-identical abil slots...")

      formSlots = []
      for i in range(0, len(defslots)):
        formSlots.append(None if defslots[i] is None else getAbility(rawSlots[i]))
      forms[cannonName]["Ability Slots"] = formSlots

    #in-battle transformation for megas
    if form in baseToMega and baseToMega[form] in dataEntryForms: #this form has a mega
      cannonMegaName = renameForm(baseToMega[form])
      forms[cannonName]["In-Battle Form Changes"] = {
        cannonMegaName: {
            "Type": "Mega",
          }
      }
      stone = None if dataEntry["Mega Stone"] is None else getItem(dataEntry["Mega Stone"])
      if stone is not None:
        forms[cannonName]["In-Battle Form Changes"][cannonMegaName]["Item"] = stone

    #first form is default
    if first:
      if cannonName != "":
        dexEntry["Default Form"] = cannonName
      first = False

  ## Appearances
  for app in dataEntryForms:
    #ensure this is a appearance form
    if app == None or app not in appToBaseForm:
      continue

    # if app == "Halloween Mega" and species == "Baariette":
    #   print("skipped")
    #   continue

    baseForm = appToBaseForm[app]
    cannonName = renameForm(app)
    appindex = dataEntryForms.index(app)
    forms[baseForm]["Appearance"] = {
      cannonName: {
        "Form Indices": {
          "pkeUranium": appindex
        }
      }
    }

    #add ability slots if they differ from form/default slots
    rawSlots = dataEntry["Alt Form Abilities"][appindex]
    if rawSlots is not None:
      #ensure app ability overrides ALL abilities
      if rawSlots.count(rawSlots[0]) != len(rawSlots):
        raise Exception(f"{species}'s app '{form}' has non-identical abil slots...")

      formSlots = forms[baseForm]["Ability Slots"] if "Ability Slots" in forms[baseForm] else None
      appSlots = []
      for i in range(0, len(defslots)):
        appSlots.append(None if defslots[i] is None else getAbility(rawSlots[i]))

      if formSlots is None and appSlots != defslots or appSlots != formSlots:
        forms[baseForm]["Appearance"][cannonName]["Ability Slots"] = appSlots

  dexEntry["Forms"] = forms


  #gender ratio
  dexEntry["Gender Ratio"] = gender[dataEntry["Gender Byte"]]

  #growth rate
  dexEntry["Growth Rate"] = growth[dataEntry["Growth Rate"]]

  #alt languages
  nameEntry = {}
  for lang in languages:
    nameEntry[lang] = langDict[lang][x]["Species"]
  dexEntry["Names"] = nameEntry


# merging complete, write file
with open(os.path.join(root, f"{FORMATNAME}SpeciesDex.json"), 'w', encoding='utf-8') as f:
  f.write(to_json(uraniumdex))
    
print("\nSpeciesDex Outputted!")