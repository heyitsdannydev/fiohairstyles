from uuid import uuid4
import streamlit as st
import boto3
import os
from dotenv import load_dotenv
import datetime
from decimal import Decimal
from loguru import logger

from models.appointment import Appointment
from models.source import SourceEnum
from styles.markdown import markdown
from dynamo.appointment import (
    get_appointments_by_month_from_dynamo,
    save_appointment,
    delete_appointment,
)
from dynamo.client import get_clients

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


def on_dismiss_dialog():
    st.session_state.show_appointment_dialog = False
    st.session_state.editing_appointment = None


@st.dialog("Save Appointment", on_dismiss=on_dismiss_dialog)
def show_create_appointment_dialog():
    """Display create/edit appointment form in a popup dialog."""
    editing: Appointment = st.session_state.get("editing_appointment")

    dt = editing.ServiceDateTime if editing else datetime.datetime.now()

    st.markdown("# Clienta")
    col1, col2 = st.columns(2)
    with col1:
        clients = {c.Name: c.sk for c in get_clients()}

        client_names = list(clients.keys())
        index = client_names.index(editing.Client.ClientName) if editing else 0

        client_name = st.selectbox(
            "Clienta",
            client_names,
            index=index,
            key="dialog_client_name",
        )
    with col2:
        address = st.text_input(
            "Domicilio",
            value=editing.Address if editing else "",
            key="dialog_address",
        )

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
    down_payment_percentage_options = ["20%", "50%"]
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
    # with col2:
    #     down_payment_date: datetime.date = st.date_input(
    #         "Fecha",
    #         value=(
    #             editing.DownPaymentDate
    #             if editing and editing.DownPaymentDate
    #             else datetime.date.today()
    #         ),
    #         key="dialog_down_payment_date",
    #     )
    # with col3:
    #     down_payment_done = st.checkbox(
    #         "Pagó seña",
    #         value=getattr(editing, "DownPaymentDone", False) if editing else False,
    #         key="dialog_down_payment_done",
    #     )

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

    # total = service_price + (float(transportation) if transportation else 0)
    # down_payment = (
    #     (Decimal(total) * down_payment_percentage / Decimal("100")).quantize(
    #         Decimal("1")
    #     )
    #     if down_payment_percentage
    #     else Decimal("0")
    # )

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
                "pk": f"Appointment#{client_id}",
                "sk": service_datetime.isoformat(),
                "Client": {
                    "ClientName": client_name,
                    "ClientId": client_id,
                },
                "Address": address,
                "ServiceDateTime": service_datetime.isoformat(),
                "Service": service,
                "ServicePrice": Decimal(str(service_price)),
                # "DownPayment": down_payment,
                # "DownPaymentDate": down_payment_date.isoformat(),
                # "DownPaymentDone": down_payment_done,
                "Transportation": transportation,
                "DownPaymentPercentage": down_payment_percentage,
                "PaymentMethod": payment_method,
                "Source": "Profesora",
                "gsi1_pk": "Appointment",
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


def display_appointments_page():
    """Display the appointments page with list and create functionality."""
    st.set_page_config(page_title="Appointments", layout="wide")
    st.title("📅 Appointments")

    # Get current date
    today = datetime.date.today()

    # Create columns for navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    # Initialize session state for month/year navigation
    if "current_month" not in st.session_state:
        st.session_state.current_month = today.month
    if "current_year" not in st.session_state:
        st.session_state.current_year = today.year
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        subcol1, subcol2, subcol3 = st.columns([1, 3, 1])

        with subcol1:
            if st.button("←"):
                if st.session_state.current_month == 1:
                    st.session_state.current_month = 12
                    st.session_state.current_year -= 1
                else:
                    st.session_state.current_month -= 1
                st.rerun()

        with subcol2:
            st.markdown(
                f"<h3 style='text-align:center;margin:0;'>"
                f"{datetime.date(st.session_state.current_year, st.session_state.current_month, 1).strftime('%B %Y')}"
                f"</h3>",
                unsafe_allow_html=True,
            )

        with subcol3:
            if st.button("→"):
                if st.session_state.current_month == 12:
                    st.session_state.current_month = 1
                    st.session_state.current_year += 1
                else:
                    st.session_state.current_month += 1
                st.rerun()

    if "editing_appointment" not in st.session_state:
        st.session_state.editing_appointment = None
    if "viewing_appointment" not in st.session_state:
        st.session_state.viewing_appointment = None

    # Create appointment button
    if st.button("➕ Create Appointment", key="create_btn"):
        st.session_state.show_appointment_dialog = True
        st.session_state.editing_appointment = None

    if st.session_state.get("show_appointment_dialog", False):
        show_create_appointment_dialog()

    st.divider()

    # Fetch and display appointments table
    appointments = get_appointments_by_month_from_dynamo(
        st.session_state.current_month,
        st.session_state.current_year,
        order="desc",
        only_future=True,
    )
    if appointments:
        (h1, h2, h3, h4, h5, h6, h7) = st.columns([2, 2, 2, 2, 2, 1, 1])
        # DownPayment DownPaymentDate Remaining RemainingPaymentDate
        markdown(h1, "Fecha")
        markdown(h2, "Hora")
        markdown(h3, "Clienta")
        markdown(h4, "Servicio")
        markdown(h5, "Dirección")
        h6.markdown("")
        h7.markdown("")
        for appointment in appointments:
            (
                col1,
                col2,
                col3,
                col4,
                col5,
                col6,
                col7,
            ) = st.columns([2, 2, 2, 2, 2, 1, 1])

            col1.write(appointment.ServiceDateTime.strftime("%d %b"))
            col2.write(appointment.ServiceDateTime.strftime("%H:%M"))
            if col3.button(
                appointment.Client.ClientName,
                key=f"view_{appointment.pk}_{appointment.sk}",
            ):
                st.session_state.selected_appointment = appointment
                st.switch_page("pages/appointment_detail.py")
                st.rerun()
            col4.write(appointment.Service or "")
            col5.write(appointment.Address or "")

            if col6.button("✏️", key=f"edit_{appointment.pk}_{appointment.sk}"):
                st.session_state.editing_appointment = appointment
                st.session_state.show_appointment_dialog = True
                st.rerun()
            if col7.button("🗑️", key=f"delete_{appointment.pk}_{appointment.sk}"):
                delete_appointment(appointment.pk, appointment.sk)
                st.success("Appointment deleted.")
                st.rerun()
    else:
        st.info("No appointments coming up just yet :)")


# Run the page
if __name__ == "__main__":
    display_appointments_page()
