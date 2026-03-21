import boto3
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables from .env file (force override, explicit path)
load_dotenv(dotenv_path=".env", override=True)


def get_appointments_from_dynamo(month: int, year: int) -> List[Dict[str, Any]]:
    """
    Fetch appointments from DynamoDB where pk=Appointments and filter by month/year.
    """
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    table_name = os.getenv("TABLE_NAME")
    table = dynamodb.Table(table_name)
    try:
        # Calculate start and end of month for sk
        start_date = datetime.datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime.datetime(year, month, last_day, 23, 59, 59)
        start_sk = start_date.strftime("%Y-%m-%dT00:00:00")
        end_sk = end_date.strftime("%Y-%m-%dT23:59:59")
        response = table.query(
            KeyConditionExpression="pk = :pk AND sk BETWEEN :start_sk AND :end_sk",
            ExpressionAttributeValues={
                ":pk": "Appointment",
                ":start_sk": start_sk,
                ":end_sk": end_sk,
            },
        )
        items = response.get("Items", [])
        return items
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return []


import streamlit as st
import datetime
import calendar

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

with col1:
    if st.button("← Previous"):
        if st.session_state.current_month == 1:
            st.session_state.current_month = 12
            st.session_state.current_year -= 1
        else:
            st.session_state.current_month -= 1

with col2:
    st.write(
        f"### {datetime.date(st.session_state.current_year, st.session_state.current_month, 1).strftime('%B %Y')}"
    )

with col3:
    if st.button("Next →"):
        if st.session_state.current_month == 12:
            st.session_state.current_month = 1
            st.session_state.current_year += 1
        else:
            st.session_state.current_month += 1

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


appointments = get_appointments_from_dynamo(
    st.session_state.current_month, st.session_state.current_year
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
                appt_items = [
                    a
                    for a in appointments
                    if int(
                        a.get("sk", "1970-01-01T00:00:00").split("-")[2].split("T")[0]
                    )
                    == day
                ]
                for appt in appt_items:
                    st.markdown(
                        f"""
                        <div style='background:#fff;border-radius:12px;padding:16px 12px;margin:6px 0;font-size:1.05em;box-shadow:0 2px 8px rgba(0,0,0,0.08);color:#222;'>
                            {appt.get('Client', {}).get('ClientName', 'Unknown')}<br>
                            {str(appt.get('sk', ''))[11:]}<br>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
