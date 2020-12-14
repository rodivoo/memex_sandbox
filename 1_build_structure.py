import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = functions.loadYmlSettings(settingsFile)

bibAll = settings["bib_all"]
memexPath = settings["path_to_memex"]

###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData):
    for k,v in bibData.items():
        functions.processBibRecord(memexPath, v)

bibData = functions.loadBib(bibAll)
processAllRecords(bibData)

print("Done!")