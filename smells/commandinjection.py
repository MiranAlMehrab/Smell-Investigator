def detect(token):
    
    if token.__contains__("line"): lineno = token["line"] 
    if token.__contains__("name"): name = token["name"]
    if token.__contains__("type"): tokenType = token["type"]
    if token.__contains__("args"): args = token["args"]
    if token.__contains__("hasInputs"): containsUserInput =  token["hasInputs"]

    unwanted = ['subprocess.Popen']
    
    if tokenType == "function_call" and name in unwanted and (args or containsUserInput):
        warning = 'possible cmd injection at line ' + str(lineno)
        print(warning)