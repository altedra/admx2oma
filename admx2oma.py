import sys, os
from lxml import objectify

usage = """
Usage is:
py parse.py <your.admx> <ADMX-OMA-URI>
<ADMX-OMA-URI>  : The OMA-URI you specifyed in Intune when ingesting admx file
                  Take care, the OMA-URI is case sensitive.
<your.admx>     : The admx file you ingested

"""

def run():
    if len(sys.argv) < 3:
        print(usage)
        sys.exit()

    admxFile    = sys.argv[1]
    admxOMA_URI = sys.argv[2]

    if not os.path.exists(admxFile):
        print("file not found: " + admxFile)
        sys.exit()

    templatestring      = "./<scope>/Vendor/MSFT/Policy/Config/<area>/<policy>"
    catHierarchie = {}
    try:
        (AppName, SettingType, id_or_admxName) = admxOMA_URI.partition("/ADMXInstall/")[2].split("/")
    except BaseException:
        print()
        print("ERROR: Bad OMA-URI: " + admxOMA_URI)
        print(usage)
        sys.exit()

    admx = objectify.parse(admxFile)
    r = admx.getroot()
    for element in r.categories.getchildren():
        catHierarchie[element.get("name")] = element.parentCategory.get('ref')

    for policy in r.policies.findall("policy"):
        out = templatestring
        out = out.replace("<policy>", policy.get("name"))

        hierarchie = policy.parentCategory.get("ref")
        nextCat = catHierarchie[policy.parentCategory.get("ref")]
        while nextCat.find(":") == -1:
            hierarchie = '~'.join((nextCat, hierarchie))
            if not nextCat in catHierarchie:
                break
            nextCat = catHierarchie[nextCat]
        hierarchie = '~'.join((AppName, SettingType, hierarchie))
        
        out = out.replace("<area>", hierarchie)

        p = PolicyOutput(policy.get("name"))
        
        if policy.get("class") in ("Both", "user"):
            p.omaUser = out.replace("<scope>", "User")
        if policy.get("class") in ("Both", "device"):
            p.omaDevice = out.replace("<scope>", "Device")
        
        if hasattr(policy, "elements"):
            for element in policy.elements.getchildren():
                v = PolicyOutput.PolicyValue(element.get('id'), element.tag, element.get('valueName') or element.get('id'), element.get('required'))
                p.values.append(v)
                if element.tag in ('enum'):
                    for item in element.getchildren():
                        val = item.value.getchildren()[0]
                        v.valEnumOptions.append(str(val.get("value") if val.get("value") is not None else val.text))
                    v.value = v.valEnumOptions[0]
                if element.tag in ('boolean'):
                    v.valEnumOptions.append('true')
                    v.valEnumOptions.append('false')
                    v.value = v.valEnumOptions[0]
        p.print()


class PolicyOutput:
    class PolicyValue:
        def __init__(self, valID = '', valType = 'text', valName = None, required = None, value = ''):
            self.valID      = valID
            self.valType    = valType
            self.valName    = valName or valID
            self.value      = value
            self.valEnumOptions = []
            self.required   = required
        
    def __init__(self, name = ""):
        self.polName    = name
        self.omaDevice  = 'No device policy'
        self.omaUser    = 'No user policy'
        self.values     = []
        templatestring  = "./<scope>/Vendor/MSFT/Policy/Config/<area>/<policy>"

    def print(self):
        print(polTemplate.format(**self.__dict__))
        dataTagList = []
        for value in self.values:
            dataTagList.append(dataTagTemplate.format(**value.__dict__))
            out = {}
            out.update({'valEnumOptionsOut': '(%s)'% '|'.join(value.valEnumOptions) if len(value.valEnumOptions) else ''})
            out.update({'requiredOut': 'required' if value.required else 'optional'})
            out.update({'dataTag': dataTagList[-1]})
            out.update(value.__dict__)
            print(valTemplate.format(**out))
        dataTagList.insert(0, '') if len(dataTagList) else dataTagList
        print(recordTemplate.format(**{'dataTags': '\n'.join(dataTagList)}))
        

polTemplate = """
===============================
Policy: {polName}
===============================
{omaUser}
{omaDevice}
Enabled value: <enabled/>
Disabled value: <disabled/>
""".rstrip()

polTemplate = """
===============================
Policy: {polName}
===============================
{omaUser}
{omaDevice}
(<enabled/>|<disabled/>)
""".rstrip()

dataTagTemplate = """
<data id='{valID}' value='{value}'/>
""".strip()

valTemplate = """
-------------------------------
{valName} ({requiredOut})
Value type: {valType} {valEnumOptionsOut}
{dataTag}
""".strip()

valTemplate = """
-------------------------------
Key Name:   {valName}
Key ID:     {valID}
Value type: {valType} {valEnumOptionsOut}
""".strip()

recordTemplate = """
----------- Example -----------
<enabled/>{dataTags}
""".strip()

if __name__ == "__main__":
    run()





