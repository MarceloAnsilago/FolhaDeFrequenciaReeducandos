import base64
from io import BytesIO
import streamlit as st

def mostrar_pdf_na_tela(pdf_bytes: bytes, altura: int = 900):
    """Exibe um PDF em um iframe embutido no Streamlit."""
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="{altura}px"
            type="application/pdf">
        </iframe>
    """
    st.markdown(pdf_html, unsafe_allow_html=True)
