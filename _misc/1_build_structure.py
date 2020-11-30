import os, shutil, re
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile):
    # create dictionary bibDic
    bibDic = {}
    # create list recordsNeedFixing
    recordsNeedFixing = []
    # open the file
    with open(bibTexFile, "r", encoding="utf8") as f1:
        # read the file and split the string by "\n@" => list
        records = f1.read().split("\n@")
        # loop through each list item - start with the second one
        for record in records[1:]:
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower():
                # save the the complete record, adding "\n@" at the begining
                completeRecord = "\n@" + record
                # split the string by "\n" - end with the second last => list; remove spaces at the begining and the end
                record = record.strip().split("\n")[:-1]
                # split record[0] by "{" and save the first item (inlcuding remove spaces)
                rType = record[0].split("{")[0].strip()
                # split record[0] by "{" and save the second item (inlcuding remove spaces and replace ",")
                rCite = record[0].split("{")[1].strip().replace(",", "")
                # create nested dictionary rCite in bibDic
                bibDic[rCite] = {}
                # save rCite to the nested dictionary rCite
                bibDic[rCite]["rCite"] = rCite
                # save rType to the nested dictionary rCite
                bibDic[rCite]["rType"] = rType
                # save completeRecord to the nested dictionary rCite
                bibDic[rCite]["complete"] = completeRecord
                # loop through each list item - start with the second one
                for r in record[1:]:
                    # split the string by "=" and save the first item (inlcuding remove spaces)
                    key = r.split("=")[0].strip()
                    # split the string by "=" and save the second item (inlcuding remove spaces)
                    val = r.split("=")[1].strip()
                    # remove { and } form the second item
                    val = re.sub("^\{|\},?", "", val)
                    # save val to bibDic[rCite][key]
                    bibDic[rCite][key] = val
                    # fix the path to PDF
                    if key == "file":
                        # check if ";" is present in val
                        if ";" in val:
                            # if true: split val by ";" and save it => list
                            temp = val.split(";")
                            # loop through each list item
                            for t in temp:
                                # check if ".pdf" is present in t
                                if ".pdf" in t:
                                    # if true: save t to val
                                    val = t
                            # update val to bibDic[rCite][key]
                            bibDic[rCite][key] = val

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    # return dictionary bibDic
    return(bibDic)

# generate path from bibtex code, and create a folder, if does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode):
    # lower caste bibTexCode and save it to temp
    temp = bibTexCode.lower()
    # create the path by joining each path item and save it to directory
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    # return the string directory
    return(directory)

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict):
    # call the function generatePublPath with the memexPath and bibRecDict["rCite"] as input value and save the return value to tempPath
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)
    # check if the path doesn't exist
    if not os.path.exists(tempPath):
        # if true: make directories
        os.makedirs(tempPath)
        # create the path to a single bib file and save it to bibFilePath
        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"])
        # create a single bib file ("rCite.bib")
        with open(bibFilePath, "w", encoding="utf8") as f9:
            # write bibRecDict["complete"] to the file
            f9.write(bibRecDict["complete"])
        # save bibRecDict["file"] (path of the pdf file) to the variable pdfFileSRC
        pdfFileSRC = bibRecDict["file"]
        # create the path to a new pdf file and save it to pdfFileDST
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"])
        # check if a new pdf file doesn't exist
        if not os.path.isfile(pdfFileDST):
            # if true: copy the pdf file to the new destination
            shutil.copyfile(pdfFileSRC, pdfFileDST)


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData):
    # loop through all items of the dictionry bibData
    for k,v in bibData.items():
        # call the function processBibRecord with the memexPath and v as input value
        processBibRecord(memexPath, v)
# call the function loadBib with the filename as input value and save the return value to bibData
bibData = loadBib(settings["bib_all"])
# call the function processAllRecords with bibData as input value
processAllRecords(bibData)

print("Done!")