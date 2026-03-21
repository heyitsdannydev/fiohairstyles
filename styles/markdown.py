def markdown(h, text):
    return h.markdown(
        f"""
    <span style="
        color:#9ca3af;
        font-size:20px;
        font-weight:500;
    ">
    {text}
    </span>
    """,
        unsafe_allow_html=True,
    )
