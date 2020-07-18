import ast
import json

class Analyzer(ast.NodeVisitor):

    def __init__(self):
        self.inputs = []
        self.statements = []

    ######################### Import Modules Block Here #########################
    def visit_Import(self, node):
        
        for name in node.names:

            module = {}
            module["type"] = "import"
            module["line"] = node.lineno
            module["og"] = name.name
            module["alias"] = name.asname if name.asname else None

            self.statements.append(module)
        self.generic_visit(node)


    def visit_ImportFrom(self, node):
        
        for name in node.names:

            member = {}
            member["type"] = "import"
            member["line"] = node.lineno
            member["og"] = node.module +'.'+ name.name if name.name !="*" else node.module
            member["alias"] = node.module +'.'+ name.asname if name.asname else None

            self.statements.append(member)
        self.generic_visit(node)


    ######################### Function Definitions Here #########################
    def visit_FunctionDef(self, node):
        
        # print(ast.dump(node))

        func_def = {}
        func_def["type"] = "function_def"
        func_def["line"] = node.lineno
        func_def["name"] = node.name
        func_def["args"] = []
        func_def["defaults"] = []
        func_def["return"] = None

        for arg in node.args.args:
            if isinstance(arg, ast.arg): func_def["args"].append(arg.arg)
        
        if isinstance(node.args.vararg, ast.arg): func_def["args"].append(node.args.vararg.arg)
        elif isinstance(node.args.kwarg, ast.arg): func_def["args"].append(node.args.kwarg.arg)
        
        for default in node.args.defaults:
            self.addVariablesToList(default,func_def["defaults"])

        for item in node.body:
            
            if isinstance(item,ast.Return):
                func_def["return"] = self.addVariablesToList(item.value,[])
                func_def["return"] = func_def["return"][0] if len(func_def["return"]) > 0 else None

                if isinstance(item.value,ast.Call):
                    func_def["returnArgs"] = []
                    for arg in item.value.args:
                        func_def["returnArgs"] = self.addVariablesToList(arg, func_def["returnArgs"])
                        
        self.statements.append(func_def)
        self.generic_visit(node)


    ######################### Variable And List Assign Block Here #########################

    def visit_Assign(self, node):
        
        # print(ast.dump(node))
        for target in node.targets:
            
            variable = {}
            variable["type"] = "variable"
            variable["line"] = node.lineno
        
            if isinstance(target,ast.Name):
                variable["name"] = target.id

            elif isinstance(target, ast.Subscript):
                var = self.addVariablesToList(target.value, [])
                variable["name"] = var[0] if len(var) > 0 else None
                
                varSlice = self.addVariablesToList(target.slice.value, [])
                varSlice = varSlice[0] if len(varSlice) > 0 else None

                if varSlice != None: variable["name"] = variable["name"]+'['+str(varSlice)+']'

            elif isinstance(target,ast.Tuple):
                variable["type"] = "tuple"
                variable["names"] = []
                for element in target.elts:
                    names = self.addVariablesToList(element, [])
                    if names[0]: variable["names"].append(names[0])
            
            elif isinstance(target, ast.Attribute):
                    # funcName = self.getFunctionAttribute(value)
                    # if value.attr and funcName: funcName = funcName +'.'+ value.attr
                    
                name = self.getFunctionAttribute(target)
                if target.attr: name = name +'.'+ target.attr
                variable["name"] = name
                
            if isinstance(node.value, ast.Constant):
                variable["value"] = node.value.value
                variable["valueSrc"] = "initialized"
                variable["isInput"] = False

            if isinstance(node.value, ast.Name):
                variable["value"] = self.valueFromName(node.value.id)
                variable["valueSrc"] = "initialized"
                variable["isInput"] = False

            
            elif isinstance(node.value, ast.BinOp):
                usedVars = self.getUsedVariablesInVariableDeclaration(node.value)
                hasInputs = self.checkUserInputsInVariableDeclaration(usedVars)

                if hasInputs:
                    self.inputs.append(variable["name"])
                    variable["value"] = None
                    variable["valueSrc"] = "input"
                    variable["isInput"] = True
                
                else:
                    variable["value"] = self.buildNewVariableValueFromUsedOnes(usedVars)
                    variable["valueSrc"] = "initialized"
                    variable["isInput"] = False

            elif isinstance(node.value, ast.Call):
                
                funcName = self.getFunctionName(node)
                returnFromFunction = self.functionReturnValue(funcName) 
                variable["value"] =  returnFromFunction if returnFromFunction != funcName else None 
                variable["valueSrc"] = funcName
                variable["args"] = []

                if(funcName == "input"):
                    variable["isInput"] = True
                    self.inputs.append(variable["name"])
                
                else: variable["isInput"] = False

                for arg in node.value.args:
                    if isinstance(arg, ast.Attribute): 
                        
                        variable["args"].append(self.getFunctionAttribute(arg)+'.'+arg.attr)

                        funcObj = {}
                        funcObj["type"] = "function_obj"
                        funcObj["line"] = node.lineno
                        funcObj["objName"] = variable["name"]
                        funcObj["funcName"] = variable["valueSrc"]
                        funcObj["args"] = variable["args"]

                        if(funcObj not in self.statements):self.statements.append(funcObj)
                    else: variable["args"] = (self.addVariablesToList(arg,variable["args"]))

            elif isinstance(node.value, ast.List):
                variable["type"] = "list"
                variable["values"] = []
                
                for value in node.value.elts:
                    variable["values"] = self.addVariablesToList(value,variable["values"])

            elif isinstance(node.value, ast.Dict):
                variable["type"] = "dict"
                variable["keys"] = []
                variable["values"] = []

                for key in node.value.keys:
                    keyList = self.addVariablesToList(key,[])
                    if len(keyList) > 0: variable["keys"].append(keyList[0]) 
                
                for value in node.value.values:
                    valueList = self.addVariablesToList(value, [])
                    if len(valueList) > 0: variable["values"].append(valueList[0])
            
            elif isinstance(node.value,ast.Tuple):
                variable["type"] = "tuple"
                variable["values"] = []
                
                for element in node.value.elts:
                    values = self.addVariablesToList(element, [])
                    if len(values)>0: variable["values"].append(values[0])
                

            elif isinstance(node.value,ast.Set):
                variable["type"] = "set"
                variable["values"] = []
                
                for element in node.value.elts:    
                    values = self.addVariablesToList(element, [])
                    if len(values)>0: variable["values"].append(values[0])
                
            elif isinstance(node.value, ast.IfExp):
                variable["type"] = "variable"
                variable["values"] = []

                bodyList = self.addVariablesToList(node.value.body,[])
                if len(bodyList) > 0: variable["values"].append(bodyList[0])

                comparatorList = self.addVariablesToList(node.value.orelse, [])
                if len(comparatorList) > 0: variable["values"].append(comparatorList[0])

            elif isinstance(node.value, ast.BoolOp):
                variable["values"] = []
                for value in node.value.values:
                    valueList = self.addVariablesToList(value,[])
                    if len(valueList) > 0: variable["values"].append(valueList[0])

            self.statements.append(variable)
        self.generic_visit(node)



    ######################### If Comparasion Block Here #########################
    def visit_If(self,node):

        # print(ast.dump(node)) 
        statement = {}
        statement["type"] = "comparison"
        statement["line"] = node.lineno
        statement["pairs"] = []
        statement["test"] = []

        if isinstance(node.test,ast.BoolOp):
            for value in node.test.values:
                
                if isinstance(value,ast.Compare):
                    if isinstance(value.left,ast.Name) and isinstance(value.ops[0],ast.Eq) and isinstance(value.comparators[0],ast.Constant):
                        pair = []
                        pair.append(value.left.id)
                        pair.append(value.comparators[0].value)

                        statement["pairs"].append(pair)
                    
                    elif isinstance(value.left,ast.Name) and isinstance(value.ops[0],ast.Eq) and isinstance(value.comparators[0],ast.BinOp):
                        pair = []
                        pair.append(value.left.id)
                        
                        usedVars = self.getUsedVariablesInVariableDeclaration(value.comparators[0])
                        value = self.buildNewVariableValueFromUsedOnes(usedVars)
                        
                        pair.append(value.lstrip())
                        statement["pairs"].append(pair)
            
                elif isinstance(value, ast.Name):
                    statement["test"].append(value.id)
                
                elif isinstance(value, ast.Constant):
                    statement["test"].append(value.value)

        elif isinstance(node.test, ast.Compare):
            pair = []
            
            leftComparatorList = self.addVariablesToList(node.test.left, [])
            if len(leftComparatorList)>0: pair.append(leftComparatorList[0])

            comparatorList = self.addVariablesToList(node.test.comparators[0],[])
            print(comparatorList)
            if len(comparatorList) > 0: pair.append(comparatorList[0])
            statement["pairs"].append(pair)

            
        elif isinstance(node.test,ast.Name):
            statement["test"].append(node.test.id)

        elif isinstance(node.test, ast.Constant):
            statement["test"].append(node.test.value)

        elif isinstance(node.test, ast.Call):
            statement["test"].append(node.test.func.id)

        
        self.statements.append(statement)
        self.generic_visit(node)


    ######################### Try Block Here #########################

    def visit_Try(self, node):
        
        statement = {}
        statement["type"] = "exception_handle"
        # print(ast.dump(node))

        if isinstance(node, ast.Try):
            print(ast.dump(node.handlers[0].body[0]))
            print(type(node.handlers[0].body[0]))
            
            if isinstance(node.handlers[0].body[0],ast.Continue):
                statement["line"] = node.handlers[0].body[0].lineno
                statement["exceptionHandler"] = "continue"

            elif isinstance(node.handlers[0].body[0],ast.Pass): 
                statement["line"] = node.handlers[0].body[0].lineno
                statement["exceptionHandler"] = "pass"

            else:
                statement["line"] = node.handlers[0].body[0].lineno
                statement["exceptionHandler"] = "expression"

        self.statements.append(statement)
        self.generic_visit(node)


    ######################### Expressions Block Here #########################

    def visit_Expr(self, node):
        
        expression = {}
        expression["type"] = "function_call"
        expression["line"] = node.lineno
        expression["name"] = None
        expression["args"] = []
        expression["keywords"] = []
        expression["hasInputs"] = False
            
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name): expression["name"] = node.value.func.id
            elif isinstance(node.value.func,ast.Call): expression["name"] = self.getFunctionName(node)
            elif isinstance(node.value.func,ast.Attribute): expression["name"] = self.getFunctionNameFromObject(self.getFunctionName(node))
            
            for arg in node.value.args:
                print(ast.dump(arg))
                arguments = self.addVariablesToList(arg,expression["args"]) 
                expression["args"] = arguments             
            
            for keyword in node.value.keywords:
                karg = keyword.arg
                kvalue = None

                if isinstance(keyword.value,ast.Constant): kvalue = keyword.value.value
                if karg and kvalue: expression["keywords"].append([karg,kvalue])

            self.statements.append(expression)
        self.generic_visit(node)
    


    ######################### Utility Function Here #########################


    def addVariablesToList(self,node,itemList):
        if isinstance(node,ast.Name):
            if self.valueFromName(node.id): itemList.append(self.valueFromName(node.id)) 
            else: itemList.append(node.id)

        elif isinstance(node,ast.Constant): itemList.append(node.value)
        elif isinstance(node,ast.Attribute): itemList.append(self.getFunctionAttribute(node)+'.'+node.attr)

        elif isinstance(node,ast.FormattedValue):
            itemList = self.addVariablesToList(node.value, itemList)
        
        elif isinstance(node,ast.BinOp):    
            usedArgs = self.getUsedVariablesInVariableDeclaration(node)
            print(usedArgs)
            actualValue = self.buildNewVariableValueFromUsedOnes(usedArgs)
            itemList.append(actualValue)
        
        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                func = node.func.id
                itemList.append(self.functionReturnValue(func) if self.functionReturnValue(func) else func)
            
            elif isinstance(node.func, ast.Attribute):
                func = self.getFunctionAttribute(node.func)
                if node.func.attr and func: func = func +'.'+ node.func.attr
                itemList.append(func)
        
        elif isinstance(node, ast.List):
            for element in node.elts:
                itemList = self.addVariablesToList(element,itemList)
        
        elif isinstance(node, ast.JoinedStr):
            for value in node.values:
                itemList = self.addVariablesToList(value, itemList)

        
        return itemList


    def refineTokens(self):
        for statement in self.statements:

            if statement["type"] == "tuple" and statement.__contains__("names"):
                for name in statement["names"]:

                    variable = {}
                    variable["type"] = "variable"
                    variable["line"] = statement["line"]
                    variable["name"] = name
                    variable["value"] = statement["values"][(statement["names"].index(name))]
                    variable["valueSrc"] = statement["valueSrc"] if statement.__contains__("valueSrc") else "initialized"
                    variable["isInput"] = statement["isInput"] if statement.__contains__("isInput") else False
                    
                    self.statements.append(variable)
                    print(variable)

                self.statements.remove(statement)

            elif statement["type"] == "function_def" and statement.__contains__("return") == False: self.statements.remove(statement)
                


    def valueFromName(self,name):
        for statement in reversed(self.statements):
            if statement["type"] == "variable" and statement["name"] == name : return statement["value"] if statement.__contains__("value") else None 
        return name


    def getFunctionNameFromObject(self,name):
        
        fName = name.split('.')[0]
        lName = name.split('.')[1]

        for statement in self.statements:
            if statement["type"] == "function_obj" and fName == statement["objName"]: return statement["funcName"]+'.'+lName
        return name


    def functionReturnValue(self,funcName):

        for statement in self.statements:
            if statement["type"] == "function_def" and statement["name"] == funcName:
                if statement.__contains__("return"): return statement["return"]
                else: return None

        return funcName


    def getOperandsFromBinOperation(self,node,usedVars):
        if isinstance(node, ast.Name) and node.id: usedVars.append(node.id)
        elif isinstance(node, ast.Constant) and node.value: usedVars.append(node.value)
        elif isinstance(node, ast.Call): usedVars.append(self.getFunctionName(node.func))
        
        elif isinstance(node,ast.BinOp):  
            usedVars = self.getOperandsFromBinOperation(node.left,usedVars)  
            usedVars = self.getOperandsFromBinOperation(node.right,usedVars)

        return usedVars     
        

    def getUsedVariablesInVariableDeclaration(self,node):
        
        usedVariables = []
        for field, value in ast.iter_fields(node):
            self.getOperandsFromBinOperation(value,usedVariables)
                
        return usedVariables



    def buildNewVariableValueFromUsedOnes(self,usedVariables):
        
        value = None
        for variable in usedVariables:    
            found = False

            for statement in self.statements:
                # print(statement)        
                if statement["type"] == "variable" and statement["name"] == variable:
                    
                    if statement["isInput"] != True and value:
                        if type(value) == str or type(statement["value"]) == str: value = str(value) + str(statement["value"])
                        else: value = value + statement["value"]

                    elif statement["isInput"] != True: value = statement["value"]
                    elif statement["isInput"] == True: value = str(value) + "input"

                    found = True
                    break
                
                elif statement["type"] == "function_def" and statement["name"] == variable:
                    if statement.__contains__("return"): 
                        if value == None: value = statement["return"]
                        elif type(value) == str or type(statement["return"]) == str: value = str(value) + str(statement["return"])
                        else : value = value + statement["return"]

                        found = True
                        break 
                    
            if found == False and value and variable: value = value + variable
            elif found == False and variable: value = variable

        return value



    def getFunctionName(self, node):
        for fieldname, value in ast.iter_fields(node.value):
            
            if(fieldname == "func" and isinstance(value, ast.Name)): return value.id
            elif(fieldname == "func" and isinstance(value, ast.Attribute)):    
                functionName = self.getFunctionAttribute(value)
                return functionName +'.'+ value.attr if value.attr and functionName else functionName 

        return None
        

    def getFunctionAttribute(self, node):
        name = None
        attr = None

        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.Attribute):
                attr = value.attr
                name = self.getFunctionAttribute(value)
            
            elif isinstance(value,ast.Name): name = value.id
            elif isinstance(value,ast.Call): name = self.getFunctionAttribute(value)

        return name+'.'+attr if attr else name


    def checkUserInputsInVariableDeclaration(self,usedVariables):
        for variable in usedVariables:
            for statement in reversed(self.statements):

                if statement["type"] == "variable" and variable == statement["name"]:
                    return True if statement["isInput"] else False
                    
        return False



    def processArgs(self,arg):
        
        pass

    def checkUserInputsInFunctionArguments(self):
        for statement in self.statements:
            if statement["type"] == "function_call":
                
                index = self.statements.index(statement)
                statement["hasInputs"] = False
                foundInputs = False                
                
                for arg in statement["args"]:
                    for idx in range(index-1,-1, -1):
                        
                        if self.statements[idx]["type"] == "variable" and self.statements[idx]["name"] == arg and self.statements[idx]["isInput"]:
                            statement["hasInputs"] = True
                            foundInputs = True
                            break

                    if foundInputs: break
                    else: self.processArgs(arg)

    
    def printStatements(self, *types):
        for statement in self.statements:
            if len(types) == 0: print(statement)
            elif statement["type"] in types: print(statement)

        self.writeToFile()


    def printUserInputs(self):
        for user_input in self.inputs:
            print("user input: "+user_input)


    def writeToFile(self):
        f = open("tokens.txt", "w")
        
        for statement in self.statements:
            json.dump(statement, f)
            f.write("\n")
        
        f.close()

    