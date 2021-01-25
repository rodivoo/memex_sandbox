import functions
import os
import json
import re 

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

def generateIndexPage():
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    # load index content
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        content = f1.read()

    pageTemp = template

    content += '<button class="collapsible">Saved Searches</button><div class="content"><table id="" class="display mainList" width="100%"><thead><tr><th>search string</th><th># of publications with matches</th><th>time stamp</th></tr></thead><tbody>'
    content += generateSearchList()
    content += '</tbody></table></div>'
    content += '<button class="collapsible-like active">Publications included into Memex</button><table id="publications" class="display mainList" width="100%"><thead><tr><th>citeKey, author, date, title</th></tr></thead><tbody>'
    content += generateContentsList()
    content += '</tbody></table>'

    pageTemp = pageTemp.replace("@MAINCONTENT@", content)

    directory = os.path.join(memexPath, "index.html")
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

def generateSearchList():
    searchFiles = functions.dicOfRelevantFiles(memexPath, "searchResults")
    queryKeys = sorted(list(searchFiles.keys()))
    searchList = []

    for queryKey in queryKeys:
        docData = json.load(open(searchFiles[queryKey]))
        searchList.append("<tr><td><div class=\"searchString\"><a href=\"search/{0}.html\">{1}</a></div></td><td>{2}</td><td>{3}</td></tr>".format(
            re.sub(r"\W+", "", docData["searchString"]),
            docData["searchString"],
            len(docData)-2,
            docData["timestamp"])
        )

    searchListSorted = sorted(searchList)
    searchList = "".join(searchListSorted)

    return(searchList)

def generateContentsList():
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    contentsList = []

    for k,v in relDic.items():
        k = k[:-1]
        bibDic = functions.loadBib(v)
        contentsList.append("<tr><td><div class=\"ID\"><a href=\"{0}/pages/DETAILS.html\">[{1}]</a></div> {2} ({3}) <i>{4}</i></td></tr>".format(
            os.path.join(k[0], k[:2], k),
            k,
            bibDic[k]["author"],
            bibDic[k]["date"],
            bibDic[k]["title"])
        )

    contentsListSorted = sorted(contentsList)
    contentsList = "".join(contentsListSorted)

    return(contentsList)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

generateIndexPage()