import streamlit as st
import datetime
from decimal import Decimal
from loguru import logger

from models.appointment import Appointment
from dynamo.appointment import (
    save_appointment,
)
from dynamo.client import get_clients
from pages.dialogs.create_client_dialog import create_client_dialog


def on_dismiss_dialog():
    st.session_state.show_appointment_dialog = False
    st.session_state.editing_appointment = None
    st.session_state.show_client_dialog = False


@st.dialog("Save Appointment", on_dismiss=on_dismiss_dialog)
def create_appointment_dialog():
    """Display create/edit appointment form in a popup dialog."""
    editing: Appointment = st.session_state.get("editing_appointment")

    if "show_client_dialog" not in st.session_state:
        st.session_state.show_client_dialog = False

    dt = editing.ServiceDateTime if editing else datetime.datetime.now()

    st.markdown("# Clienta")
    col1, col2 = st.columns(2)
    with col1:
        clients = {c.Name: c.sk for c in get_clients()}

        client_names = list(clients.keys())
        selected_client_name = st.session_state.get(
            "go_back_to_appointment_dialog_client_name", None
        )
        if selected_client_name and selected_client_name in client_names:
            index = client_names.index(selected_client_name)
        else:
            index = client_names.index(editing.Client.ClientName) if editing else 0

        client_name = st.selectbox(
            "Clienta",
            client_names,
            index=index,
            key="dialog_client_name",
        )
        if st.button("➕", key="dialog_new_client_btn"):
            st.session_state.show_client_dialog = True
            st.session_state.show_appointment_dialog = False
            st.session_state.go_back_to_appointment_dialog = True
            st.rerun()
    with col2:
        address = st.text_input(
            "Domicilio",
            value=editing.Address if editing else "",
            key="dialog_address",
        )

    if st.session_state.get("show_client_dialog", False):
        create_client_dialog()

    st.markdown("# Horario")
    col1, col2 = st.columns(2)
    with col1:
        service_date = st.date_input(
            "Fecha", value=dt.date(), key="dialog_service_date"
        )
    with col2:
        service_time = st.time_input("Hora", value=dt.time(), key="dialog_service_time")

    st.markdown("# Servicio")
    col1, col2, col3 = st.columns([2, 1, 1])
    services = [
        "Peinado Social",
        "Pack novia",
        "P&Mk Social",
        "Maquilalje Social",
        "Ondas",
        "Quinceañera",
        "Novia Civil P&Mk",
    ]
    service_index = services.index(editing.Service) if editing else 0
    with col1:
        service = st.selectbox(
            "Servicio", services, index=service_index, key="dialog_service"
        )
    with col2:
        service_price = st.number_input(
            "Precio",
            min_value=0,
            step=1,
            value=int(editing.ServicePrice) if editing else 1,
            key="dialog_service_price",
        )
    with col3:
        transportation = st.number_input(
            "Transporte",
            min_value=0,
            step=1,
            value=getattr(editing, "Transportation", 1) if editing else 1,
            key="dialog_transportation",
        )

    st.markdown("# Seña")
    down_payment_percentage_options = ["0%", "20%", "50%"]
    dp_index = 0
    if editing and getattr(editing, "DownPaymentPercentage", None) is not None:
        existing_dp = f"{int(editing.DownPaymentPercentage)}%"
        if existing_dp in down_payment_percentage_options:
            dp_index = down_payment_percentage_options.index(existing_dp)

    down_payment_percentage_str = st.selectbox(
        "% de seña",
        down_payment_percentage_options,
        index=dp_index,
        key="dialog_down_payment_percentage",
    )
    down_payment_percentage = Decimal(down_payment_percentage_str.replace("%", ""))

    st.markdown("# Método de pago")
    payment_methods = ["Itaú", "BROU"]
    pm_index = (
        payment_methods.index(editing.PaymentMethod)
        if editing and editing.PaymentMethod
        else 0
    )

    payment_method = st.selectbox(
        "Método de pago",
        payment_methods,
        index=pm_index,
        key="dialog_payment_method",
    )

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Save Appointment", key="dialog_save_btn", use_container_width=True
        ):
            logger.info(f"Saving appointment")
            service_datetime = datetime.datetime.combine(service_date, service_time)
            client_id = clients[client_name]

            logger.info(f"{service_datetime=} {client_id=}")

            appointment_data = {
                "pk": f"Appointment#{service_datetime.strftime("%Y-%m")}",
                "sk": service_datetime.isoformat(),
                "Client": {
                    "ClientName": client_name,
                    "ClientId": client_id,
                },
                "Address": address,
                "ServiceDateTime": service_datetime.isoformat(),
                "Service": service,
                "ServicePrice": Decimal(str(service_price)),
                "Transportation": transportation,
                "DownPaymentPercentage": down_payment_percentage,
                "PaymentMethod": payment_method,
                "Source": "Profesora",
            }
            logger.info(f"Appointment data to save: {appointment_data}")
            save_appointment(
                appointment_data,
                old_sk=editing.sk.isoformat() if editing else None,
                new_sk=service_datetime.isoformat(),
            )
            st.success("Appointment saved successfully!")

            st.session_state.show_appointment_dialog = False
            st.session_state.editing_appointment = None
            st.rerun()

    with col2:
        if st.button("Cancel", key="dialog_cancel_btn", use_container_width=True):
            st.session_state.show_appointment_dialog = False
            st.session_state.editing_appointment = None
            st.rerun()
