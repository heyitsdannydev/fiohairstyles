import boto3
import os
import csv
import datetime
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


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


def get_client_by_name(table, client_name: str):
    """Find client in DynamoDB by name and return their sk (id)."""
    try:
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "Client"},
        )
        clients = response.get("Items", [])

        for client in clients:
            if client.get("Name", "").lower() == client_name.lower():
                return client.get("sk")
    except Exception as e:
        print(f"Error searching for client: {e}")

    return None


def import_appointments_from_csv():
    """Import appointments from clients.csv file to DynamoDB."""
    csv_file_path = os.path.join(os.path.dirname(__file__), "clients_parsed.csv")
    table = get_dynamodb_table()

    try:
        with open(csv_file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            if csv_reader.fieldnames:
                print(f"CSV columns found: {csv_reader.fieldnames}\n")

            count = 0
            skipped = 0

            for row in csv_reader:
                client_name = (row.get("Client", "") or row.get("client", "")).strip()
                service_date = (
                    row.get("ServiceDateTime", "") or row.get("serviceDateTime", "")
                ).strip()
                service = (row.get("Service", "") or row.get("service", "")).strip()
                total = (row.get("Total", "") or row.get("total", "")).strip()
                address = (row.get("Address", "") or row.get("address", "")).strip()
                down_payment = (
                    row.get("DownPayment", "") or row.get("downPayment", "")
                ).strip()
                down_payment_date = (
                    row.get("DownPaymentDate", "") or row.get("downPaymentDate", "")
                ).strip()
                remaining = (
                    row.get("Remaining", "") or row.get("remaining", "")
                ).strip()
                remaining_payment_date = (
                    row.get("RemainingPaymentDate", "")
                    or row.get("remainingPaymentDate", "")
                ).strip()
                payment_method = (
                    row.get("PaymentMethod", "") or row.get("paymentMethod", "")
                ).strip()

                # Skip if no client name or service
                if not client_name or not service:
                    skipped += 1
                    continue

                # Find client ID by name
                client_id = get_client_by_name(table, client_name)

                if not client_id:
                    print(f"⚠️  Skipped: Client '{client_name}' not found in database")
                    skipped += 1
                    continue

                # Convert numeric fields
                try:
                    total_val = Decimal(str(total)) if total else Decimal("0")
                    down_payment_val = (
                        Decimal(str(down_payment)) if down_payment else Decimal("0")
                    )
                    remaining_val = (
                        Decimal(str(remaining)) if remaining else Decimal("0")
                    )
                except:
                    total_val = Decimal("0")
                    down_payment_val = Decimal("0")
                    remaining_val = Decimal("0")

                appointment_data = {
                    "pk": "Appointment",
                    "sk": service_date,
                    "Client": {
                        "ClientId": client_id,
                        "ClientName": client_name,
                    },
                    "ServiceDateTime": service_date if service_date else "",
                    "Service": service,
                    "Address": address,
                    "Total": total_val,
                    "DownPayment": down_payment_val,
                    "DownPaymentDate": down_payment_date if down_payment_date else "",
                    "Remaining": remaining_val,
                    "RemainingPaymentDate": (
                        remaining_payment_date if remaining_payment_date else ""
                    ),
                    "PaymentMethod": payment_method,
                }

                table.put_item(Item=appointment_data)
                count += 1
                print(f"{appointment_data=}")

            print(f"\n✅ Successfully imported {count} appointments!")
            if skipped > 0:
                print(f"⚠️  Skipped {skipped} rows (missing data or client not found)")

    except FileNotFoundError:
        print(f"❌ Error: clients.csv file not found at {csv_file_path}")
    except Exception as e:
        print(f"❌ Error importing appointments: {e}")


if __name__ == "__main__":
    import_appointments_from_csv()
