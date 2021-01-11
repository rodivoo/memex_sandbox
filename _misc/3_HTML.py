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

    # replace file extension 
    jsonFile = pathToBibFile.replace(".bib", ".json")

    # open json file
    with open(jsonFile) as jsonData:
        # save the content from the json file to ocred (string)
        ocred = json.load(jsonData)
        # save page numbers to pNums
        pNums = ocred.keys()

        # call the function generatePageLinks with pNums as input value and save the return value to pageDic
        pageDic = functions.generatePageLinks(pNums)

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read()

        # load individual bib record
        bibFile = pathToBibFile
        # call the function loadBib with bibFile as input value and save the return value to bibDic
        bibDic = functions.loadBib(bibFile)
        # call the function prettifyBib with bibDic[citeKey]["complete"] as input value and save the return value to bibForHTML
        bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])

        # create a list with the keys oft the dictionary pageDic and save it to orderedPages
        orderedPages = list(pageDic.keys())

        # loop: start = 0; end = number of elements in the list orderedPages
        for o in range(0, len(orderedPages)):
            #print(o)
            k = orderedPages[o]
            v = pageDic[orderedPages[o]]

            # save template to pageTemp
            pageTemp = template
            # replace @MAINCONTENT@ with v
            pageTemp = pageTemp.replace("@PAGELINKS@", v)
            # replace @PATHTOFILE@ with ""
            pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            # replace @CITATIONKEY@ with citeKey
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)

            if k != "DETAILS": # normal page
                # png: replace @PAGEFILE@ with name of the image
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k)
                # replace @MAINELEMENT@ with mainElement
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                # replace @OCREDCONTENT@ with the ocred text (replace "\n" by "<br>")
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>"))
            else: # detail page
                # save the detail text (bib file) to mainElement
                mainElement = bibForHTML.replace("\n", "<br> ")
                # add html to detail text
                mainElement = '<div class="bib">%s</div>' % mainElement
                # add image workcloud
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">'
                # replace @MAINELEMENT@ with mainElement
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
                # replace @OCREDCONTENT@ with ""
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "")

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            # detail page
            if k == "DETAILS":
                nextPage = "0001.html"
                # no previous page
                prevPage = ""
            # first page of publication
            elif k == "0001":
                nextPage = "0002.html"
                # previous page = detail page
                prevPage = "DETAILS.html"
            # last page of publication
            elif o == len(orderedPages)-1:
                # no next page
                nextPage = ""
                # prevPage: page - 1
                prevPage = orderedPages[o-1] + ".html"
            # "normal" page of publication
            else:
                # nextPage: page + 1
                nextPage = orderedPages[o+1] + ".html"
                # prevPage: page - 1
                prevPage = orderedPages[o-1] + ".html"

            # replace @NEXTPAGEHTML@ with nextPage
            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage)
            # replace @PREVIOUSPAGEHTML@ with prevPage
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage)

            # path to html pages
            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k)
            # create html pages
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp)

def generateIndexPage():
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read()

    # load index content
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        content = f1.read()

    # save template to pageTemp
    pageTemp = template 
    # replace @MAINCONTENT@ with content
    pageTemp = pageTemp.replace("@MAINCONTENT@", content)

    # path to index.html
    directory = os.path.join(memexPath, "index.html")
    # create the file index.html
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

def generateContentsPage():
    # load contents template
    with open(settings["template_contents"], "r", encoding="utf8") as ft:
        template = ft.read()

    # call the function dicOfRelevantFiles with memexPath as input value and save the return value to relDic
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    # create the list linkList
    linkList = []

    # loop through all items of the dictionry relDic
    for k,v in relDic.items():
        # removing the last character
        k = k[:-1]
        # call the function loadBib with v as input value and save the return value to bibDic
        bibDic = functions.loadBib(v)
        # append an item (link) to the list linkList
        linkList.append("<a href=\"{0}/pages/DETAILS.html\">[{1}]</a> {2} ({3}) - <i>{4}</i>".format(
            os.path.join(k[0], k[:2], k),
            k,
            bibDic[k]["author"],
            bibDic[k]["date"],
            bibDic[k]["title"]))
    # sort the list linkList
    linkListSorted = sorted(linkList)
    # join items of linkListSorted by </li><li> and store in a sting 
    linkList = "</li><li>".join(linkListSorted)

    # save template to pageTemp
    pageTemp = template
    # replace @MAINCONTENT@ with linkList and save it to pageTemp
    pageTemp = pageTemp.replace("@MAINCONTENT@", linkList)

    # path to contents.html
    directory = os.path.join(memexPath, "contents.html")
    # create the file contents.html
    with open(directory, "w", encoding="utf8") as f2:
        f2.write(pageTemp)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords():
    # call the function dicOfRelevantFiles with memexPath as input value and save the return value to relDic
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    # loop through all items of the dictionry relDic
    for k,v in relDic.items():
        # call the function generatePublicationInterface with k (removing the last character) and v as input values
        generatePublicationInterface(k[:-1], v)

# call the function processAllRecords
processAllRecords()
# call the function generateIndexPage
generateIndexPage()
# call the function generateContentsPage
generateContentsPage()