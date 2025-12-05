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
    try:
        c = canvas.Canvas(buffer, pagesize=A4)

        # Metadados do PDF (mostra "Folha de ponto" em vez de "untitled")
        c.setTitle("Folha de ponto")

        # Cabeçalho (se o logo não for encontrado, vai levantar erro aqui)
        desenhar_cabecalho(c)

        # No futuro:
        # desenhar_tabela(c, ano=2025, mes=12)

        c.showPage()
        c.save()

        buffer.seek(0)
        pdf_bytes = buffer.getvalue()

        # Se por algum motivo vier vazio, avisamos
        if not pdf_bytes:
            st.error("❌ PDF gerado vazio (0 bytes).")
            return None

        return pdf_bytes

    except Exception as e:
        # Mostra o erro na interface (inclusive no Streamlit Cloud)
        st.error(f"❌ Erro ao gerar PDF: {e}")
        return None


st.title("Gerador de Folha de Ponto")

if st.button("Gerar PDF"):
    pdf_bytes = gerar_pdf()
    if pdf_bytes:
        st.session_state["pdf"] = pdf_bytes

if "pdf" in st.session_state:
    st.subheader("Pré-visualização do PDF")

    try:
        mostrar_pdf_na_tela(st.session_state["pdf"])
        st.caption(f"Tamanho do PDF: {len(st.session_state['pdf'])} bytes")
    except Exception as e:
        st.error(f"❌ Erro ao exibir o PDF: {e}")

    st.download_button(
        "⬇ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
else:
    st.info("Clique no botão **Gerar PDF** para criar a folha de ponto.")
