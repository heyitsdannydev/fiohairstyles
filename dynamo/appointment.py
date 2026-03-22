import os
import boto3
import datetime
import calendar
from typing import Literal
from loguru import logger
from boto3.dynamodb.conditions import Key

from models.appointment import Appointment
from dynamo.dynamo import get_dynamodb_table


def get_appointments_by_month_from_dynamo(
    month: int, year: int, order: Literal["desc", "asc"] = "desc"
) -> list[Appointment]:
    """
    Fetch appointments from DynamoDB using GSI1 (global by date).
    """

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    table = dynamodb.Table(os.getenv("TABLE_NAME"))

    start_date = datetime.datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime.datetime(year, month, last_day, 23, 59, 59)

    start_sk = start_date.strftime("%Y-%m-%dT00:00:00")
    end_sk = end_date.strftime("%Y-%m-%dT23:59:59")

    response = table.query(
        IndexName="appointment-date",
        KeyConditionExpression=Key("gsi1_pk").eq("Appointment")
        & Key("ServiceDateTime").between(start_sk, end_sk),
        ScanIndexForward=(order == "asc"),  # True = asc, False = desc
    )

    appointments = response.get("Items", [])

    return [Appointment(**a) for a in appointments]


def save_appointment(appointment_data: dict, old_sk: str, new_sk: str) -> bool:
    """Save appointment to DynamoDB."""
    table = get_dynamodb_table()
    if old_sk and old_sk != new_sk:
        table.delete_item(Key={"pk": appointment_data["pk"], "sk": old_sk})
    table.put_item(Item=appointment_data)
    return True
