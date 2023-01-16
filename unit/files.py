import os
from config import Config


def getFileName(path):
    filenames = []
    allfiles = os.listdir(path)
    for filename in allfiles:
        if os.path.splitext(filename)[-1].lower() in Config.EXTENSION_FILTER:
            filenames.append(filename)

    return filenames