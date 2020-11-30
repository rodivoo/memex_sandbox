import os, shutil
import yaml
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

bibAll = settings["bib_all"]
pathToMemex = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = functions.generatePublPath(pathToMemex, bibRecDict["rCite"])

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


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData):
    for k,v in bibData.items():
        processBibRecord(pathToMemex, v)

bibData = functions.loadBib(bibAll)
processAllRecords(bibData)

print("Done!")