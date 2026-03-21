import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import datetime
from decimal import Decimal
from loguru import logger

from models.appointment import Appointment
from styles.markdown import markdown

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
    return dynamodb.Table(os.getenv("TABLE_NAME"))


def get_appointments() -> list[Appointment]:
    """Fetch all appointments from DynamoDB where pk=Appointment, ordered by date desc."""
    try:
        table = get_dynamodb_table()
        response = table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "Appointment"},
        )
        appointments = response.get("Items", [])
        # Sort by ServiceDateTime in descending order
        appointments.sort(key=lambda x: x.get("ServiceDateTime", ""), reverse=True)
        return [Appointment(**a) for a in appointments]
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []


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


def save_appointment(appointment_data: Dict[str, Any]) -> bool:
    """Save appointment to DynamoDB."""
    try:
        table = get_dynamodb_table()
        res = table.put_item(Item=appointment_data)
        logger.info(f"Saving {appointment_data=} {res=}")
        return True
    except Exception as e:
        st.error(f"Error saving appointment: {e}")
        return False


@st.dialog("Save Appointment")
def show_create_appointment_dialog():
    """Display create/edit appointment form in a popup dialog."""
    editing: Appointment = st.session_state.get("editing_appointment")
    logger.info(f"{editing=}")

    # Row 1: Select Client | Address
    col1, col2 = st.columns(2)
    with col1:
        _clients = get_clients()
        clients = {c["Name"]: c["sk"] for c in _clients}

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
        down_payment_date = st.date_input(
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
        remaining_payment_date = st.date_input(
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
            client = clients[client_name]

            logger.info(f"{service_datetime=} {client=}")

            appointment_data = {
                "pk": "Appointment",
                "sk": (
                    editing.sk.isoformat()
                    if editing
                    else datetime.datetime.now().isoformat()
                ),
                "Client": {
                    "ClientName": client_name,
                    "ClientId": client,
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
            }
            logger.info(f"Appointment data to save: {appointment_data}")
            save_appointment(appointment_data)
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
    appointments = get_appointments()
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
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = (
                st.columns([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1])
            )

            # Clienta Servicio Fecha Direccion Total Seña Resto Metodo de pago

            col1.write(appointment.Client.ClientName)
            col2.write(appointment.Service)
            col3.write(appointment.ServiceDateTime.strftime("%d %b %Y %H:%M"))
            col4.write(f"${appointment.Total:.2f}")
            col5.write(appointment.Address or "")
            col6.write(appointment.PaymentMethod)
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

            if col11.button("✏️", key=f"edit_{appointment.sk}"):
                st.session_state.editing_appointment = appointment
                st.session_state.show_appointment_dialog = True
                st.rerun()
    else:
        st.info("No appointments found.")


# Run the page
if __name__ == "__main__":
    display_appointments_page()
