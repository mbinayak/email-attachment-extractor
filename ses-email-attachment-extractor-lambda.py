__author__ = "Binayak Mishra"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Binayak Mishra"
__email__ = "mbinayak@ymail.com"
__status__ = "Development"
from __future__ import print_function

import email
import boto3
import urllib
import os
import gzip
import string
import zipfile

s3 = boto3.client('s3')
s3r = boto3.resource('s3')
tempStoreDir = "/tmp/output/"

outputPrefix = "files/"
outputBucket = os.environ['BUCKET_STORE']  # Bucket to upload the attachments
fileExt = os.environ['FILE_EXT']  # File extension type to look for as an attachment for example: xml or pdf etc.


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    try:
        # Set outputBucket if required
        if not outputBucket:
            global outputBucket
            outputBucket = bucket

        # Use waiter to ensure the file is persisted
        waiter = s3.get_waiter('object_exists')
        waiter.wait(Bucket=bucket, Key=key)

        response = s3r.Bucket(bucket).Object(key)
        msg = email.message_from_string(response.get()["Body"].read())  # Read the raw text file into a Email Object

        if len(msg.get_payload()) == 2:
            if not os.path.isdir(tempStoreDir):
                os.mkdir(tempStoreDir)  # Create directory for file/files
            attachment = msg.get_payload()[1]  # The first attachment
            extract_attachment(attachment)  # Extract the attachment into tempStoreDir
            upload_file()  # Upload the "fileExt" file / files to S3
        else:
            print("Could not see file/attachment.")
        return 0
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist '
              'and your bucket is in the same region as this '
              'function.'.format(key, bucket))
        raise e
    delete_file(key, bucket)


def extract_attachment(attachment):
    print(attachment.get_content_type(), attachment.get_filename())
    if fileExt in attachment.get_content_type():
        open(attachment.get_filename(), 'wb').write(attachment.get_payload(decode=True))
    elif "gzip" in attachment.get_content_type():
        # Process filename.fileExt.gz attachments (Providers not complying to standards)
        contentdisp = string.split(attachment.get('Content-Disposition'), '=')
        fname = contentdisp[1].replace('\"', '')
        open('/tmp/' + contentdisp[1], 'wb').write(attachment.get_payload(decode=True))
        # This assumes we have filename.fileExt.gz, if we get this wrong, we will just ignore the report
        fileName = fname[:-3]
        open(tempStoreDir + fileName, 'wb').write(gzip.open('/tmp/' + contentdisp[1], 'rb').read())
    elif "zip" in attachment.get_content_type():
        # Process filename.zip attachments
        open('/tmp/attachment.zip', 'wb').write(attachment.get_payload(decode=True))
        with zipfile.ZipFile('/tmp/attachment.zip', "r") as z:
            z.extractall(tempStoreDir)
    else:
        print('Skipping ' + attachment.get_content_type())


def upload_file():
    # Put all "fileExt" back into S3 (Covers non-compliant cases if a ZIP contains multiple results)
    for fileName in os.listdir(tempStoreDir):
        if fileName.endswith("." + fileExt):
            print("Uploading: " + fileName + "--START--")  # File name to upload
            s3r.meta.client.upload_file(tempStoreDir + '/' + fileName, outputBucket, outputPrefix + fileName)
            print("Uploaded: " + fileName + "--END--")
    return True


# Delete the file in the current bucket
def delete_file(key, bucket):
    s3.delete_object(Bucket=bucket, Key=key)
    print("%s deleted fom %s ") % (key, bucket)

