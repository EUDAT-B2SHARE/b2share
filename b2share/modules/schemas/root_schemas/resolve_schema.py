import requests
import json
import os

# Step 1: Fetch the JSON file from the HTTPS link
url = "https://dtr-playground.pidconsortium.eu/objects/testing/4160ad49bc7861b2cfd3"
response = requests.get(url)
data = response.json()

def fetch_type_info(data):
    if data.get("Schema", None) is not None:
        if data["Schema"].get("Properties", None) is not None:
            for item in data["Schema"]["Properties"]:
                if item.get("Type", None) is not None:
                    link=item.get("Type")
                    if "testing/" in item.get("Type"):
                        print("\"{}\": \"{}\"".format(item.get("Name"),"https://dtr-playground.pidconsortium.eu/#objects/"+item.get("Type")))
                        content_response = requests.get("https://dtr-playground.pidconsortium.eu/objects/"+link)
                        item['Type']=fetch_type_info(content_response.json())
    return data

# Step 2: Iterate over each link in the JSON file and curl the content
fetch_type_info(data)

with open(os.path.join(os.getcwd(), "b2share/modules/schemas/root_schemas", "dtr_test extended.json"), "w") as json_file:
    json.dump(data, json_file, indent=4)
