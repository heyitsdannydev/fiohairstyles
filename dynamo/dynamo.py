import os
import boto3


def get_dynamodb_table():
    """Get DynamoDB table resource."""
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return dynamodb.Table(os.getenv("TABLE_NAME"))
