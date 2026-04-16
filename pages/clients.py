import streamlit as st
from dotenv import load_dotenv

from styles.markdown import markdown
from dynamo.client import get_clients, delete_client
from pages.dialogs.create_client_dialog import create_client_dialog


load_dotenv(dotenv_path=".env", override=True)


def display_clients_page():
    st.set_page_config(layout="wide")

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
        create_client_dialog()

    search_term = st.text_input(
        "Search",
        value=st.session_state.get("client_search", ""),
        key="client_search",
        width=130,
    ).strip()

    st.divider()

    # Clients list
    clients = get_clients()

    if search_term:
        clients = [
            client
            for client in clients
            if search_term.lower() in (client.Name or "").lower()
        ]

    if clients:
        # Header row
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
        markdown(h1, "Nombre")
        markdown(h2, "Teléfono")
        markdown(h3, "Instagram")
        markdown(h4, "Fuente")
        h4.markdown("")

        for client in clients:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])

            col1.write(client.Name)
            col2.write(client.Phone)
            col3.write(client.Instagram)
            col4.write(client.Source.value or "")

            if col5.button("✏️", key=f"edit_{client.sk}"):
                st.session_state.editing_client = client
                st.session_state.show_client_dialog = True
                st.rerun()
            if col6.button("🗑️", key=f"delete_{client.sk}"):
                delete_client(client.sk)
                st.success("Client deleted!")
                st.rerun()
    else:
        st.info("No clients found.")


if __name__ == "__main__":
    display_clients_page()
