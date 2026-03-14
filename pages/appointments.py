import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import datetime
from decimal import Decimal

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


def get_appointments() -> List[Dict[str, Any]]:
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
        return appointments
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
        table.put_item(Item=appointment_data)
        return True
    except Exception as e:
        st.error(f"Error saving appointment: {e}")
        return False


@st.dialog("Create New Appointment")
def show_create_appointment_dialog():
    """Display create appointment form in a popup dialog."""
    # Row 1: Select Client | Address
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.selectbox(
            "Select Client",
            [c.get("Name", "") for c in get_clients()],
            key="dialog_client_name",
        )
    with col2:
        address = st.text_input("Address", key="dialog_address")

    # Row 2: Service Date (with hours)
    col1, col2 = st.columns(2)
    with col1:
        service_date = st.date_input("Service Date", key="dialog_service_date")
    with col2:
        service_time = st.time_input("Hours", key="dialog_service_time")

    # Row 3: Service | Total
    col1, col2 = st.columns(2)
    with col1:
        service = st.selectbox(
            "Service",
            ["Peinado Social", "Corte", "Color", "Tratamiento"],
            key="dialog_service",
        )
    with col2:
        total = st.number_input("Total", min_value=0.0, step=0.01, key="dialog_total")

    # Row 4: Down Payment | Down Payment Date
    col1, col2 = st.columns(2)
    with col1:
        down_payment = st.number_input(
            "Down Payment", min_value=0.0, step=0.01, key="dialog_down_payment"
        )
    with col2:
        down_payment_date = st.date_input(
            "Down Payment Date", key="dialog_down_payment_date"
        )

    # Row 5: Remaining | Remaining Payment Date
    col1, col2 = st.columns(2)
    with col1:
        remaining = st.number_input(
            "Remaining", min_value=0.0, step=0.01, key="dialog_remaining"
        )
    with col2:
        remaining_payment_date = st.date_input(
            "Remaining Payment Date", key="dialog_remaining_payment_date"
        )

    # Row 6: Payment Method
    payment_method = st.selectbox(
        "Payment Method",
        ["Itaú", "BROU", "Santander"],
        key="dialog_payment_method",
    )

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Save Appointment", key="dialog_save_btn", use_container_width=True
        ):
            if client_name and service:
                # Combine service date and time
                service_datetime = datetime.datetime.combine(service_date, service_time)

                appointment_data = {
                    "pk": "Appointment",
                    "sk": datetime.datetime.now().isoformat(),
                    "Client": client_name,
                    "Address": address,
                    "ServiceDateTime": service_datetime.isoformat(),
                    "Service": service,
                    "Total": Decimal(str(total)),
                    "DownPayment": Decimal(str(down_payment)),
                    "DownPaymentDate": down_payment_date.isoformat(),
                    "Remaining": Decimal(str(remaining)),
                    "RemainingPaymentDate": remaining_payment_date.isoformat(),
                    "PaymentMethod": payment_method,
                }
                save_appointment(appointment_data)
                st.success("Appointment saved successfully!")
                st.session_state.show_dialog = False
                st.rerun()
            else:
                st.error("Please fill in required fields.")

    with col2:
        if st.button("Cancel", key="dialog_cancel_btn", use_container_width=True):
            st.session_state.show_dialog = False
            st.rerun()


def display_appointments_page():
    """Display the appointments page with list and create functionality."""
    st.set_page_config(page_title="Appointments", layout="wide")
    st.title("📅 Appointments")

    # Create appointment button
    if st.button("➕ Create Appointment", key="create_btn"):
        st.session_state.show_dialog = True

    if st.session_state.get("show_dialog", False):
        show_create_appointment_dialog()

    st.divider()

    # Fetch and display appointments table
    appointments = get_appointments()
    if appointments:

        import pandas as pd

        data = []
        for appointment in appointments:
            data.append(
                {
                    "Clienta": appointment.get("Client", {}).get(
                        "ClientName", "Unknown"
                    ),
                    "Servicio": appointment.get("Service", ""),
                    "Fecha": appointment.get("ServiceDateTime", ""),
                    "Dirección": appointment.get("Address", ""),
                    "Total": f"${float(appointment.get('Total', 0)):.2f}",
                    "Seña": f"${float(appointment.get('DownPayment', 0)):.2f}",
                    "Resto": f"${float(appointment.get('Remaining', 0)):.2f}",
                    "Método de pago": appointment.get("PaymentMethod", ""),
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No appointments found.")


# Run the page
if __name__ == "__main__":
    display_appointments_page()
