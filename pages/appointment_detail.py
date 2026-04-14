import streamlit as st


def display_appointment_detail_page():
    st.set_page_config(page_title="Appointment Detail", layout="wide")
    st.title("📝 Appointment Detail")

    appointment = st.session_state.get("selected_appointment")

    if not appointment:
        st.warning("No appointment selected.")
        return

    st.markdown("## Clienta")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Clienta**  \n{appointment.Client.ClientName}")
    with col2:
        st.markdown(f"**Domicilio**  \n{appointment.Address or ''}")

    st.markdown("## Horario")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Fecha**  \n{appointment.ServiceDateTime.strftime('%Y-%m-%d')}")
    with col2:
        st.markdown(f"**Hora**  \n{appointment.ServiceDateTime.strftime('%H:%M')}")

    st.markdown("## Servicio")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"**Servicio**  \n{appointment.Service}")
    with col2:
        st.markdown(f"**Precio servicio**  \n${appointment.ServicePrice}")
    with col3:
        st.markdown(f"**Transporte**  \n${appointment.Transportation}")
    with col4:
        st.markdown(f"**Total**  \n${appointment.Total}")

    st.markdown("## Seña")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"**% de seña**  \n"
            f"{f'{appointment.DownPaymentPercentage}%' if appointment.DownPaymentPercentage is not None else ''}"
        )
    with col2:
        st.markdown(f"**Monto de seña**  \n" f"{f'${appointment.DownPayment}'}")

    st.markdown("## Método de pago")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Método de pago**  \n{appointment.PaymentMethod or ''}")


if __name__ == "__main__":
    display_appointment_detail_page()
