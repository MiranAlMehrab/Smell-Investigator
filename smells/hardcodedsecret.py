from operations.action_upon_detection import action_upon_detection

def detect(token, project_name, src_file):
    
    if token.__contains__("line"): lineno = token["line"]
    if token.__contains__("type"): tokenType = token["type"]
    if token.__contains__("name"): name = token["name"]
    if token.__contains__("value"): value = token["value"]
    if token.__contains__("valueSrc"): valueSrc = token["valueSrc"]
    
    commonKeywords = ['key','id', 'cert', 'root','passno','pass-no', 'pass_no', 'auth_token', 'authetication_token','auth-token', 'authentication-token', 'user', 'uname', 'username', 'user-name', 'user_name', 'owner-name', 'owner_name', 'owner', 'admin', 'login', 'pass', 'pwd', 'password', 'passwd', 'secret', 'uuid', 'crypt', 'certificate', 'userid', 'loginid', 'token', 'ssh_key', 'md5', 'rsa', 'ssl_content', 'ca_content', 'ssl-content', 'ca-content', 'ssh_key_content', 'ssh-key-content', 'ssh_key_public', 'ssh-key-public', 'ssh_key_private', 'ssh-key-private', 'ssh_key_public_content', 'ssh_key_private_content', 'ssh-key-public-content', 'ssh-key-private-content']
    commonPasswords = ['password','passwords','pass','pwd','userpassword','userpwd', 'userpass', 'pass_no', 'pass-no', 'user-pass', 'upass']

    if tokenType == "variable" and valueSrc == "initialized" and (name.lower() in commonKeywords or name.lower() in commonPasswords) and value is not None: 
        action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')
        
    elif tokenType == "comparison" and token.__contains__("pairs"):
        pairs = token["pairs"]
        for pair in pairs:        
          
            if len(pair) == 2 and pair[0] is not None and pair[1] is not None and (pair[0] in commonKeywords or pair[0] in commonPasswords): 
                action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')
            
            elif len(pair) == 2 and pair[0] is not None and pair[1] is not None and (pair[1] in commonKeywords or pair[1] in commonPasswords): 
                action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')
    
    elif (tokenType == "list" or tokenType == "set") and token.__contains__("values"):
        if (name.lower() in commonKeywords or name.lower() in commonPasswords) and len(token['values']) > 0: 
            action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')
    
    elif tokenType == "dict" and token.__contains__("keys"):
        if (name.lower() in commonKeywords or name.lower() in commonPasswords) and len(token['keys']) > 0: 
            action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret') 
        
        keys = token["keys"]
        for key in keys:
            if key in commonKeywords or key in commonPasswords: 
                action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')

    elif tokenType == "function_call" and token.__contains__('keywords'):
        keywords = token['keywords']
        for keyword in keywords:
            if len(keyword) == 2 and keyword[0] is not None and keyword[1] is not None and (keyword[0] in commonKeywords or keyword[0] in commonPasswords): 
                action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret')

    elif tokenType == "function_def" and token.__contains__("args") and token.__contains__("defaults"):
        args = token['args']
        defaults = token['defaults']
        
        if len(token["args"]) == len(token["defaults"]):
            pairs = zip(args, defaults)
            for pair in pairs:
                if pair[0] is not None and pair[1] is not None and (pair[0] in commonKeywords or pair[0] in commonPasswords): 
                    action_upon_detection(project_name, src_file, lineno, 'hardcoded_secret', 'hardcoded secret') 
