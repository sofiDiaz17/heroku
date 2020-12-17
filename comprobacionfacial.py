import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person

KEY = "4e341ff775bf4ee18e3a726fc1b5de7b"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://faceorange.cognitiveservices.azure.com/"
face_client=FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))



# Verification example for faces of different persons.
# Since target faces are same person, in this example, we can use the 1st ID in the detected_faces_ids list to compare.
#verify_result_diff = face_client.face.verify_face_to_face(source_image2_id, detected_faces_ids[0])
#print('Faces from {} & {} are of the same person, with confidence: {}'
#    .format(source_image_file_name2, target_image_file_names[0], verify_result_diff.confidence)
#    if verify_result_diff.is_identical
#    else 'Faces from {} & {} are of a different person, with confidence: {}'
#        .format(source_image_file_name2, target_image_file_names[0], verify_result_diff.confidence))

def Comprobacion(_urlIne,_urlSelfie):
    target_image_file_names = [_urlIne]
    # The source photos contain this person
    source_image_file_name1 = open(_urlSelfie,"rb")
    #source_image_file_name2 = open("pelon.jpeg","rb")

    # Detect face(s) from source image 1, returns a list[DetectedFaces]
    # We use detection model 2 because we are not retrieving attributes.
    detected_faces1 = face_client.face.detect_with_stream(source_image_file_name1 , detectionModel='detection_02')
    # Add the returned face's face ID
    print(detected_faces1)
    if not detected_faces1:
        print("NO HAY ROSTRO")
        bandera=2
        return bandera
    source_image1_id = detected_faces1[0].face_id
    print('{} face(s) detected from image {}.'.format(len(detected_faces1), source_image_file_name1))

    # Detect face(s) from source image 2, returns a list[DetectedFaces]
    #detected_faces2 = face_client.face.detect_with_stream(source_image_file_name2, detectionModel='detection_02')
    # Add the returned face's face ID
    #source_image2_id = detected_faces2[0].face_id
    #print('{} face(s) detected from image {}.'.format(len(detected_faces2), source_image_file_name2))

    # List for the target face IDs (uuids)
    detected_faces_ids = []
    # Detect faces from target image url list, returns a list[DetectedFaces]
    for image_file_name in target_image_file_names:
        # We use detection model 2 because we are not retrieving attributes.
        print(image_file_name)
        image_file_name = open(image_file_name,"rb")
        detected_faces = face_client.face.detect_with_stream(image_file_name, detectionModel='detection_02')
        # Add the returned face's face ID
        detected_faces_ids.append(detected_faces[0].face_id)
        print('{} face(s) detected from image {}.'.format(len(detected_faces), image_file_name))

        # Verification example for faces of the same person. The higher the confidence, the more identical the faces in the images are.
    # Since target faces are the same person, in this example, we can use the 1st ID in the detected_faces_ids list to compare.
    verify_result_same = face_client.face.verify_face_to_face(source_image1_id, detected_faces_ids[0])
    print('Faces from {} & {} are of the same person, with confidence: {}'
        .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence)
        if verify_result_same.is_identical
           
        else 'Faces from {} & {} are of a different person, with confidence: {}'
            .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence))

    print(verify_result_same.confidence)
    if verify_result_same.confidence >.5:
        bandera=1
        return bandera
    else:
        bandera=0
        return bandera


