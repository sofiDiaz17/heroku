import requests
# pprint is used to format the JSON response
from pprint import pprint
import os

subscription_key = "10ed6ba7b3d4497096beabf32a4c9d39"
endpoint = "https://nrrecluters.cognitiveservices.azure.com/"
language_api_url = endpoint + "/text/analytics/v3.0/languages"

documents = {"documents": [
    {"id": "1", "text": "de den store hvide kanin sprang over hegnet og breakkede benet"},
    {"id": "2", "text": "Este es un document escrito en Español."},
    {"id": "3", "text": "这是一个用中文写的文件"}
]}
print("teamovic")
headers = {"Ocp-Apim-Subscription-Key": subscription_key}
response = requests.post(language_api_url, headers=headers, json=documents)
languages = response.json()
pprint(languages)