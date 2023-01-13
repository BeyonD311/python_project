import os, re

def _get_modules():
    modules = []
    files = os.listdir("app/controllers")
    for file in files:
        if re.match(r'__.*__(?:\.py)?', file) == None:
            file = file[:-3]
            modules.append(file)
    return modules

modules = _get_modules()