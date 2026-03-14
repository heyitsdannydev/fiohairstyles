import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import datetime
import uuid

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
    return dynamodb.Table("fiohairstyles")


def get_clients() -> List[Dict[str, Any]]:
    """Fetch all clients from DynamoDB where pk=Client."""
    try:
        table = get_dynamodb_table()
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "Client"},
        )
        return response.get("Items", [])
    except Exception as e:
        st.error(f"Error fetching clients: {e}")
        return []


def save_client(client_data: Dict[str, Any]) -> bool:
    """Save client to DynamoDB."""
    try:
        table = get_dynamodb_table()
        table.put_item(Item=client_data)
        return True
    except Exception as e:
        st.error(f"Error saving client: {e}")
        return False


@st.dialog("Create New Client")
def show_create_client_dialog():
    """Display create client form in a popup dialog."""
    client_name = st.text_input("Client Name", key="dialog_client_name")
    client_phone = st.text_input("Phone", key="dialog_client_phone")
    client_instagram = st.text_input("Instagram", key="dialog_client_instagram")

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Client", key="dialog_save_btn", use_container_width=True):
            if client_name.strip():
                client_data = {
                    "pk": "Client",
                    "sk": str(uuid.uuid4()),
                    "Name": client_name,
                    "Phone": client_phone,
                    "Instagram": client_instagram,
                }
                save_client(client_data)
                st.success("Client saved successfully!")
                st.session_state.show_dialog = False
                st.rerun()
            else:
                st.error("Please fill in required fields.")

    with col2:
        if st.button("Cancel", key="dialog_cancel_btn", use_container_width=True):
            st.session_state.show_dialog = False
            st.rerun()


def display_clients_page():
    """Display the clients page with list and create functionality."""
    st.set_page_config(page_title="Clients", layout="wide")
    st.title("👥 Clients")

    # Create client button
    if st.button("➕ Create Client", key="create_btn"):
        st.session_state.show_dialog = True

    if st.session_state.get("show_dialog", False):
        show_create_client_dialog()

    st.divider()

    # Fetch and display clients table
    clients = get_clients()
    if clients:

        import pandas as pd

        data = []
        for client in clients:
            data.append(
                {
                    "Name": client.get("Name", "Unknown"),
                    "Phone": client.get("Phone", ""),
                    "Instagram": client.get("Instagram", ""),
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No clients found.")


# Run the page
if __name__ == "__main__":
    display_clients_page()
