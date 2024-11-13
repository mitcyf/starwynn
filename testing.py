import requests
import json
import starwynn_utils as utils

current_dict = {key:value['guild']['prefix'] for key, value in utils.get_terr().items()}

def replace_guild(dict, original, new):
    return {key:(value if value != original else new) for key, value in dict.items()}

corkus_hold = replace_guild(current_dict, "bean", "ESI")

# json_string = json.dumps(corkus_hold, sort_keys=True, indent=2)
with open('claims.json', 'w') as fp:
    json.dump(corkus_hold, fp, sort_keys=True)
