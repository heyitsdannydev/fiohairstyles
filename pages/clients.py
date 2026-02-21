import streamlit as st
import boto3
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_clients_from_dynamo() -> List[Dict[str, Any]]:
    """
    Fetch all clients from DynamoDB where pk=Client.

    Returns:
        List of client dictionaries
    """
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    table_name = "fiohairstyles"
    table = dynamodb.Table(table_name)

    try:
        # Query for all items with pk=Client
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "Client"},
        )

        return response.get("Items", [])
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return []


def display_clients_page():
    """Display the clients page with all clients from DynamoDB."""
    st.set_page_config(page_title="Clients", layout="wide")

    st.title("👥 Clients")

    try:
        clients = get_clients_from_dynamo()

        if clients:
            st.markdown(
                f"<h2 style='text-align:center;margin-bottom:0;'>Total Clients: <span style='color:#4F8CFF'>{len(clients)}</span></h2>",
                unsafe_allow_html=True,
            )
            st.divider()

            # Pagination logic
            page_size = 10
            total_pages = (len(clients) - 1) // page_size + 1
            if "page" not in st.session_state:
                st.session_state["page"] = 1
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.button("⬅️", key="prev") and st.session_state["page"] > 1:
                    st.session_state["page"] -= 1
            with nav_col2:
                st.markdown(
                    f"<div style='text-align:center;font-size:1.2em;'>Page <b>{st.session_state['page']}</b> of <b>{total_pages}</b></div>",
                    unsafe_allow_html=True,
                )
            with nav_col3:
                if (
                    st.button("➡️", key="next")
                    and st.session_state["page"] < total_pages
                ):
                    st.session_state["page"] += 1
            page = st.session_state["page"]
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_clients = clients[start_idx:end_idx]

            st.divider()
            for client in paginated_clients:
                with st.container():
                    client_cols = st.columns([1, 2])
                    with client_cols[0]:
                        st.markdown(
                            f"<div style='background:#F0F4FF;border-radius:8px;padding:16px;margin-bottom:8px;'>"
                            f"<b>Name:</b> <span style='color:#222'>{client.get('Name', 'Unknown')}</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
            st.divider()
        else:
            st.info("No clients found in the database")

    except Exception as e:
        st.error(f"Error fetching clients: {e}")


# Run the page
if __name__ == "__main__":
    display_clients_page()
