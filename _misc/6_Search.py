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

# create resultDic
def createSearchResultDic(searchString):
    # create dict with all json files
    ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
    # create dict with all keys of ocrFiles
    citeKeys = sorted(list(ocrFiles.keys()))

    # create dict resultDic
    resultDic = {}

    # loop through the dict citeKeys
    for citeKey in citeKeys:
        # open the json file and store it to the dict docData
        docData = json.load(open(ocrFiles[citeKey]))
        # variable for the number of matches per publication 
        count = 0
        # create the dict subResultDic
        subResultDic = {}
        # loop through all pages of the dict docData
        for k, v in docData.items():
            # check if serach resluts exists
            if re.search(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE):
                # create the dict subResultDic[k] (k=page)
                subResultDic[k] = {}
                # store the number of matches on a page
                subResultDic[k]["matches"] = len(re.findall(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE))
                # store the page path
                subResultDic[k]["pathToPage"] = os.path.join(citeKey[0], citeKey[:2], citeKey, "pages", k + ".html")
                # mark the matches with html
                doc = re.sub(r"\b({0})\b".format(searchString), r"<span class='searchResult'>\1</span>", v, flags=re.IGNORECASE)
                # doc = doc.replace("\n", "<br>")
                # store the marked content of the page
                subResultDic[k]["result"] = doc
                # count the matches of the publication
                count = count + len(re.findall(r"\b{0}\b".format(searchString), v, flags=re.IGNORECASE))

        # add the number of matches per publication to the citeKey (e.g. 00000008::::allenTrackingAgriculturalRevolution199)  
        key = "{:08d}".format(count) + "::::" + citeKey
        # create dict resultDic[key]
        resultDic[key] = {}
        # add the subResultDic to the dict
        resultDic[key] = subResultDic
        
        # remove dict if enpty
        if resultDic[key] == {}:
            resultDic.pop(key)

    # sort the dict
    resultDic = dict(sorted(resultDic.items(), reverse=True))

    # add the searchstring to the dict
    resultDic["searchString"] = searchString
    # add the timestamp to the dict
    resultDic["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # file name: remove non alphanumeric characters from searchString
    saveWith = re.sub(r"\W+", "", searchString)
    # create the path to the file (folder: search; extension: .searchResults)
    saveTo = os.path.join(memexPath, "search", "{0}.searchResults".format(saveWith))
    # create the json file with resultDic as content
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(resultDic, f9c, sort_keys=True, indent=4, ensure_ascii=False)

    # return resultDic
    return(resultDic)

# create search result html page
def createSearchResultPage(searchDic):

    # open the search template
    with open(settings["template_search"], "r", encoding="utf8") as ft:
        template = ft.read()

    # template of the button
    buttonItemTemplate = '<button class="collapsible"><b>@CITATIONKEY@</b> (pages with results: @PAGEWITHRESULTS@, total results: @TOTALRESULTS@)</button>'
    # template of the search result page
    listItemTemplate = '<li><hr><b>(pdfPage: @PAGENUMBER@)</b><hr>@PAGECONTENT@<hr> <a href="../@PAGELINK@"><i>go to the original page...</i></a></li>'
    # create list contentsList
    contentsList = []

    # create variable searchString 
    searchString = searchDic["searchString"]
    # remove timestamp from dict
    searchDic.pop("timestamp")
    # remove timestamp from dict
    searchDic.pop("searchString")

    # loop through dict searchDic
    for citekey, pages in searchDic.items():
        # save the template of the button to recordToAdd
        recordToAdd = buttonItemTemplate
        # replace @CITATIONKEY@ with the citekey
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", re.sub(r'(^0+)(\d+)::::(\w+)', r'\3', citekey))
        # replace @PAGEWITHRESULTS@ with the number of pages with result
        recordToAdd = recordToAdd.replace("@PAGEWITHRESULTS@", str(len(pages)))
        # replace @TOTALRESULTS@ with the total number of search results
        recordToAdd = recordToAdd.replace("@TOTALRESULTS@", re.sub(r'(^0+)(\d+)::::(\w+)', r'\2', citekey))

        # create list linkList
        linkList = []
        # loop through the sub dict pages
        for page, results in pages.items():
            # save the template of the search result page to itemToAdd
            itemToAdd = listItemTemplate
            # replace @PAGENUMBER@ with the number of the page
            itemToAdd = itemToAdd.replace("@PAGENUMBER@", page)
            # replace @PAGECONTENT@ with the content oft the page
            itemToAdd = itemToAdd.replace("@PAGECONTENT@", results["result"])
            # replace @PAGELINK@ with the path to the page
            itemToAdd = itemToAdd.replace("@PAGELINK@", results["pathToPage"])
            # append itemToAdd to the list linkList
            linkList.append(itemToAdd)
            
        # join all elements of linkList to the string listContent
        listContent = "\n<div class='content'>\n<ul>\n%s\n</ul>\n</div>" % "\n".join(linkList)
        # concatenate the strings recordToAdd and listContent
        recordToAdd = recordToAdd + listContent
        # append the new string to the list contentsList
        contentsList.append(recordToAdd)

    # join all elements of contentsList to the string contents
    contents = "".join(contentsList)
    # concatenate the headline of the html page with contents
    mainContent = "<h1>SEARCH RESULTS FOR: <i><div class='searchString'>" + searchString + "</div></i></h1>\n\n" + contents

    # file name: remove non alphanumeric characters from searchString
    saveWith = re.sub(r"\W+", "", searchString)
    # create the path to the html page
    directory = os.path.join(memexPath, "search", saveWith + ".html")
    # create the html file with mainContent as content
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

# call function createSearchResultDic with the searchQuery as input value
resultDic = createSearchResultDic(searchQuery)
# call function createSearchResultPage with the resultDic as input value
createSearchResultPage(resultDic)

# execute the file 7_IndexPage.py (create index page)
exec(open("7_IndexPage.py").read())