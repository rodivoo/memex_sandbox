import functions
import os
import json

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

bibAll = settings["bib_all"]
memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile):
    print("="*80)
    print(citeKey)

    jsonFile = pathToBibFile.replace(".bib", ".json")
    with open(jsonFile) as jsonData:
        ocred = json.load(jsonData)
        pNums = ocred.keys()

        pageDic = functions.generatePageLinks(pNums)

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # load individual bib record
        bibFile = pathToBibFile
        bibDic = functions.loadBib(bibFile)
        bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])

        orderedPages = list(pageDic.keys())

        for o in range(0, len(orderedPages)):
            #print(o)
            k = orderedPages[o]
            v = pageDic[orderedPages[o]]

            pageTemp = template
            pageTemp = pageTemp.replace("@PAGELINKS@", v)
            pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)

            if k != "DETAILS":
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k)
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>"))
            else:
                mainElement = bibForHTML.replace("\n", "<br> ")
                mainElement = '<div class="bib">%s</div>' % mainElement
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">'
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "")

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

def dicOfRelevantFiles(pathToMemex, extension):
    dic = {}
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication tf data
            if file.endswith(extension):
                key = file.replace(extension, "")
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)

def generateIndexPage():
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    # load index content
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        content = f1.read()

    pageTemp = template
    pageTemp = pageTemp.replace("@MAINCONTENT@", content)

    directory = os.path.join(memexPath, "index.html")
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

def generateContentsPage():
    # load contents template
    with open(settings["template_contents"], "r", encoding="utf8") as ft:
        template = ft.read()

    relDic = dicOfRelevantFiles(memexPath, "bib")
    linkList = []

    for k,v in relDic.items():
        k = k[:-1]
        bibDic = functions.loadBib(v)
        linkList.append("<a href=\"{0}/pages/DETAILS.html\">[{1}]</a> {2} ({3}) - <i>{4}</i>".format(
            os.path.join(k[0], k[:2], k),
            k,
            bibDic[k]["author"],
            bibDic[k]["date"],
            bibDic[k]["title"]))

    linkListSorted = sorted(linkList)
    linkList = "</li><li>".join(linkListSorted)

    pageTemp = template
    pageTemp = pageTemp.replace("@MAINCONTENT@", linkList)

    directory = os.path.join(memexPath, "contents.html")
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords():
    relDic = dicOfRelevantFiles(memexPath, "bib")
    for k,v in relDic.items():
        generatePublicationInterface(k[:-1], v)

processAllRecords()
generateIndexPage()
generateContentsPage()