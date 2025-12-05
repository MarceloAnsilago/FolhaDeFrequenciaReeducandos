import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from pdf.cabecalho import desenhar_cabecalho
from pdf.corpo import desenhar_tabela


st.set_page_config(page_title="Folha de Ponto", layout="centered")


def gerar_pdf():
    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle("Folha de ponto")

    desenhar_cabecalho(c)
    # desenhar_tabela(c, ano=2025, mes=12)  # depois

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

if st.button("Gerar PDF"):
    pdf_bytes = gerar_pdf()
    st.session_state["pdf"] = pdf_bytes
    st.success("✅ PDF gerado com sucesso! Use o botão abaixo para baixar.")

if "pdf" in st.session_state:
    st.download_button(
        "⬇ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
else:
    st.info("Clique em **Gerar PDF** para criar a folha de ponto.")
