from operations.action_upon_detection import action_upon_detection
from operations.save_token_exceptions import save_token_detection_exception

def detect(token, project_name, srcFile):
    try:
        if token.__contains__("line"): lineno = token["line"]
        if token.__contains__("type"): tokenType = token["type"]
        if token.__contains__("name"): name = token["name"]
        if token.__contains__("args"): args = token["args"]
        if token.__contains__("hasInputs"): hasInputs = token["hasInputs"]

        unwantedMethods = ['execution.query', 'connection.cursor.execute']
        
        if tokenType == "variable" and token.__contains__('valueSrc') and token.__contains__('args'):
            
            args = token['args']
            valueSrc = token['valueSrc']
            if valueSrc in unwantedMethods and len(args) > 0:
                action_upon_detection(project_name, srcFile, lineno, 'sql_injection', 'sql injection', token)
                    
        elif tokenType == "function_call" and name in unwantedMethods and len(args) > 0 :
            action_upon_detection(project_name, srcFile, lineno, 'sql_injection', 'sql injection', token)
        
    except Exception as error: save_token_detection_exception('sql injection detection  '+str(error)+'  '+ str(token), srcFile)