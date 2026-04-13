import streamlit as st
import boto3
import os
from dotenv import load_dotenv
import uuid

from styles.markdown import markdown
from dynamo.client import get_clients, save_client
from models.client import Client
from models.source import SourceEnum


load_dotenv(dotenv_path=".env", override=True)


def on_dismiss_dialog():
    st.session_state.show_client_dialog = False
    st.session_state.editing_client = None


@st.dialog("Save client", on_dismiss=on_dismiss_dialog)
def show_client_dialog():
    editing: Client = st.session_state.get("editing_client")

    client_name = st.text_input("Nombre", value=editing.Name if editing else "")
    client_phone = st.text_input("Teléfono", value=editing.Phone if editing else "")
    client_instagram = st.text_input(
        "Instagram", value=editing.Instagram if editing else ""
    )
    client_source = st.selectbox(
        "Fuente",
        source_values := SourceEnum.values(),
        index=(
            source_values.index(editing.Source.value)
            if editing and editing.Source
            else 0
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save", use_container_width=True):
            if client_name.strip():
                if editing:
                    client_data = {
                        "pk": editing.pk,
                        "sk": editing.sk,
                        "Name": client_name,
                        "Phone": client_phone,
                        "Instagram": client_instagram,
                        "Source": client_source,
                    }
                    save_client(client_data)
                    st.success("Client updated!")
                else:
                    client_data = {
                        "pk": "Client",
                        "sk": str(uuid.uuid4()),
                        "Name": client_name,
                        "Phone": client_phone,
                        "Instagram": client_instagram,
                        "Source": client_source,
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
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
        markdown(h1, "Nombre")
        markdown(h2, "Teléfono")
        markdown(h3, "Instagram")
        markdown(h4, "Fuente")
        h4.markdown("")

        for client in clients:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

            col1.write(client.Name)
            col2.write(client.Phone)
            col3.write(client.Instagram)
            col4.write(client.Source.value or "")

            if col5.button("✏️", key=f"edit_{client.sk}"):
                st.session_state.editing_client = client
                st.session_state.show_client_dialog = True
                st.rerun()
    else:
        st.info("No clients found.")


if __name__ == "__main__":
    display_clients_page()
