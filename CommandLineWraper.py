import json
import os
import sys
import pathlib as Path

class CommandLine:
  def __init__(self,commands_file:str = "commandLine_llm_wraper.json") -> None:
    self.commands = json.loads(open(commands_file).read())
    self.functions = { 
      "G30":self.G30,
      "G31":self.G31,
      "G32":self.G32}
  def __del__(self):
    pass

  def HandleCommand(self, key:str, args:str = None) -> str:
    if key in self.commands:
      return self.functions[key](args)
    raise Exception("command not found")
  
  def GetCommand(self) -> str:
    return self.commands
  
  def G30(self, args) -> str:
    if os.path.isfile(args) or os.path.isdir(args):
      os.system("code " + args)
      return "opened vscode"  + args
    os.system("code")
    return "opened vscode"
  
  def G31(self,args) -> str:
    if args != None or args != "":
      os.system("firefox " + args + " &")
      return "opened firefox" + args
    os.system("firefox &")
    return "opened firefox"  

  def G32(self,args) -> str:
    os.system("discord &")
    return "opened dicord"