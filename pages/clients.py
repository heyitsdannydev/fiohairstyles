import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import uuid

from styles.markdown import markdown

# Load environment variables
load_dotenv(dotenv_path=".env", override=True)


# ---------------------------
# DynamoDB
# ---------------------------
def get_dynamodb_table():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return dynamodb.Table(os.getenv("TABLE_NAME"))


def get_clients() -> List[Dict[str, Any]]:
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
    try:
        table = get_dynamodb_table()
        table.put_item(Item=client_data)
        return True
    except Exception as e:
        st.error(f"Error saving client: {e}")
        return False


def update_client(client_data: Dict[str, Any]) -> bool:
    """Overwrite existing client (same pk/sk)."""
    try:
        table = get_dynamodb_table()
        table.put_item(Item=client_data)
        return True
    except Exception as e:
        st.error(f"Error updating client: {e}")
        return False


# ---------------------------
# Dialog (Create + Edit)
# ---------------------------
@st.dialog("Save client")
def show_client_dialog():
    editing = st.session_state.get("editing_client")

    # Prefill values if editing
    default_name = editing.get("Name", "") if editing else ""
    default_phone = editing.get("Phone", "") if editing else ""
    default_instagram = editing.get("Instagram", "") if editing else ""

    client_name = st.text_input("Nombre", value=default_name)
    client_phone = st.text_input("Teléfono", value=default_phone)
    client_instagram = st.text_input("Instagram", value=default_instagram)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save", use_container_width=True):
            if client_name.strip():
                if editing:
                    # UPDATE
                    client_data = {
                        "pk": editing["pk"],
                        "sk": editing["sk"],
                        "Name": client_name,
                        "Phone": client_phone,
                        "Instagram": client_instagram,
                    }
                    update_client(client_data)
                    st.success("Client updated!")
                else:
                    # CREATE
                    client_data = {
                        "pk": "Client",
                        "sk": str(uuid.uuid4()),
                        "Name": client_name,
                        "Phone": client_phone,
                        "Instagram": client_instagram,
                    }
                    save_client(client_data)
                    st.success("Client created!")

                st.session_state.show_client_dialog = False
                st.session_state.editing_client = None
                st.rerun()
            else:
                st.error("Name is required.")

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_client_dialog = False
            st.session_state.editing_client = None
            st.rerun()


# ---------------------------
# UI
# ---------------------------
def display_clients_page():
    st.set_page_config(page_title="Clients", layout="wide")
    st.title("👥 Clients")

    # Init session state
    if "show_client_dialog" not in st.session_state:
        st.session_state.show_client_dialog = False
    if "editing_client" not in st.session_state:
        st.session_state.editing_client = None

    # Create button
    if st.button("➕ Create client"):
        st.session_state.editing_client = None
        st.session_state.show_client_dialog = True

    # Show dialog
    if st.session_state.get("show_client_dialog", False):
        show_client_dialog()

    st.divider()

    # Clients list
    clients = get_clients()

    if clients:
        # Header row
        h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
        markdown(h1, "Nombre")
        markdown(h2, "Teléfono")
        markdown(h3, "Instagram")
        h4.markdown("")

        for client in clients:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            col1.write(client.get("Name", "Unknown"))
            col2.write(client.get("Phone", ""))
            col3.write(client.get("Instagram", ""))

            if col4.button("✏️", key=f"edit_{client['sk']}"):
                st.session_state.editing_client = client
                st.session_state.show_client_dialog = True
                st.rerun()
    else:
        st.info("No clients found.")


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    display_clients_page()
