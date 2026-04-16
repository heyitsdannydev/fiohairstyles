import streamlit as st
from pages.dialogs.create_appointment_dialog import create_appointment_dialog


def display_appointment_detail_page():
    st.set_page_config(layout="wide")

    appointment = st.session_state.get("selected_appointment")

    if not appointment:
        st.warning("No appointment selected.")
        return

    # --- HEADER ---
    header_col1, header_col2 = st.columns([6, 1])

    with header_col2:
        if st.button("✏️", use_container_width=True):
            st.session_state.editing_appointment = appointment
            st.session_state.show_appointment_dialog = True
            st.rerun()

    with st.container():
        st.subheader("👤 Clienta")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Nombre**")
            st.write(appointment.Client.ClientName)

        with col2:
            st.markdown("**Domicilio**")
            st.write(appointment.Address or "-")

    st.divider()

    with st.container():
        st.subheader("🕒 Horario")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Fecha**")
            st.write(appointment.ServiceDateTime.strftime("%d %B %Y"))

        with col2:
            st.markdown("**Hora**")
            st.write(appointment.ServiceDateTime.strftime("%H:%M"))

    st.divider()

    with st.container():
        st.subheader("💄 Servicio")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Servicio**")
            st.write(appointment.Service)

        with col2:
            st.markdown("**Precio**")
            st.write(f"${appointment.ServicePrice}")

        with col3:
            st.markdown("**Transporte**")
            st.write(f"${appointment.Transportation}")

        with col4:
            st.markdown("**Total**")
            st.write(f"${appointment.Total}")

    st.divider()

    with st.container():
        st.subheader("💰 Seña")

        col1, col2 = st.columns(2)

        with col1:
            percentage = (
                f"{appointment.DownPaymentPercentage}%"
                if appointment.DownPaymentPercentage is not None
                else "-"
            )
            st.markdown("**% de seña**")
            st.write(percentage)

        with col2:
            st.markdown("**Monto**")
            st.write(f"${appointment.DownPayment}")

    st.divider()

    with st.container():
        st.subheader("💳 Método de pago")

        st.write(appointment.PaymentMethod or "-")

    if st.session_state.get("show_appointment_dialog", False):
        create_appointment_dialog()


if __name__ == "__main__":
    display_appointment_detail_page()
