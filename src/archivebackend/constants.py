import os


maxFileNameLength = 500
descriptionLength = 500
authorLength = 100
titleLength = 200

syncFileFolder = "./static"
localFileBase = lambda classname, suffix:  "local" + classname + ".json"
peersOfPeersFileBase = lambda classname, suffix: "peersAndLocal" + classname + ".json"
maxSyncFileItems = 2000
