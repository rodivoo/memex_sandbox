import os
import PyPDF2
import json
import pdf2image
import pytesseract
import functions
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile))

bibAll = settings["bib_all"]
pathToMemex = settings["path_to_memex"]

germanLangCodes = ["de", "DE", "DEU", "Deutsch", "deutsch", "ger", "GER"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# creates a clean temporary copy of a pdf
def removeCommentsFromPDF(pathToPdf):
    with open(pathToPdf, 'rb') as pdf_obj:
        pdf = PyPDF2.PdfFileReader(pdf_obj)
        out = PyPDF2.PdfFileWriter()
        for page in pdf.pages:
            out.addPage(page)
            out.removeLinks()
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf")
        with open(tempPDF, 'wb') as f: 
            out.write(f)
    return(tempPDF)

# extracts images, OCRs them, collects results into a dictionary, saves OCR results into a JSON file.
def ocrPublication(pathToMemex, citationKey, language):
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json")
    saveToPath = os.path.join(publPath, "pages")

    pdfFileTemp = removeCommentsFromPDF(pdfFile)

    if not os.path.isfile(jsonFile):
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}
        images = pdf2image.convert_from_path(pdfFileTemp)
        pageTotal = len(images)
        pageCount = 1
        for image in images:
            image = image.convert('1')
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            image.save(finalPath, optimize=True, quality=10)

            text = pytesseract.image_to_string(image, lang=language)
            textResults["%04d" % pageCount] = text

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1

        with open(jsonFile, 'w', encoding='utf8') as f9:
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
    else:
        print("\t>>> %s has already been OCR-ed..." % citationKey)

    os.remove(pdfFileTemp)
    
def processOCR(pathToMemex, bibRecDict, tesseractLang):
    citationKey = bibRecDict["rCite"]
    language = "eng" 
    for key in bibRecDict:
        if key == "language":
            if bibRecDict["language"] in tesseractLang:
                language = bibRecDict["language"]
            elif bibRecDict["language"] in germanLangCodes:
                language = "deu"

    ocrPublication(pathToMemex, citationKey, language)

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

with open("tesseract_lang.txt", "r") as f1:
    tesseractLang = []
    for line in f1:
        tesseractLang.append(line.strip())

def processAllRecords(bibData):
    for k,v in bibData.items():
        processOCR(pathToMemex, v, tesseractLang)

bibData = functions.loadBib(bibAll)
processAllRecords(bibData)

