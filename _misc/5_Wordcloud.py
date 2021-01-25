import functions
import json
import re
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

memexPath = settings["path_to_memex"]

###########################################################
# FUNCTIONS ###############################################
###########################################################

# create wordcloud images
def createWordCloud(savePath, tfIdfDic):
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                   relative_scaling=0.5, colormap="gray") 
    wc.generate_from_frequencies(tfIdfDic)
    # plotting
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    #plt.show() # this line will show the plot
    plt.savefig(savePath, dpi=200, bbox_inches='tight')

###########################################################
# GENERATE WORDCLOUD ###############################################
###########################################################

# path to the file tf-idf_terms.txt 
directory = os.path.join(memexPath, "tf-idf_terms.txt")
# open the file tf-idf_terms.txt and save it to the dict tfidDic
with open(directory, 'r', encoding='utf8') as f1:
    tfidDic = json.load(f1)

# loop through dict tfidDic
for k, v in tfidDic.items():
    citeKey = k
    # create path to each wordcloud.jpg
    savePath = os.path.join(functions.generatePublPath(memexPath, citeKey), "pages", "wordcloud.jpg")
    # create a new dict
    k = {}
    # add the values of tfidDic to the new dict
    k = v
    # call the function createWordCloud with the path and the dict as input values
    createWordCloud(savePath, k)