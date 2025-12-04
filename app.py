import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from pdf.cabecalho import desenhar_cabecalho
from pdf.corpo import desenhar_tabela
from pdf.pdf_utils import mostrar_pdf_na_tela


st.set_page_config(page_title="Folha de Ponto", layout="centered")


def gerar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # 🔥 Define o título exibido no visualizador de PDF
    c.setTitle("Folha de ponto")

    desenhar_cabecalho(c)
    # desenhar_tabela(c, ano=2025, mes=12)  # quando estiver pronto

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

if st.button("Gerar PDF"):
    pdf_bytes = gerar_pdf()
    st.session_state["pdf"] = pdf_bytes

if "pdf" in st.session_state:
    st.subheader("Pré-visualização do PDF")
    mostrar_pdf_na_tela(st.session_state["pdf"])

    st.download_button(
        "⬇ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
