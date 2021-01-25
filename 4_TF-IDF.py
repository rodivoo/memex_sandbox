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

ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
citeKeys = list(ocrFiles.keys())

docList   = []
docIdList = []

corpusDic = {}
for citeKey in citeKeys:
    docData = json.load(open(ocrFiles[citeKey]))
    
    docId = citeKey
    doc   = " ".join(docData.values())

    doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc) # undo hyphenation (bla-bla => blabla)
    doc = re.sub('\W+', ' ', doc) # replace the sign after a word (e.g. linebreak) with a space
    doc = re.sub('\d+', ' ', doc) # replace numbers with a space
    doc = re.sub(' +', ' ', doc) # replace multiple spaces with one space

    docList.append(doc)
    docIdList.append(docId)

vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5)
countVectorized = vectorizer.fit_transform(docList)
tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
vectorized = tfidfTransformer.fit_transform(countVectorized) # https://en.wikipedia.org/wiki/Sparse_matrix
cosineMatrix = cosine_similarity(vectorized)

tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
print("tfidfTable Shape: ", tfidfTable.shape) # optional
tfidfTable = tfidfTable.transpose()
tfidfTableDic = tfidfTable.to_dict()

cosineTable = pd.DataFrame(cosineMatrix)
print("cosineTable Shape: ", cosineTable.shape) # optional
cosineTable.columns = docIdList
cosineTable.index = docIdList
cosineTableDic = cosineTable.to_dict()

###########################################################
# GENERATE JSON FILES ###############################################
###########################################################

def filterDic(tableDic, limit):
    newDic = {}
    for k, v in tableDic.items():
        newDic[k] = {}
        for key in v:
            if limit <= v[key] < 0.99:
                newDic[k][key] = v[key]
    return(newDic)

tfidfTableDic = filterDic(tfidfTableDic, 0.05)
directory = os.path.join(memexPath, "tf-idf_terms.dataJson")
with open(directory, 'w', encoding='utf8') as f1:
     json.dump(tfidfTableDic, f1, sort_keys=True, indent=4, ensure_ascii=False)

cosineTableDic = filterDic(cosineTableDic, 0.25)
directory = os.path.join(memexPath, "tf-idf_distances.dataJson")
with open(directory, 'w', encoding='utf8') as f2:
     json.dump(cosineTableDic, f2, sort_keys=True, indent=4, ensure_ascii=False)