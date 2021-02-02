import functions
import os
import json
import re
import unicodedata

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

memexPath = settings["path_to_memex"]

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">

@ELEMENTCONTENT@

</div>
"""

searchesTemplate = """
<button class="collapsible">Saved Searches</button>
<div class="content">
<table id="" class="display mainList" width="100%">
<thead>
    <tr>
        <th>search string</th>
        <th># of publications with matches</th>
        <th>time stamp</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""

publicationsTemplate = """
<button class="collapsible-like active">Publications included into Memex</button>

<table id="" class="display mainList" width="100%">
<thead>
    <tr>
        <th>citeKey, Author(s), Year, Title</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
"""

###########################################################
# FUNCTIONS ###############################################
###########################################################

def createSearchResultPages():
    with open(settings["template_search"], "r", encoding="utf8") as ft:
        template = ft.read()
    dof = functions.dicOfRelevantFiles(memexPath, ".searchResults")

    for file, pathToFile in dof.items():
        data = json.load(open(pathToFile))
        contentsList = []
        searchString = data["searchString"]
        data.pop("timestamp")
        data.pop("searchString")
        keys = sorted(data.keys(), reverse=True)

        for citekey in keys:
            recordToAdd = generalTemplate
            temp = citekey.split("::::")
            buttonHeader = '<b>{0}</b> (pages with results: {1})'.format(
                temp[1],
                int(temp[0])
            )
            recordToAdd = recordToAdd.replace("@ELEMENTHEADER@", buttonHeader)
            linkList = []
            pages = data[citekey]

            for page, results in pages.items():
                itemToAdd = '<li><hr><b>(pdfPage: {0})</b><hr>{1}<hr> <a href="../{2}"><i>go to the original page...</i></a></li>'.format(
                    page,
                    results["result"],
                    results["pathToPage"]
                )
                linkList.append(itemToAdd)
                
            listContent = "\n<ul>\n%s\n</ul>\n" % "\n".join(linkList)
            recordToAdd = recordToAdd.replace("@ELEMENTCONTENT@", listContent)
            contentsList.append(recordToAdd)

            contents = "".join(contentsList)
            mainContent = "<h1>SEARCH RESULTS FOR: <i><div class='searchString'>" + searchString + "</div></i></h1>\n\n" + contents

            saveWith = re.sub(r"\W+", "", searchString)
            directory = os.path.join(memexPath, "search", saveWith + ".html")
            with open(directory, "w", encoding="utf8") as f9:
                f9.write(template.replace("@MAINCONTENT@", mainContent))

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

    mainElement = searchesTemplate.replace("@TABLECONTENTS@", searchList)

    createSearchResultPages()

    return(mainElement)

def generateContentsList():
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    contentsList = []

    for k,v in relDic.items():
        k = k[:-1]
        bibDic = functions.loadBib(v)

        authorOrEditor = "[No data]"
        if "editor" in bibDic[k]:
            authorOrEditor = bibDic[k]["editor"]
        if "author" in bibDic[k]:
            authorOrEditor = bibDic[k]["author"]

        publication =  "{0} ({1}) <i>{2}</i>".format(
            authorOrEditor,
            bibDic[k]["date"],
            bibDic[k]["title"]
        )
        search = unicodedata.normalize('NFKD', publication).encode('ascii','ignore')
        publication += " <div class=\"hidden\">{0}</div>".format(search)
        contentsList.append("<tr><td><div class=\"ID\"><a href=\"{0}/pages/DETAILS.html\">[{1}]</a></div> {2}</td></tr>".format(
            os.path.join(k[0], k[:2], k),
            k,
            publication
        ))

    contentsListSorted = sorted(contentsList)
    contentsList = "".join(contentsListSorted)
    mainElement = publicationsTemplate.replace("@TABLECONTENTS@", contentsList)
    return(mainElement)

def generateIndexPage():
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()
    # load index content
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        content = f1.read()

    pageTemp = template
    content += generateSearchList()
    content += generateContentsList()
    pageTemp = pageTemp.replace("@MAINCONTENT@", content)

    directory = os.path.join(memexPath, "index.html")
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

generateIndexPage()