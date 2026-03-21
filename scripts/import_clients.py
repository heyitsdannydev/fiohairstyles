import boto3
import os
import csv
import datetime
from dotenv import load_dotenv

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


def import_clients_from_csv():
    """Import clients from clients.csv file to DynamoDB."""
    csv_file_path = os.path.join(os.path.dirname(__file__), "clients.csv")
    table = get_dynamodb_table()

    try:
        with open(csv_file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            # Get the actual column headers
            if csv_reader.fieldnames:
                print(f"CSV columns found: {csv_reader.fieldnames}")

            count = 0

            for row in csv_reader:
                # Try different possible column names
                client_name = (
                    row.get("Clienta ", "")
                    or row.get("clienta", "")
                    or row.get("Client", "")
                    or row.get("Name", "")
                ).strip()

                if client_name:
                    client_data = {
                        "pk": "Client",
                        "sk": datetime.datetime.now().isoformat(),
                        "Name": client_name,
                        "Phone": "",
                        "Instagram": "",
                    }

                    table.put_item(Item=client_data)
                    count += 1
                    print(f"✓ Imported: {client_name}")

            print(f"\n✅ Successfully imported {count} clients!")

    except FileNotFoundError:
        print(f"❌ Error: clients.csv file not found at {csv_file_path}")
    except Exception as e:
        print(f"❌ Error importing clients: {e}")


if __name__ == "__main__":
    import_clients_from_csv()
