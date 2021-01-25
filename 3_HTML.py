import functions
import os
import json
import re 

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
def generatePublicationInterface(citeKey, pathToBibFile, cosDistance):
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
                mainElement = '<img src="{}.png" width="100%" alt="">'.format(k)
                mainElement += '<button class="collapsible">Ocred Text</button><div class="content"><div class="bib">{}</div></div>'.format(
                    ocred[k].replace("\n", "<br>")
                )
                
            else:
                mainElement = '<h2>{0} ({1}). {2}</h2>'.format(
                    bibDic[citeKey]["author"],
                    bibDic[citeKey]["date"],
                    bibDic[citeKey]["title"]
                )
                mainElement += '<button class="collapsible">BibTeX Bibliographical Record</button><div class="content"><div class="bib">{}</div></div>'.format(
                    bibForHTML.replace("\n", "<br> ")
                )
                mainElement += '<button class="collapsible">WordCloud of Keywords (tf-idf)</button><div class="content"><img src="wordcloud.jpg" width="100%" alt="wordcloud"></div>'

            mainElement += '<button class="collapsible">Similar Texts (tf-idf + cosine similarity)</button><div class="content"><table id="publications" class="mainList" width="100%"><thead><tr><th>SIM</th><th>citeKey, author, date, title</th></tr></thead><tbody>'
            mainElement += generateSimilarList(cosDistance)
            mainElement += '</tbody></table></div>'

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

def generateSimilarList(cosDic):
    similarList = []

    for k, v in cosDic.items():
        filePath = os.path.join(functions.generatePublPath(memexPath, k), k + ".bib")
        bibDic = functions.loadBib(filePath)
        similarList.append("<tr><td>{5:.5f}</td><td><div class=\"ID\"><a href=\"../../../../{0}/pages/DETAILS.html\">[{1}]</a></div> {2} ({3}) <i>{4}</i></td></tr>".format(
            os.path.join(k[0], k[:2], k),
            k,
            bibDic[k]["author"],
            bibDic[k]["date"],
            bibDic[k]["title"],
            v)
        )
        
    similarListSorted = sorted(similarList, reverse=False)
    similarList = "".join(similarListSorted)

    return(similarList)

""" def generateContentsPage():
    # load contents template
    with open(settings["template_contents"], "r", encoding="utf8") as ft:
        template = ft.read()

    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
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
        f2.write(pageTemp) """

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords():
    relDic = functions.dicOfRelevantFiles(memexPath, "bib")
    # load "tf-idf_distances.dataJson"
    distDataPath = os.path.join(memexPath, "tf-idf_distances.dataJson")
    distData = json.load(open(distDataPath))
    for k,v in relDic.items():
        generatePublicationInterface(k[:-1], v, distData[k[:-1]])

processAllRecords()
#generateContentsPage()

exec(open("7_IndexPage.py").read())
