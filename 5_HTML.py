import functions
import os
import json
import re 
import math
import unicodedata
 
###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

bibAll = settings["bib_all"]
memexPath = settings["path_to_memex"]

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

connectionsTemplate = """
<button class="collapsible">Similar Texts (<i>tf-idf</i> + cosine similarity)</button>

  <div class="content">
  <ul>
    <li>
    <b>Sim*</b>: <i>cosine similarity</i>; 1 is a complete match, 0 — nothing similar;
    cosine similarity is calculated using <i>tf-idf</i> values of top keywords.</li>
  </ul>
  </div>


<table id="publications" class="mainList">

<thead>
    <tr>
        <th>citeKey, Author(s), Year, Title, (Pages)</th>
        <th>Sim*</th>
    </tr>
</thead>

<tbody>
@CONNECTEDTEXTSTEMP@
</tbody>

</table>

"""

ocrTemplate = """
<button class="collapsible">Ocred Text</button>
<div class="content">
  <div class="bib">
  @OCREDCONTENTTEMP@
  </div>
</div>
"""

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">
@ELEMENTCONTENT@
</div>
"""

###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

# a function for grouping pages into clusters of y number of pages
# x = number to round up; y = a multiple of the round-up-to number
def roundUp(x, y):
    result = int(math.ceil(x / y)) * y
    return(result)

def checkPageNumbers(bib, bibTexCode, startPage):
    page = 0
    if "pages" in bib.keys(): 
        bibPages = functions.prettifyBib(bib["pages"])
        bibPagesList = list(bibPages.split("--"))
        bibPagesList = [int(i) for i in bibPagesList]

        pathToPubl = functions.generatePublPath(memexPath, bibTexCode)
        jsonFile = os.path.join(pathToPubl, "%s.json" % bibTexCode)

        with open(jsonFile) as jsonData:
            ocred = json.load(jsonData)
            pNumList = ocred.keys()

        if len(pNumList) > (bibPagesList[1] - bibPagesList[0] + 1):
            if startPage == 1:
                page = "TITLE"
            else:
                page = startPage + bibPagesList[0] - 2
        else:
            page = startPage + bibPagesList[0] - 1
    else:
        page = startPage

    return(page)

# formats individual references to publications
def generateDoclLink(bibTexCode, pageVal, distance):
    pathToPubl = functions.generatePublPath(memexPath, bibTexCode)
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode))
    bib = bib[bibTexCode]

    author = "N.d."
    if "editor" in bib:
        author = bib["editor"]
    if "author" in bib:
        author = bib["author"]

    reference = "%s (%s). <i>%s</i>" % (author, bib["date"][:4], bib["title"])
    search = unicodedata.normalize('NFKD', reference).encode('ascii','ignore')
    search = " <div class='hidden'>%s</div>" % search

    if pageVal == 0: # link to the start of the publication
        htmlLink = os.path.join(pathToPubl.replace(memexPath, "../../../../"), "pages", "DETAILS.html")
        htmlLink = "<a href='{0}'>[{1}]</a>".format(
            htmlLink,
            bibTexCode)
        page = ""
        startPage = 0
    else:
        startPage = pageVal - 5
        endPage   = pageVal
        if startPage == 0:
            startPage += 1

        realStartPage = checkPageNumbers(bib, bibTexCode, startPage)
        realEndPage = checkPageNumbers(bib, bibTexCode, endPage)

        htmlLink = os.path.join(pathToPubl.replace(memexPath, "../../../../"), "pages", "%04d.html" % startPage)
        htmlLink = "<a href='{0}'>[{1},{2}]</a>".format(
            htmlLink,
            bibTexCode,
            realStartPage
        )
        page = ", pp. {0}-{1}</i></a>".format(
            realStartPage,
            realEndPage
        )

    publicationInfo = reference + page + search
    publicationInfo = publicationInfo.replace("{", "").replace("}", "")
    singleItemTemplate = '<tr><td data-order="{1}{2:05d}"><div class="ID">{3}</div> {4}</td><td>{0:f}</td></tr>'.format(
        distance,
        bibTexCode,
        startPage,
        htmlLink,
        publicationInfo)

    return(singleItemTemplate)

def generateReferenceSimple(bibTexCode):
    pathToPubl = functions.generatePublPath(memexPath, bibTexCode)
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode))
    bib = bib[bibTexCode]

    author = "N.d."
    if "editor" in bib:
        author = bib["editor"]
    if "author" in bib:
        author = bib["author"]

    reference = "%s (%s). <i>%s</i>" % (author, bib["date"][:4], bib["title"])
    reference = reference.replace("{", "").replace("}", "")
    return(reference)

# convert json dictionary of connections into HTML format
def formatDistConnections(pathToMemex, distanceFile):
    print("Formatting distances data from `%s`..." % distanceFile)
    distanceFile = os.path.join(pathToMemex, distanceFile)
    distanceDict = json.load(open(distanceFile))

    formattedHTML = {}

    for doc1, doc1Dic in distanceDict.items():
        formattedHTML[doc1] = []
        for doc2, distance in doc1Dic.items():
            doc2 = doc2.split("_")
            if len(doc2) == 1:
                tempVar = generateDoclLink(doc2[0], 0, distance)
            else:
                tempVar = generateDoclLink(doc2[0], int(doc2[1]), distance)

            formattedHTML[doc1].append(tempVar)
    print("\tdone!")
    return(formattedHTML)

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

publConnData = formatDistConnections(memexPath, "tf-idf_distances_publications.dataJson")
pageConnData = formatDistConnections(memexPath, "tf-idf_distances_pages.dataJson")

# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile):
    print("="*80)
    print(citeKey)

    jsonFile = pathToBibFile.replace(".bib", ".json")
    with open(jsonFile) as jsonData:
        ocred = json.load(jsonData)
        pNums = ocred.keys()

        #pageDic = functions.generatePageLinks(pNums)

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # load individual bib record
        bibFile = pathToBibFile
        bibDic = functions.loadBib(bibFile)
        bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])

        if "pages" in bibDic[citeKey].keys(): 
            bibPages = functions.prettifyBib(bibDic[citeKey]["pages"])
            bibPages = list(bibPages.split("--"))
            bibPages = [int(i) for i in bibPages]
        else:
            bibPages = "no"

        pageDic = functions.generatePageLinks(pNums, bibPages)

        orderedPages = list(pageDic.keys())

        for o in range(0, len(orderedPages)):
            #print(o)
            k = orderedPages[o]
            v = pageDic[orderedPages[o]]

            pageTemp = template
            pageTemp = pageTemp.replace("@PAGELINKS@", v)
            if bibPages == "no":
                pageTemp = pageTemp.replace("@PAGELINKSCOMMENT@", "<i>IMPORTANT<br>these numbers do not correspond to the actual page numbers")
            else:
                pageTemp = pageTemp.replace("@PAGELINKSCOMMENT@", "")
            pageTemp = pageTemp.replace("@PAGELINKS@COMMENTS", v)
            pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)

            emptyResults = '<tr><td><i>%s</i></td><td><i>%s</i></td></tr>'

            if k != "DETAILS":
                mainElement = '<img src="{}.png" width="100%" alt="">'.format(k)

                pageKey = citeKey+"_%05d" % roundUp(int(k), 5)
                #print(pageKey)
                if pageKey in pageConnData:
                    formattedResults = "\n".join(pageConnData[pageKey])
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data")

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults)
                mainElement += ocrTemplate.replace("@OCREDCONTENTTEMP@", ocred[k].replace("\n", "<br>"))
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                
            else:
                reference = generateReferenceSimple(citeKey)
                mainElement = "<h2>%s</h2>\n\n" % reference

                bibElement = '<div class="bib">%s</div>' % bibForHTML.replace("\n", "<br> ")
                bibElement = generalTemplate.replace("@ELEMENTCONTENT@", bibElement)
                bibElement = bibElement.replace("@ELEMENTHEADER@", "BibTeX Bibliographical Record")
                mainElement += bibElement + "\n\n"

                wordCloud = '\n<img src="../wordcloud.jpg" width="100%" alt="wordcloud">'
                wordCloud = generalTemplate.replace("@ELEMENTCONTENT@", wordCloud)
                wordCloud = wordCloud.replace("@ELEMENTHEADER@", "WordCloud of Keywords (<i>tf-idf</i>)")
                mainElement += wordCloud + "\n\n"

                if citeKey in publConnData:
                    formattedResults = "\n".join(publConnData[citeKey])
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data")

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults)

                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            if k == "DETAILS":
                nextPage = "0001.html"
                prevPage = ""
            elif k == "0001":
                nextPage = "0002.html"
                prevPage = "DETAILS.html"
            elif o == len(orderedPages)-1:
                nextPage = ""
                prevPage = orderedPages[o-1] + ".html"
            else:
                nextPage = orderedPages[o+1] + ".html"
                prevPage = orderedPages[o-1] + ".html"

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage)
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage)

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k)
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

functions.memexStatusUpdates(memexPath, ".html")

def processAllRecords():
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    for k,v in relDic.items():
        generatePublicationInterface(k[:-1], v)

processAllRecords()

exec(open("7_IndexPage.py").read())
