from operations.savewarnings import saveWarnings

def detect(token):

    if token.__contains__("line"): lineno = token["line"]
    if token.__contains__("type"): tokenType = token["type"]
    
    if tokenType == "variable":
        if token.__contains__("valueSrc"): valueSrc = token["valueSrc"]
        if token.__contains__("args"): args = token["args"]
        if valueSrc == "yaml.load": printWarning(lineno)

    elif tokenType == "function_call":
        if token.__contains__("name"): name = token["name"]
        if token.__contains__("args"): args = token["args"]
        
        if name == "yaml.load": printWarning(lineno)
        elif "yaml.load" in args: printWarning(lineno)

    elif tokenType == "function_def":
        if token.__contains__("return"): funcReturn  = token["return"]
        if token.__contains__("returnArgs"): returnArgs = token["returnArgs"]
        if funcReturn == "yaml.load" and returnArgs!= None: printWarning(lineno)
    

def printWarning(lineno):
    warning = 'yaml.load used'
    saveWarnings(warning,str(lineno))
    print(warning+ ' at line '+ str(lineno))
