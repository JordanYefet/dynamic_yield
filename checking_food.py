import os
import json
import sys
from datetime import *
import boto3

max_labels = 10
S3Bucket = "drorassignment"
fileName = "timestamp.json"


def lambda_handler(event, context):
    # Filename of object (with path)
    photo_path = event['Records'][0]['s3']['object']['key']
    print(photo_path)
    photo = os.path.basename(photo_path)

    client = boto3.client('rekognition', 'eu-central-1')

    response = client.detect_labels(
        Image={'S3Object': {'Bucket': S3Bucket, 'Name': photo}},
        MaxLabels=max_labels,
        MinConfidence=90)

    print('\n')
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])

    print("labels: ")
    print(labels)

    isFood = False
    for label in labels:
        if(label == "Fish" or label == "Bread" or label == "Milk"):
            isFood = True
            break

    if(isFood):
        print("Food has been uploaded.")
        print("Updating timestamp...")
        timestamp = timestampUpdate()
        print(f"timestamp has been updated: {timestamp}")
    else:
        print("The uploaded photo is not food!")


######################################################
# writing to file
def timestampUpdate():
    # getting data from timestamp.json
    s3 = boto3.resource('s3')
    obj = s3.Object(S3Bucket, fileName)
    jsonData = json.load(obj.get()['Body'])

    # getting current datetime
    currentDate = date.today()
    currentTime = datetime.now().time()

    # writing data to jsonData
    jsonData['date']['year'] = currentDate.year
    jsonData['date']['month'] = currentDate.month
    jsonData['date']['day'] = currentDate.day
    jsonData['time']['hour'] = currentTime.hour
    jsonData['time']['minute'] = currentTime.minute
    jsonData['time']['second'] = currentTime.second

    print("writing to data...")
    obj.put(Body=json.dumps(jsonData))

    return jsonData
