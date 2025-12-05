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

    # Define título interno do PDF
    c.setTitle("Folha de ponto")

    # Cabeçalho oficial
    desenhar_cabecalho(c)

    # Corpo (quando estiver finalizado)
    # desenhar_tabela(c, ano=2025, mes=12)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

st.write("""
Clique em **Gerar PDF** para criar a Folha de Ponto com cabeçalho oficial.
Depois use **Baixar PDF** para salvar o arquivo.
""")


# Botão para gerar PDF
if st.button("Gerar PDF"):
    st.session_state["pdf"] = gerar_pdf()
    st.success("PDF gerado com sucesso!")


# Apenas botão de download (sem visualização e sem link extra)
if "pdf" in st.session_state:
    st.download_button(
        "⬇ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
