import streamlit as st
from dotenv import load_dotenv


pages = {
    "Appointments": [
        st.Page("pages/appointments.py", title="See appointments"),
        st.Page("pages/calendar.py", title="Calendar"),
        st.Page(
            "pages/appointment_detail.py",
            title="Appointment detail",
        ),
    ],
    "Clients": [
        st.Page("pages/clients.py", title="See clients"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()


# Load environment variables from .env file (force override, explicit path)
load_dotenv(dotenv_path=".env", override=True)
