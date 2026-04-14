import os
import boto3
import datetime
import calendar
from typing import Literal
from loguru import logger
from boto3.dynamodb.conditions import Key, Attr

from models.appointment import Appointment
from dynamo.dynamo import get_dynamodb_table


def get_appointments_by_month_from_dynamo(
    month: int,
    year: int,
    order: Literal["desc", "asc"] = "desc",
    only_future: bool = False,
) -> list[Appointment]:
    """
    Fetch appointments from DynamoDB using pk and sk.
    """

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    table = dynamodb.Table(os.getenv("TABLE_NAME"))

    pk = f"Appointment#{year:04d}-{month:02d}"
    response = table.query(
        KeyConditionExpression=Key("pk").eq(pk),
        ScanIndexForward=(order == "asc"),  # True = asc, False = desc
    )

    appointments = [Appointment(**a) for a in response.get("Items", [])]

    # only show future appointments if we're looking at the current month and year
    if (
        only_future
        and month == datetime.datetime.now().month
        and year == datetime.datetime.now().year
    ):
        return [a for a in appointments if a.ServiceDateTime >= datetime.datetime.now()]

    return appointments


def delete_appointment(pk: str, sk: datetime.datetime) -> bool:
    """Delete appointment from DynamoDB."""
    table = get_dynamodb_table()
    table.delete_item(Key={"pk": pk, "sk": sk.isoformat()})
    return True


def save_appointment(appointment_data: dict, old_sk: str, new_sk: str) -> bool:
    """Save appointment to DynamoDB."""
    table = get_dynamodb_table()
    if old_sk and old_sk != new_sk:
        table.delete_item(Key={"pk": appointment_data["pk"], "sk": old_sk})
    table.put_item(Item=appointment_data)
    return True


def get_appointments_by_income_from_dynamo(
    month: int, year: int, order: Literal["desc", "asc"] = "desc"
) -> list[Appointment]:
    """
    Fetch appointments from DynamoDB by scanning appointment items and filtering
    RemainingPaymentDate or DownPaymentDate in the requested month.
    """

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    table = dynamodb.Table(os.getenv("TABLE_NAME"))

    # Month boundaries
    start_date = datetime.datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime.datetime(year, month, last_day, 23, 59, 59)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    filter_expression = Attr("pk").begins_with("Appointment#") & (
        Attr("RemainingPaymentDate").between(start_str, end_str)
        | Attr("DownPaymentDate").between(start_str, end_str)
    )

    items = []
    response = table.scan(FilterExpression=filter_expression)
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=filter_expression,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))

    appointments = [Appointment(**item) for item in items]
    appointments.sort(key=lambda a: a.ServiceDateTime, reverse=(order == "desc"))
    return appointments
