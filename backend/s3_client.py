import os
import json
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET", "audiovook-test")
S3_PUBLIC_ENDPOINT = os.getenv("S3_PUBLIC_ENDPOINT")

s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

def create_bucket_if_not_exists():
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print(f"Bucket '{S3_BUCKET}' already exists.")
    except ClientError as e:
        # If a 404 error is raised, the bucket does not exist.
        if e.response['Error']['Code'] == '404':
            print(f"Bucket '{S3_BUCKET}' not found. Creating it.")
            s3_client.create_bucket(Bucket=S3_BUCKET)
            set_cors_policy()
            set_public_read_policy()
        else:
            # For any other exception, re-raise it.
            print("Error checking bucket existence.")
            raise

def set_cors_policy():
    # The user mentioned "Bucket privat", so we will not set a public read policy.
    # We will use presigned URLs. The CORS policy is still needed for the browser
    # to be able to fetch the HLS manifest and segments.
    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET'],
            'AllowedOrigins': [os.getenv("ALLOW_ORIGINS", "http://localhost:5173")],
            'ExposeHeaders': []
        }]
    }
    try:
        s3_client.put_bucket_cors(Bucket=S3_BUCKET, CORSConfiguration=cors_configuration)
        print(f"CORS policy set for bucket '{S3_BUCKET}'.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotImplemented':
            print(f"WARN: Could not set CORS policy on bucket '{S3_BUCKET}'. This might be a limitation of the local S3 server (LocalStack). Continuing without setting CORS.")
        else:
            # For any other exception, re-raise it.
            print("Error setting CORS policy.")
            raise

def set_public_read_policy():
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{S3_BUCKET}/*",
            }
        ],
    }
    try:
        s3_client.put_bucket_policy(Bucket=S3_BUCKET, Policy=json.dumps(policy))
        print(f"Public read policy set for bucket '{S3_BUCKET}'.")
    except ClientError:
        print(f"Error setting public policy for bucket '{S3_BUCKET}'.")
        raise
