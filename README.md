# Online Music Subscription Application

## Overview
This project is an online music subscription application developed using Python, Flask, AWS services including EC2, S3, and DynamoDB. The application allows users to log in, register, subscribe to music, and view their subscriptions.

## Features
- **User Authentication**: Users can log in and register. The credentials are validated against data stored in a DynamoDB table.
- **Music Subscription**: Users can search for music by title, artist, or year, and subscribe to them. Subscribed music details are displayed in the user's subscription area.
- **Music Management**: Users can remove music from their subscriptions.
- **Image Handling**: Artist images are automatically downloaded from external links then uploaded and stored in an S3 bucket.

## Prerequisites
- AWS Account with access to EC2, S3, and DynamoDB.
- Python environment to run the scripts.

## Setup and Running

1. **Set up AWS Credentials**:
Replace the placeholders in the `music_subscription/app.py` with your AWS credentials.
```
region_name='us-east-1',
aws_access_key_id='######',
aws_secret_access_key='######',
aws_session_token='######'
```


2. **Run the Scripts**:
- To create the music table in DynamoDB:
  ```
  python MusicCreateTable.py
  ```
- To load data from `a1.json` to the music table:
  ```
  python MusicLoadData.py
  ```
- To download artist images and upload them to S3:
  ```
  python UploadArtistImage.py
  ```

3. **Deploy on EC2**:
- Launch an EC2 instance with Ubuntu Server 20.04/18.04 LTS AMI.
- Connect to the instance using its Public IPv4 DNS.
- Set up a web server environment, e.g., Apache2:
  ```
  sudo service apache2 start
  sudo service apache2 restart
  ```
- Deploy the application on the server and ensure it's accessible via the root Public IPv4 DNS of the EC2 instance.

## Acknowledgements
This project was developed as part of the COSC2626/2640 Cloud Computing course at RMIT.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
