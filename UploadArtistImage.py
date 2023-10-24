from decimal import Decimal
import json
import requests
import logging
import boto3
from botocore.exceptions import ClientError

def create_bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        
    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == '__main__':
    # Creating s3 Bucket
    create_bucket('s3905369')
    s3 = boto3.client('s3')
    response = s3.list_buckets() 
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f' {bucket["Name"]}')
    # Loading Artist Images
    with open("a1.json") as json_file:
        music_list = json.load(json_file, parse_float=Decimal)

    for song in music_list['songs']:
        artimg = song['img_url']
        fname = artimg.split('/')[-1]
        img_data = requests.get(artimg).content
        with open(fname , 'wb') as handler:
            handler.write(img_data)
        upload_file(fname , 's3905369')
    print('Images Uploaded Successfully!')