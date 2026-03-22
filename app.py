import boto3
import os
from dotenv import load_dotenv
import streamlit as st
import datetime
import calendar

from dynamo.appointment import get_appointments_by_month_from_dynamo


# Load environment variables from .env file (force override, explicit path)
load_dotenv(dotenv_path=".env", override=True)


st.set_page_config(page_title="Dashboard", layout="wide")

st.subheader("📅 Calendar")

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
# ...existing code...
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
                for appt in appt_items:
                    st.markdown(
                        f"""
                        <div style='background:#fff;border-radius:12px;padding:16px 12px;margin:6px 0;font-size:1.05em;box-shadow:0 2px 8px rgba(0,0,0,0.08);color:#222;'>
                            {appt.Client.ClientName}<br>
                            {str(appt.sk)[11:]}<br>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
