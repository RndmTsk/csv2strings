#!/usr/bin/env python

#!/usr/bin/env python

import glob, os, sys, getopt, csv

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:l:o:", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    filename = "localizations.csv"
    baseLang = "en"
    logFile = None
    for opt, arg in opts:
        if opt == "-f":
            filename = arg
        if opt == "-l":
            baseLang = arg
        if opt == "-o":
            logFile = arg

    # Actual program start
    loadCSV(filename, baseLang)

# Functions
def loadCSV(filename, baseLang):
    with open(filename, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="\"")
        (fieldnames, languages) = getFieldnamesAndLanguages(csvfile, reader, baseLang)
        valueStartIdx = len(fieldnames)
        pathColumn = fieldnames.index("path")
        fileColumn = fieldnames.index("file")
        commentColumn = fieldnames.index("comment")
        objectIdColumn = fieldnames.index("object-id")
        if pathColumn == None or fileColumn == None or commentColumn == None or objectIdColumn == None:
            raise Usage(filename + " does not have a valid format, must have columns 'path', 'file', 'comment', 'object-id'")

        lastPath = ""
        lastFile = ""
        values = initializeLocalizedValues(languages) 
        for row in reader:
            path = row[pathColumn]
            file = row[fileColumn]
            objectId = row[objectIdColumn]
            comment = row[commentColumn]

            # We can ignore the lproj part for now
            # We're not using this filename to write the file
            if lastPath == "" and lastFile == "":
                    lastPath = path
                    lastFile = file

            if lastPath != path or lastFile != file:
                writeStringsFile(lastPath, lastFile, languages, values)
                # Wipe out the old list
                values = initializeLocalizedValues(languages)
                lastPath = path
                lastFile = file

            l10ns = row[valueStartIdx:]
            for (index, value) in enumerate(l10ns):
                language = languages[index]
                stringValue = comment + "\n\"" + objectId + ".text\" = \"" + value + "\";\n"
                values[language] += [stringValue]

        writeStringsFile(lastPath, lastFile, languages, values)

def getFieldnamesAndLanguages(csvfile, reader, baseLang):
    if csv.Sniffer().has_header(csvfile.read(1024)):
        csvfile.seek(0)
        fields = reader.next()
    else:
        csvfile.seek(0)
        fields = ["path", "file", "object-id", "comment", baseLang]

    nonLanguageFieldCount = 0
    for field in fields:
        if isLanguage(field) == False:
            nonLanguageFieldCount += 1

    return (fields[:nonLanguageFieldCount], fields[nonLanguageFieldCount:])

def isLanguage(field):
    # TODO: (TL) Make this more robust, check against ISO codes
    return field == "en" or field == "fr"

def initializeLocalizedValues(languages):
    return { lang : [] for lang in languages } 

def writeStringsFile(path, file, languages, values):
    for language in languages:
        relativePath = os.path.join(path, language + ".lproj", "test-" + file)
        # TODO: (TL) Log to logfile if specified
        print "Writing " + relativePath
        with open(relativePath, "wb") as stringsFile:
            stringsFile.write("\n".join(values[language]))

# MAIN #
if __name__ == "__main__":
    sys.exit(main())
