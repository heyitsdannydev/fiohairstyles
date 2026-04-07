import streamlit as st
from dotenv import load_dotenv
import datetime

from styles.markdown import markdown
from dynamo.appointment import get_appointments_by_income_from_dynamo

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)


def display_incomes_page():
    st.set_page_config(page_title="Incomes", layout="wide")
    st.title("💰 Incomes")

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

    st.divider()

    # Fetch and display appointments table
    appointments = get_appointments_by_income_from_dynamo(
        st.session_state.current_month, st.session_state.current_year, order="desc"
    )

    total_income = 0
    for appointment in appointments:
        if (
            appointment.DownPaymentDate
            and appointment.DownPaymentDate.month == st.session_state.current_month
            and appointment.DownPaymentDate.year == st.session_state.current_year
            and appointment.DownPayment
        ):
            total_income += appointment.DownPayment
        if (
            appointment.RemainingPaymentDate
            and appointment.RemainingPaymentDate.month == st.session_state.current_month
            and appointment.RemainingPaymentDate.year == st.session_state.current_year
            and appointment.Remaining
        ):
            total_income += appointment.Remaining

    st.markdown(f"<h2>Total income ${int(total_income)}</h2>", unsafe_allow_html=True)

    st.divider()

    if appointments:
        h1, h2, h3, h4, h5 = st.columns([2, 2, 2, 2, 2])
        markdown(h1, "Clienta")
        markdown(h2, "Servicio")
        markdown(h3, "Fecha")
        markdown(h4, "Total")
        markdown(h5, "Pagó")
        for appointment in appointments:
            if not appointment.DownPayment and not appointment.Remaining:
                continue
            (
                col1,
                col2,
                col3,
                col4,
                col5,
            ) = st.columns([2, 2, 2, 2, 2])

            col1.write(appointment.Client.ClientName)
            col2.write(appointment.Service)
            col3.write(appointment.ServiceDateTime.strftime("%d %b"))
            col4.write(f"${int(appointment.Total)}")

            show_str = ""

            if (
                appointment.DownPaymentDate
                and appointment.DownPaymentDate.month == st.session_state.current_month
                and appointment.DownPaymentDate.year == st.session_state.current_year
            ):
                show_str = f"Pagó seña de ${int(appointment.DownPayment)} el {appointment.DownPaymentDate.strftime('%d %b')}"

            if (
                appointment.RemainingPaymentDate
                and appointment.RemainingPaymentDate.month
                == st.session_state.current_month
                and appointment.RemainingPaymentDate.year
                == st.session_state.current_year
            ):
                show_str += " y el resto de $" if show_str else "Pagó el resto de $"
                show_str += (
                    f"{int(appointment.Remaining)} el "
                    + appointment.RemainingPaymentDate.strftime("%d %b ")
                )

            col5.text(show_str)

    else:
        st.info("No appointments found.")


if __name__ == "__main__":
    display_incomes_page()
