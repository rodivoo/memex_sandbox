import os, shutil
import re

#############################
# STORING FUNCTIONS #########
#############################

# generates path from bibtex code:
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    return(directory)

# load bibTex Data into a dictionary
def loadBib(bibTexFile):
    bibDic = {}
    #recordsNeedFixing = []
    with open(bibTexFile, "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower():
                completeRecord = "\n@" + record

                record = record.strip().split("\n")[:-1]

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord

                for r in record[1:]:
                    key = r.split("=")[0].strip()
                    val = r.split("=")[1].strip()
                    val = re.sub(r"\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # fix the path to PDF
                    if key == "file":
                        if ";" in val:
                            temp = val.split(";")
                            for t in temp:
                                if ".pdf" in t:
                                    val = t

                            bibDic[rCite][key] = val

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"])
        with open(bibFilePath, "w", encoding="utf8") as f9:
            f9.write(bibRecDict["complete"])

        pdfFileSRC = bibRecDict["file"]
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"])
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST)

def loadYmlSettings(ymlFile):
    with open(ymlFile, "r", encoding="utf8") as f1:
        data = f1.read()
        data = re.sub(r"#.*", "", data) # remove comments
        data = re.sub(r"\n+", "\n", data) # remove extra linebreaks used for readability
        data = re.split(r"\n(?=\w)", data) # splitting
        dic = {}
        for d in data:
            if ":" in d:
                d = re.sub(r"\s+", " ", d.strip())
                d = re.split(r"^([^:]+) *:", d)[1:]
                key = d[0].strip()
                value = d[1].strip()
                dic[key] = value
    return(dic)

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
    
def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)

def prettifyBib(bibText):
    bibText = bibText.replace("{{", "").replace("}}", "")
    bibText = re.sub(r"\n\s+file = [^\n]+", "", bibText)
    bibText = re.sub(r"\n\s+abstract = [^\n]+", "", bibText)
    return(bibText)