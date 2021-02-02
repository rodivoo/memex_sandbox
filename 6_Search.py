import functions
import json
import re
import os
from datetime import datetime

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

def serachOCR(memexPath, searchString):
    ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
    citeKeys = sorted(list(ocrFiles.keys()))

    resultDic = {}

    for citeKey in citeKeys:
        docData = json.load(open(ocrFiles[citeKey]))
        count = 0
        subResultDic = {}
        for k, v in docData.items():
            if re.search(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE):
                subResultDic[k] = {}
                subResultDic[k]["matches"] = len(re.findall(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE))
                subResultDic[k]["pathToPage"] = os.path.join(citeKey[0], citeKey[:2], citeKey, "pages", k + ".html")
                doc = re.sub(r"\b({0})\b".format(searchString), r"<span class='searchResult'>\1</span>", v, flags=re.IGNORECASE)
                # doc = doc.replace("\n", "<br>")
                subResultDic[k]["result"] = doc
                #count = count + len(re.findall(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE))
                count += 1
                
        key = "{:08d}".format(count) + "::::" + citeKey
        resultDic[key] = {}
        resultDic[key] = subResultDic
        
        if resultDic[key] == {}:
            resultDic.pop(key)

    resultDic = dict(sorted(resultDic.items(), reverse=True))

    resultDic["searchString"] = searchString
    resultDic["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saveWith = re.sub(r"\W+", "", searchString)
    saveTo = os.path.join(memexPath, "search", "{0}.searchResults".format(saveWith))
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(resultDic, f9c, sort_keys=True, indent=4, ensure_ascii=False)

###########################################################
# GENERATE SEARCH ###############################################
###########################################################

#searchQuery = r"bread"
#searchQuery  = r"sixteenth\W*century"
#searchQuery  = r"sixteenth-?century"
#searchQuery = r"price"
#searchQuery  = r"modi\W*fications"
#searchQuery = r"plague"
searchQuery = r"balkan"

serachOCR(memexPath, searchQuery)

exec(open("7_IndexPage.py").read())