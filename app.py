import streamlit as st
from io import BytesIO
import base64

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from pdf.cabecalho import desenhar_cabecalho
from pdf.corpo import desenhar_tabela  # vamos usar depois

st.set_page_config(page_title="Folha de Ponto", layout="centered")


def gerar_pdf() -> bytes:
    """
    Gera o PDF em memória e retorna os bytes.
    """
    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)

    # Metadados do PDF
    c.setTitle("Folha de ponto")

    # Cabeçalho (logo + textos + linha)
    desenhar_cabecalho(c)

    # No futuro:
    # desenhar_tabela(c, ano=2025, mes=12)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

st.write(
    """
Clique em **Gerar PDF** para criar a folha de ponto com cabeçalho oficial.
Depois você pode **abrir em uma nova aba** ou **baixar o arquivo**.
"""
)

if st.button("Gerar PDF"):
    pdf_bytes = gerar_pdf()
    st.session_state["pdf"] = pdf_bytes
    st.success("✅ PDF gerado com sucesso!")

# Se já temos um PDF em memória, mostramos as ações
if "pdf" in st.session_state:
    pdf_bytes = st.session_state["pdf"]

    # -----------------------------
    # Link para abrir em nova aba
    # -----------------------------
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_url = f"data:application/pdf;base64,{b64_pdf}"

    st.markdown(
        f"""
        <p>
            👉 <a href="{pdf_url}" target="_blank">
                <strong>Abrir PDF em nova aba</strong>
            </a>
        </p>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Botão de download
    # -----------------------------
    st.download_button(
        label="⬇ Baixar PDF",
        data=pdf_bytes,
        file_name="folha.pdf",
        mime="application/pdf",
    )
else:
    st.info("Ainda não há PDF gerado. Clique em **Gerar PDF**.")
