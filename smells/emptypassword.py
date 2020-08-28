from operations.action_upon_detection import action_upon_detection

def detect(token, project_name, srcFile):
    
    if token.__contains__("line"): lineno = token["line"]
    if token.__contains__("type"): tokenType = token["type"]
    if token.__contains__("name"): name = token["name"]
    if token.__contains__("value"): value = token["value"]
    
    commonPasswords = ['password','passwords','pass','pwd','userpassword','userpwd', 'userpass', 'pass_no', 'pass-no', 'user-pass', 'upass']
    
    if tokenType == "variable" and name in commonPasswords and value is None: 
        action_upon_detection(project_name, srcFile, lineno, 'empty_password', 'empty password', token)

    elif tokenType == "variable" and name in commonPasswords and len(value) == 0: 
        action_upon_detection(project_name, srcFile, lineno, 'empty_password', 'empty password', token)

    elif tokenType == "comparison" and token.__contains__("pairs"):
        pairs = token["pairs"]

        for pair in pairs:
            if len(pair) == 2 and pair[0] in commonPasswords and (pair[1] is None or len(pair[1]) == 0): 
                action_upon_detection(project_name, srcFile, lineno, 'empty_password', 'empty password', token)
            
            elif len(pair) == 2 and pair[1] in commonPasswords and (pair[0] is None or len(pair[0]) == 0): 
                action_upon_detection(project_name, srcFile, lineno, 'empty_password', 'empty password', token)
    

    elif tokenType == "function_call" and token.__contains__('keywords'):
        for keyword in token['keywords']:
            if len(keyword) == 2 and keyword[0].lower() in commonPasswords and len(keyword[1]) == 0: 
                action_upon_detection(project_name, srcFile, lineno, 'empty_password', 'empty password', token)
