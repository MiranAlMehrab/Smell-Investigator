from operations.actionUponDetection import actionUponDetection

def detect(token, project_name, srcFile):

    if token.__contains__("line"): lineno = token["line"]
    if token.__contains__("type"): tokenType = token["type"]
    if token.__contains__("name"): name = token["name"]
    if token.__contains__("value"): value = token["value"]
    
    restrictedNames = ['debug','debug_propagate_exceptions']
    
    if tokenType == "variable" and name.lower() in restrictedNames and value is True: 
        actionUponDetection(project_name, srcFile, lineno, 'debug_true', 'debug set true')


    elif tokenType == "function_call" and token.__contains__("keywords"):
        keywords = token["keywords"]
        
        for keyword in keywords:
            if(keyword[0] in restrictedNames and keyword[1] is True): 
                actionUponDetection(project_name, srcFile, lineno, 'debug_true', 'debug set true')


    elif tokenType == "dict" and token.__contains__("keys") and token.__contains__("values"): 
        pairs = [list(item) for item in zip(token["keys"], token["values"])]
        
        for pair in pairs: 
            if pair[0] in restrictedNames and pair[1] is True: 
                actionUponDetection(project_name, srcFile, lineno, 'debug_true', 'debug set true')
