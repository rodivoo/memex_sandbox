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
            result = re.findall(searchString, v)
            if result:
                subResultDic[k] = {}
                subResultDic[k]["matches"] = len(result)
                subResultDic[k]["pathToPage"] = os.path.join(citeKey[0], citeKey[:2], citeKey, "pages", k + ".html")
                doc = re.sub(searchString, "<span class='searchResult'>" + searchString + "</span>", v)
                # doc = doc.replace("\n", "<br>")
                subResultDic[k]["result"] = doc
                count = count + len(result)
                
        key = "{:08d}".format(count) + "::::" + citeKey
        resultDic[key] = {}
        resultDic[key] = subResultDic
        
        if resultDic[key] == {}:
            resultDic.pop(key)

    resultDic = dict(sorted(resultDic.items(), reverse=True))

    resultDic["searchString"] = searchString
    resultDic["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S)")

    return(resultDic)

def createSearchResultPage(searchDic, searchString):

    with open(settings["template_search"], "r", encoding="utf8") as ft:
        template = ft.read()

    searchPath = os.path.join(memexPath, "search")

    if not os.path.exists(searchPath):
        os.makedirs(searchPath)

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

    directory = os.path.join(memexPath, "search", searchString + ".html")
    with open(directory, "w", encoding="utf8") as f9:
        f9.write(template.replace("@MAINCONTENT@", mainContent))

###########################################################
# GENERATE SEARCH ###############################################
###########################################################

searchQuery = "bread"
#searchQuery = "price"
#searchQuery = "speculators"

resultDic = createSearchResultDic(searchQuery)

createSearchResultPage(resultDic, searchQuery)