import json
import os
import boto3
from datetime import *
from botocore.exceptions import ClientError

S3Bucket = "drorassignment"
fileName = "timestamp.json"
sender = "jordan.yefet90@gmail.com"
recipient = "jordan.yefet90@gmail.com"
emailSubject = "A Message from your Cat!"


def lambda_handler(event, context):
    print(f"S3Bucket: {S3Bucket}")
    print(f"sender: {sender}")
    print(f"recipient: {recipient}")

    fileName = "timestamp.json"

    timeLimitForFood = timedelta(minutes=15)

    # getting data from timestamp.json
    s3 = boto3.resource('s3')
    obj = s3.Object(S3Bucket, fileName)
    jsonData = json.load(obj.get()['Body'])

    # getting the date inside of the json file
    timestamp_year = jsonData['date']['year']
    timestamp_month = jsonData['date']['month']
    timestamp_day = jsonData['date']['day']

    # getting the time inside of the json file
    timestamp_hour = jsonData['time']['hour']
    timestamp_minute = jsonData['time']['minute']
    timestamp_second = jsonData['time']['second']

    # getting the email status bollian
    timestamp_emailSent = jsonData['emailSent']

    # building Date and Time objects of the json data
    timestampDate = date(timestamp_year, timestamp_month, timestamp_day)
    timestampTimedelta = timedelta(
        hours=timestamp_hour, minutes=timestamp_minute, seconds=timestamp_second)
    # building Date and Time objects of the current Date and Time
    currentDate = date.today()
    currentTime = datetime.now().time()
    currentTimedelta = timedelta(
        hours=currentTime.hour, minutes=currentTime.minute, seconds=currentTime.second)

    # conditional time delta - (given in the home-work)
    limit_timedelata = timedelta(minutes=15)

    if(timestamp_emailSent == False):
        # the first condition checks if it's the same date, the second condition checks if the timedelta is lower then 15 minutes
        if((currentDate == timestampDate) and ((currentTimedelta - timestampTimedelta) < limit_timedelata)):
            print("All good, the cat already ate!")
        else:
            body = "Warning! Feed the cat!"
            print(f"Sending an Email: {body}")
            emailFunction(sender, recipient, emailSubject, body)
            jsonData['emailSent'] = True
            # writing to jsonData
            obj.put(Body=json.dumps(jsonData))
    else:
        if((currentDate == timestampDate) and ((currentTimedelta - timestampTimedelta) < limit_timedelata)):
            body = "Back to normal..."
            print(f"Sending an Email: {body}")
            emailFunction(sender, recipient, emailSubject, body)
            jsonData['emailSent'] = False
            # writing to jsonData
            obj.put(Body=json.dumps(jsonData))
        else:
            print("The Email has already been sent. Check your inbox!")


def emailFunction(sender, recipient, emailSubject, emailBody):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = sender

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "eu-central-1"

    # The subject line for the email.
    SUBJECT = emailSubject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (  # "A Message from your Cat!\r\n"
        "{emailBody}"
    )

    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <!-- <h1>A Message from your Cat!</h1> -->
      <p>""" + str(emailBody) + """</p>
    </body>
    </html>
                """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
