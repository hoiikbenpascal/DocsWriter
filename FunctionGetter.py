import re
import Templates

def AddFunctionToFile(file, function):
    # Create return data
    returns = {
        "Type": function["ReturnValue"],
        "Description": function["Summary"]["Returns"]
    }

    exception_table = ""
    if function["Summary"]["Exceptions"]:
        exception_table = Templates.exceptionTableTemplate


    for exception in function["Summary"]["Exceptions"]:
        exception_str = Templates.exceptionTemplate.format(**exception)
        exception_table += exception_str
        exception_table = re.sub("(?P<Char>[><])", r"\\\g<Char>", exception_table)
    
    param_table = ""
    if(function["Paramaters"] != None and len(function["Paramaters"]) != 0):
        param_table = Templates.paramTableTemplate
        for param in function["Paramaters"]:
            param_dict = {
                "Name": param["Name"],
                "Type": param["Type"],
                "Description": ""
            }

            par = next((par for par in function["Summary"]["Params"] if par["Name"] == param["Name"]), None)
            if(par != None):
                param_dict["Description"] = par["Description"]
            param_table += Templates.paramTemplate.format(**param_dict)
        param_table = re.sub("(?P<Char>[><])", r"\\\g<Char>", param_table)

    data = {
        "Name": function["Name"],
        "Description": function["Summary"]["Description"],
        "Paramaters": param_table,
        "Returns": Templates.returnTemplate.format(**returns),
        "Exceptions": exception_table
    }

    data_str = Templates.functionTableTemplate.format(**data)
    file.write(data_str)
    file.write('\n')




def GetFuncData(file_lines: list[str], index: int):
    summary = get_summary(file_lines, index)
    if(summary["Lines"] == 0):
        return
    line = file_lines[index + summary["Lines"]]

    func_regex = "public\s((?P<ReturnValue>\S*\s)){1,2}(?P<FunctionName>\S*)\((?P<Params>(.|[\n])*)\)"
    func = {
        "Summary": summary
    }
    match = re.search(func_regex, line)
    if(match):
        func_dict = match.groupdict()
        func["ReturnValue"] = func_dict["ReturnValue"].strip()
        func["Name"] = func_dict["FunctionName"]
        params_text = func_dict["Params"]
        func["Paramaters"] = get_paramaters(params_text)
        return func

def get_summary(file_lines: list[str], index: int):
    line = file_lines[index].strip()
    summary = ""

    sum_object = {
        "Description": "",
        'Params': [],
        "Returns": "",
        "Exceptions": [],
        "Lines": 0
    }

    while line.startswith("///"):
        summary += line.removeprefix('///')
        if(index + sum_object["Lines"] + 1 > len(file_lines)):
            break
        sum_object["Lines"] += 1
        line = file_lines[index + sum_object["Lines"]].strip()

    if(summary == ""):
        return sum_object
    

    annotations = re.finditer("<(?P<Name>\S*){1}[^>\"]*(\"(?P<VarName>[^>]*)\")?>(?P<Data>(?:[^<]|\n)*)<\/(?P=Name)>", summary)
    for data_line in annotations:
        data = data_line.groupdict()
        data_str = data["Data"].rstrip()
        match data["Name"]:
            case "summary":
                sum_object["Description"] = data_str
            case "param":
                param = {"Name": data["VarName"], "Description": data_str}
                sum_object["Params"].append(param)
            case "exception":
                exception = {"Type": data["VarName"], "Description": data_str}
                sum_object["Exceptions"].append(exception)
            case "returns":
                sum_object["Returns"] = data_str

        
    return sum_object

def get_paramaters(params):
    param_regex = "\s*(?P<Param>(?P<Type>\S*)\s(?P<Name>[^\s,]*)(\s*=\s*(?P<DefaultValue>[^,]*))?)[\s,]?"
    param_list = []
    if(params):
        all_params = re.finditer(param_regex, params)
        for param in all_params:
            param_dict = param.groupdict()
            param_list.append(param_dict)
        return param_list
    