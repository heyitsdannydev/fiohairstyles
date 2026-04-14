import streamlit as st
import uuid

from dynamo.client import save_client
from models.client import Client
from models.source import SourceEnum


def on_dismiss_dialog():
    st.session_state.show_client_dialog = False
    st.session_state.editing_client = None


@st.dialog("Save client", on_dismiss=on_dismiss_dialog)
def create_client_dialog():
    editing: Client = st.session_state.get("editing_client")

    client_name = st.text_input("Nombre", value=editing.Name if editing else "").strip()
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
            client_data = {
                "pk": "Client",
                "sk": str(uuid.uuid4()) if not editing else editing.sk,
                "Name": client_name,
                "Phone": client_phone,
                "Instagram": client_instagram,
                "Source": client_source,
            }
            save_client(client_data)
            st.success("Client created!")
            st.session_state.show_client_dialog = False
            st.session_state.show_client_dialog = False
            st.session_state.editing_client = None
            if st.session_state.get("go_back_to_appointment_dialog", False):
                st.session_state.show_appointment_dialog = True
                st.session_state.go_back_to_appointment_dialog = False
                st.session_state.go_back_to_appointment_dialog_client_name = client_name
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_client_dialog = False
            st.session_state.editing_client = None
            st.rerun()
