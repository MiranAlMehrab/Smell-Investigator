import csv

def saveParsingExceptions(error,lineno):

    with open('logs/parsingExceptions.csv', 'a') as fp: 
        
        fw = csv.writer(fp)
        if error: fw.writerow([lineno,error])