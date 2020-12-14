# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml"
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"]
langKeys = yaml.load(open(settings["language_keys"]))

###########################################################
# TRICKY FUNCTIONS ########################################
###########################################################

# the function creates a temporary copy of a PDF file
# with comments and highlights removed from it; it creates
# a clean copy of a PDF suitable for OCR-nig 
def removeCommentsFromPDF(pathToPdf):
    # open the pdf file
    with open(pathToPdf, 'rb') as pdf_obj:
        # read the pdf file 
        pdf = PyPDF2.PdfFileReader(pdf_obj)
        # create a new PdfFileWriter instance and store it
        out = PyPDF2.PdfFileWriter()
        # loop through each page of the pdf file
        for page in pdf.pages:
            # add a new page to out
            out.addPage(page)
            # remove links and annotations
            out.removeLinks()
        # change the file name
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf")
        # create the temporary pdf file
        with open(tempPDF, 'wb') as f: 
            # write out to the file
            out.write(f)
    # return the path form the new pdf file
    return(tempPDF)

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language):
    # generate and create necessary paths
    # path to the folder
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    # path to the pdf file
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    # path to the json file
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    # path to the pages folder
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # generate CLEAN pdf (necessary if you added highlights and comments to your PDFs)
    pdfFileTemp = removeCommentsFromPDF(pdfFile)

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            # create folder pages
            os.makedirs(saveToPath)
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)

        # create the dictionary textResults
        textResults = {}
        # create the list images 
        images = pdf2image.convert_from_path(pdfFileTemp)
        # length of the list
        pageTotal = len(images)
        # set pageCount
        pageCount = 1
        # loop through the list images
        for image in images:
            image = image.convert('1') # binarizes image, reducing its size
            # create the path for each image file
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            # save the image
            image.save(finalPath, optimize=True, quality=10)

            # get the text from the image
            text = pytesseract.image_to_string(image, lang=language)
            # save the text to the dictionary textResults
            textResults["%04d" % pageCount] = text

            # write the process to terminal
            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            # increase pageCount
            pageCount += 1

        # create the json file
        with open(jsonFile, 'w', encoding='utf8') as f9:
            # write textResults to the file
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)

    # delete the temporary pdf file
    os.remove(pdfFileTemp)

def identifyLanguage(bibRecDict, fallBackLanguage):
    # check if "langid" is present in bibRecDict
    if "langid" in bibRecDict:
        try:
            # save the corresponding value from bibtex_languages.yml to language
            language = langKeys[bibRecDict["langid"]]
            message = "\t>> Language has been successfuly identified: %s" % language
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage
            # save the fallBackLanguage to language
            language = fallBackLanguage
    else:
        message = "\t>> No data on the language of the publication"
        message += "\t>> For now, trying `%s`..." % fallBackLanguage
        # save the fallBackLanguage to language
        language = fallBackLanguage
    # print the message to the terminal
    print(message)
    # return the string language
    return(language)

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#ocrPublication("AbdurasulovMaking2020", "eng")

###########################################################
# PROCESS ALL RECORDS: APPROACH 1 #########################
###########################################################

"""

def processAllRecords(bibData):
    for k,v in bibData.items():
        # 1. create folders, copy files
        functions.processBibRecord(memexPath, v)

        # 2. OCR the file
        language = identifyLanguage(v, "eng")
        ocrPublication(memexPath, v["rCite"], language)

bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)

"""

###########################################################
# PROCESS ALL RECORDS: APPROACH 2 #########################
###########################################################

# Why this way? Our computers are now quite powerful; they
# often have multiple cores and we can take advantage of this;
# if we process our data in the manner coded below --- we shuffle
# our publications and process them in random order --- we can
# run multiple instances fo the same script and data will
# be produced in parallel. You can run as many instances as
# your machine allows (you need to check how many cores
# your machine has). Even running two scripts will cut
# processing time roughly in half.

def processAllRecords(bibData):
    # save the keys from the dictionary bibData to the list keys
    keys = list(bibData.keys())
    # pick random element from the shuffled list keys
    random.shuffle(keys)

    # loop through each key from the list keys
    for key in keys:
        # save the bibData record to bibRecord
        bibRecord = bibData[key]

        # 1. create folders, copy files
        # call the function processBibRecord with the memexPath and the bibRecord as input values
        functions.processBibRecord(memexPath, bibRecord)

        # 2. OCR the file
        # call the function identifyLanguage with the bibRecord and the fallBackLanguage as input values and save the return value to language
        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(memexPath, bibRecord["rCite"], language)


# call the function loadBib with the filename as input value and save the return value to bibData
bibData = functions.loadBib(settings["bib_all"])
# call the function processAllRecords with bibData as input value
processAllRecords(bibData)

# record to regenerate: RossabiReview2011