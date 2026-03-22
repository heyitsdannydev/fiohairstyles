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
from dynamo.appointment import get_appointments_by_month_from_dynamo, save_appointment
from dynamo.client import get_clients

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


@st.dialog("Save Appointment")
def show_create_appointment_dialog():
    """Display create/edit appointment form in a popup dialog."""
    editing: Appointment = st.session_state.get("editing_appointment")

    # Row 1: Select Client | Address
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

    dt = editing.ServiceDateTime if editing else datetime.datetime.now()

    # Row 2: Service Date (with hours)
    col1, col2 = st.columns(2)
    with col1:
        service_date = st.date_input(
            "Fecha", value=dt.date(), key="dialog_service_date"
        )
    with col2:
        service_time = st.time_input("Hora", value=dt.time(), key="dialog_service_time")

    # Row 3: Service | Total
    services = [
        "Peinado Social",
        "Pack novia",
        "P&Mk Social",
        "Maquilalje Social",
        "Ondas",
    ]
    service_index = services.index(editing.Service) if editing else 0

    col1, col2 = st.columns(2)
    with col1:
        service = st.selectbox(
            "Servicio", services, index=service_index, key="dialog_service"
        )
    with col2:
        total = st.number_input(
            "Total",
            min_value=0.0,
            step=0.01,
            value=float(editing.Total) if editing else 0.0,
            key="dialog_total",
        )

    # Row 4: Down Payment | Down Payment Date
    col1, col2 = st.columns(2)
    with col1:
        down_payment = st.number_input(
            "Seña",
            min_value=0.0,
            step=0.01,
            value=editing.DownPayment if editing else 0.0,
            key="dialog_down_payment",
        )
    with col2:
        down_payment_date: datetime.date = st.date_input(
            "Fecha seña",
            value=(
                editing.DownPaymentDate
                if editing and editing.DownPaymentDate
                else datetime.date.today()
            ),
            key="dialog_down_payment_date",
        )

    # Row 5: Remaining Payment Date
    col1, col2 = st.columns(2)
    with col1:
        remaining_payment_date: datetime.date = st.date_input(
            "Fecha resto",
            value=(editing.RemainingPaymentDate if editing else datetime.date.today()),
            key="dialog_remaining_payment_date",
        )

    # Row 6: Payment Method
    payment_methods = ["Itaú", "BROU"]
    pm_index = payment_methods.index(editing.PaymentMethod) if editing else 0

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
                "pk": "Appointment",
                "sk": service_datetime.isoformat(),
                "Client": {
                    "ClientName": client_name,
                    "ClientId": client_id,
                },
                "Address": address,
                "ServiceDateTime": service_datetime.isoformat(),
                "Service": service,
                "Total": Decimal(str(total)),
                "DownPayment": Decimal(str(down_payment)),
                "DownPaymentDate": down_payment_date.isoformat(),
                "Remaining": Decimal(str(total - down_payment)),
                "RemainingPaymentDate": remaining_payment_date.isoformat(),
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

    # Create appointment button
    if st.button("➕ Create Appointment", key="create_btn"):
        st.session_state.show_appointment_dialog = True
        st.session_state.editing_appointment = None

    if st.session_state.get("show_appointment_dialog", False):
        show_create_appointment_dialog()

    st.divider()

    # Fetch and display appointments table
    appointments = get_appointments_by_month_from_dynamo(
        st.session_state.current_month, st.session_state.current_year, order="desc"
    )
    if appointments:
        h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11 = st.columns(
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
        )
        # DownPayment DownPaymentDate Remaining RemainingPaymentDate
        markdown(h1, "Clienta")
        markdown(h2, "Servicio")
        markdown(h3, "Fecha")
        markdown(h4, "Total")
        markdown(h5, "Domicilio")
        markdown(h6, "Método de pago")
        markdown(h7, "Seña")
        markdown(h8, "Fecha seña")
        markdown(h9, "Resto")
        markdown(h10, "Fecha resto")
        h11.markdown("")
        for appointment in appointments:
            (
                col1,
                col2,
                col3,
                col4,
                col5,
                col6,
                col7,
                col8,
                col9,
                col10,
                col11,
            ) = st.columns([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1])

            # Clienta Servicio Fecha Direccion Total Seña Resto Metodo de pago

            col1.write(appointment.Client.ClientName)
            col2.write(appointment.Service)
            col3.write(appointment.ServiceDateTime.strftime("%d %b %Y %H:%M"))
            col4.write(f"${appointment.Total:.2f}")
            col5.write(appointment.Address or "")
            col6.write(appointment.PaymentMethod or "")
            col7.write(f"${appointment.DownPayment:.2f}")
            col8.write(
                appointment.DownPaymentDate.strftime("%d %b %Y")
                if appointment.DownPaymentDate
                else ""
            )
            col9.write(f"${appointment.Remaining:.2f}")
            col10.write(
                appointment.RemainingPaymentDate.strftime("%d %b %Y")
                if appointment.RemainingPaymentDate
                else ""
            )

            if col11.button("✏️", key=f"edit_{appointment.pk}_{appointment.sk}"):
                st.session_state.editing_appointment = appointment
                st.session_state.show_appointment_dialog = True
                st.rerun()
    else:
        st.info("No appointments found.")


# Run the page
if __name__ == "__main__":
    display_appointments_page()
