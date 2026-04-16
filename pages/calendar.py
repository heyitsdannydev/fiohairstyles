import streamlit as st
import datetime
import calendar

from dynamo.appointment import get_appointments_by_month_from_dynamo
from pages.dialogs.create_appointment_dialog import create_appointment_dialog
from pages.dialogs.create_client_dialog import create_client_dialog


def display_calendar_page():

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
    if "show_appointment_dialog" not in st.session_state:
        st.session_state.show_appointment_dialog = False
    if "show_client_dialog" not in st.session_state:
        st.session_state.show_client_dialog = False

    if st.button("➕ Create Appointment", key="calendar_create_btn"):
        st.session_state.show_appointment_dialog = True
        st.session_state.editing_appointment = None
        st.session_state.show_client_dialog = False

    if st.session_state.get("show_appointment_dialog", False):
        create_appointment_dialog()
    if st.session_state.get("show_client_dialog", False):
        create_client_dialog()

    st.divider()

    # Generate calendar
    cal = calendar.monthcalendar(
        st.session_state.current_year, st.session_state.current_month
    )
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Display calendar header
    col_headers = st.columns(7)
    for i, day in enumerate(days_of_week):
        with col_headers[i]:
            st.write(f"**{day}**")

    appointments = get_appointments_by_month_from_dynamo(
        st.session_state.current_month,
        st.session_state.current_year,
        order="asc",
    )

    # Show all appointment fields in calendar day cell
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    # Highlight today
                    if (
                        day == today.day
                        and st.session_state.current_month == today.month
                        and st.session_state.current_year == today.year
                    ):
                        st.write(f"**{day}** 🔵")
                    else:
                        st.write(f"{day}")
                    # Show appointments for this day
                    appt_items = [a for a in appointments if int(a.sk.day) == day]
                    for appointment in appt_items:
                        if st.button(
                            f"{appointment.Client.ClientName} — {appointment.sk.strftime('%H:%M')} hs",
                            key=f"view_{appointment.pk}_{appointment.sk.strftime('%Y%m%dT%H%M%S')}",
                            use_container_width=True,
                        ):
                            st.session_state.selected_appointment = appointment
                            st.switch_page("pages/appointment_detail.py")
                            st.rerun()

    # if st.session_state.get("show_appointment_dialog", False):
    #     create_appointment_dialog()


if __name__ == "__main__":
    display_calendar_page()
