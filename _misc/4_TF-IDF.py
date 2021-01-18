import functions
import json
import re
import os
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# dict with all ocred json files
ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
# list with all citekyes
citeKeys = list(ocrFiles.keys())

# new list
docList   = []
# new list
docIdList = []

# new dict
corpusDic = {}

# loop through all items of the list citeKeys
for citeKey in citeKeys:
    # load the content of the ocred json files and save it to docData
    docData = json.load(open(ocrFiles[citeKey]))
    
    # save citeKey to docId
    docId = citeKey
    # joins values of docData to the string doc
    doc   = " ".join(docData.values())

    doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc) # undo hyphenation (bla-bla => blabla)
    doc = re.sub('\W+', ' ', doc) # replace the sign after a word (e.g. linebreak) with a space
    doc = re.sub('\d+', ' ', doc) # replace numbers with a space
    doc = re.sub(' +', ' ', doc) # replace multiple spaces with one space

    # adds the elements to the list docList
    docList.append(doc)
    # adds the elements to the list docIdList
    docIdList.append(docId)

vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5)
countVectorized = vectorizer.fit_transform(docList)
tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
vectorized = tfidfTransformer.fit_transform(countVectorized) # https://en.wikipedia.org/wiki/Sparse_matrix
cosineMatrix = cosine_similarity(vectorized)

# create tfidfTableDic
tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
print("tfidfTable Shape: ", tfidfTable.shape) # optional
tfidfTable = tfidfTable.transpose()
tfidfTableDic = tfidfTable.to_dict()

# create cosineTableDic
cosineTable = pd.DataFrame(cosineMatrix)
print("cosineTable Shape: ", cosineTable.shape) # optional
cosineTable.columns = docIdList
cosineTable.index = docIdList
cosineTableDic = cosineTable.to_dict()

###########################################################
# GENERATE JSON FILES ###############################################
###########################################################

def filterDic(tableDic, limit):
    # create new dict
    newDic = {}
    # loop through all items of the dictionry tableDic
    for k, v in tableDic.items():
        # create new sub dict
        newDic[k] = {}
        # loop through all values
        for key in v:
            # check the threshold
            if limit <= v[key] < 0.99:
                # add entry to the new dict newDic
                newDic[k][key] = v[key]
    # retrun the new dict newDic
    return(newDic)

# call the function filterDic with tfidfTableDic and threshold as input values
tfidfTableDic = filterDic(tfidfTableDic, 0.05)
# path to tf-idf_terms.txt
directory = os.path.join(memexPath, "tf-idf_terms.txt")
# create the file tf-idf_terms.txt
with open(directory, 'w', encoding='utf8') as f1:
     json.dump(tfidfTableDic, f1, sort_keys=True, indent=4, ensure_ascii=False)

# call the function filterDic with cosineTableDic and threshold as input values
cosineTableDic = filterDic(cosineTableDic, 0.25)
# path to tf-idf_distances.txt
directory = os.path.join(memexPath, "tf-idf_distances.txt")
# create the file tf-idf_distances.txt
with open(directory, 'w', encoding='utf8') as f2:
     json.dump(cosineTableDic, f2, sort_keys=True, indent=4, ensure_ascii=False)