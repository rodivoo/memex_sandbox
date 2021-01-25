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

def createSearchResultDic(searchString):
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
                count = count + len(re.findall(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE))
                
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

    return(resultDic)

def createSearchResultPage(searchDic):

    with open(settings["template_search"], "r", encoding="utf8") as ft:
        template = ft.read()

    buttonItemTemplate = '<button class="collapsible"><b>@CITATIONKEY@</b> (pages with results: @PAGEWITHRESULTS@, total results: @TOTALRESULTS@)</button>'
    listItemTemplate = '<li><hr><b>(pdfPage: @PAGENUMBER@)</b><hr>@PAGECONTENT@<hr> <a href="../@PAGELINK@"><i>go to the original page...</i></a></li>'
    contentsList = []

    searchString = searchDic["searchString"]
    searchDic.pop("timestamp")
    searchDic.pop("searchString")

    for citekey, pages in searchDic.items():
        recordToAdd = buttonItemTemplate
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", re.sub(r'(^0+)(\d+)::::(\w+)', r'\3', citekey))
        recordToAdd = recordToAdd.replace("@PAGEWITHRESULTS@", str(len(pages)))
        recordToAdd = recordToAdd.replace("@TOTALRESULTS@", re.sub(r'(^0+)(\d+)::::(\w+)', r'\2', citekey))

        linkList = []
        for page, results in pages.items():
            itemToAdd = listItemTemplate
            itemToAdd = itemToAdd.replace("@PAGENUMBER@", page)
            itemToAdd = itemToAdd.replace("@PAGECONTENT@", results["result"])
            itemToAdd = itemToAdd.replace("@PAGELINK@", results["pathToPage"])
            linkList.append(itemToAdd)
            
        listContent = "\n<div class='content'>\n<ul>\n%s\n</ul>\n</div>" % "\n".join(linkList)
        recordToAdd = recordToAdd + listContent
        contentsList.append(recordToAdd)

    contents = "".join(contentsList)
    mainContent = "<h1>SEARCH RESULTS FOR: <i><div class='searchString'>" + searchString + "</div></i></h1>\n\n" + contents

    saveWith = re.sub(r"\W+", "", searchString)
    directory = os.path.join(memexPath, "search", saveWith + ".html")
    with open(directory, "w", encoding="utf8") as f9:
        f9.write(template.replace("@MAINCONTENT@", mainContent))

###########################################################
# GENERATE SEARCH ###############################################
###########################################################

#searchQuery = r"bread"
searchQuery  = r"sixteenth\W*century"
#searchQuery  = r"sixteenth-?century"
#searchQuery = r"price"
#searchQuery  = r"modi\W*fications"
#searchQuery = r"plague"

resultDic = createSearchResultDic(searchQuery)
createSearchResultPage(resultDic)

exec(open("7_IndexPage.py").read())