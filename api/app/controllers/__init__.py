import os

import boto3

TABLE_NAME = os.environ["TABLE_NAME"]

# Single shared boto3 resource for every controller — mirrors the old
# dynamo/dynamo.py's get_dynamodb_table(), just centralized so no controller
# file re-creates its own client. Same table backs the pre-existing
# Streamlit app's production data (Client and Appointment# items).
#
# No credentials are passed explicitly: in Lambda, boto3 picks up the
# execution role automatically; locally, `uv run --env-file .env` (see
# run_local.sh) puts AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY in the
# environment, which boto3's default credential chain also picks up.
_dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
_table = _dynamodb.Table(TABLE_NAME)
