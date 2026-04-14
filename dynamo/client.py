from dynamo.dynamo import get_dynamodb_table
from models.client import Client


def get_clients() -> list[Client]:
    """Fetch all clients from DynamoDB where pk=Client."""
    table = get_dynamodb_table()
    response = table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "Client"},
    )
    return [Client(**item) for item in response.get("Items", [])]


def save_client(client_data: dict) -> bool:
    table = get_dynamodb_table()
    table.put_item(Item=client_data)
    return True


def delete_client(sk: str) -> bool:
    """Delete client from DynamoDB."""
    table = get_dynamodb_table()
    table.delete_item(Key={"pk": "Client", "sk": sk})
    return True
