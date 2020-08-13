from operations.actionUponDetection import actionUponDetection

def detect(token, srcFile) :

    if token.__contains__("line"): lineno = token["line"]
    if token.__contains__("type"): tokenType = token["type"] 
    if token.__contains__("name"): methodname = token["name"]
    if token.__contains__("args"): args = token["args"]
    if token.__contains__("hasInputs"): containsUserInput =  token["hasInputs"]

    if (tokenType == "function_call" and methodname == "exec" and args and containsUserInput): actionUponDetection(srcFile, lineno, 'shell_injection', 'exec statement')