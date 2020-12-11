from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
from PIL import Image
import sys
import time
import requests
import json
import os

# If you are using a Jupyter notebook, uncomment the following line.
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO


subscription_key = "7ee7446ab0c44ec9b79e2baaa14ba40b"
endpoint = "https://ekkos02.cognitiveservices.azure.com/"


computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

print("===== Batch Read File - local =====")
# Get image of handwriting
localimg = "static\\INEDELANTE\\fotofiona.jpeg"
# Open the image
image = Image.open(localimg)


text_recognition_url = endpoint + "/vision/v3.1/read/analyze"

# Set image_url to the URL of an image that you want to recognize.
image_url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs/master/articles/cognitive-services/Computer-vision/Images/readsample.jpg"

headers = {'Ocp-Apim-Subscription-Key': subscription_key,'Content-Type': 'application/octet-stream'}
with open(localimg, 'rb') as f:
    data = f.read()
response = requests.post(
    text_recognition_url, headers=headers, data=data)

# Extracting text requires two API calls: One call to submit the
# image for processing, the other to retrieve the text found in the image.

# Holds the URI used to retrieve the recognized text.
operation_url = response.headers["Operation-Location"]

# The recognized text isn't immediately available, so poll to wait for completion.
analysis = {}
poll = True
while (poll):
    response_final = requests.get(
        response.headers["Operation-Location"], headers=headers)
    analysis = response_final.json()
    
    #print(json.dumps(analysis))

    time.sleep(1)
    if ("analyzeResult" in analysis):
        poll = False
    if ("status" in analysis and analysis['status'] == 'failed'):
        poll = False

contador= ' '
if analysis['status'] == "succeeded":
    #print(analysis["analyzeResult"]["readResults"][0]["lines"])
    for l in analysis["analyzeResult"]["readResults"][0]["lines"]:
        #print(l["text"])
        contador=contador+ '\n' + l["text"]
    

print(contador)