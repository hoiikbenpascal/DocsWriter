import FunctionGetter
import os

fileName = "TestFile.cs"
newFileName = "TestFile.md"
className = ""

Title = ""



regex = r"public.*(class)|(Interface)"
file = open(fileName, "r")
os.remove(newFileName)
newFile = open(newFileName, "w")


file = file.readlines()
i = 0
while i < len(file): 
    func = FunctionGetter.GetFuncData(file, i)
    if(func != None):
        i += func["Summary"]["Lines"]
        FunctionGetter.AddFunctionToFile(newFile, func)
    i += 1

