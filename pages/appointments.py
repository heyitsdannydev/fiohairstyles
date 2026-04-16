from pages.dialogs.create_appointment_dialog import create_appointment_dialog
import streamlit as st
from dotenv import load_dotenv
import datetime

from styles.markdown import markdown
from dynamo.appointment import (
    get_appointments_by_month_from_dynamo,
    delete_appointment,
)
from pages.dialogs.create_client_dialog import create_client_dialog

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


def display_appointments_page():
    """Display the appointments page with list and create functionality."""
    st.set_page_config(layout="wide")

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
    if "show_client_dialog" not in st.session_state:
        st.session_state.show_client_dialog = False

    # Create appointment button
    if st.button("➕ Create Appointment", key="create_btn"):
        st.session_state.show_appointment_dialog = True
        st.session_state.editing_appointment = None
        st.session_state.show_client_dialog = False

    search_term = st.text_input(
        "Search",
        value=st.session_state.get("appointment_search", ""),
        key="appointment_search",
        width=180,
    ).strip()

    if st.session_state.get("show_appointment_dialog", False):
        create_appointment_dialog()
    if st.session_state.get("show_client_dialog", False):
        create_client_dialog()

    st.divider()

    # Fetch and display appointments table
    appointments = get_appointments_by_month_from_dynamo(
        st.session_state.current_month,
        st.session_state.current_year,
        order="desc",
        only_future=True,
    )
    if search_term:
        appointments = [
            appointment
            for appointment in appointments
            if search_term.lower() in (appointment.Client.ClientName or "").lower()
        ]
    if appointments:
        (h1, h2, h3, h4, h5, h6, h7) = st.columns([2, 2, 2, 2, 2, 1, 1])
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
