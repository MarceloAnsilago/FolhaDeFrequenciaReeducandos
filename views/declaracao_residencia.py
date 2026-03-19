from datetime import datetime
from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from streamlit.errors import StreamlitAPIException


def _wrap_text(text: str, font_name: str, font_size: int, max_width: float):
    linhas = []
    for paragrafo in text.splitlines():
        palavras = paragrafo.split()
        if not palavras:
            linhas.append("")
            continue
        linha = palavras[0]
        for palavra in palavras[1:]:
            tentativa = f"{linha} {palavra}"
            if stringWidth(tentativa, font_name, font_size) <= max_width:
                linha = tentativa
            else:
                linhas.append(linha)
                linha = palavra
        linhas.append(linha)
    return linhas


def _draw_restituicao_header(
    c: canvas.Canvas, page_width: float, page_height: float, logo_path: Path
) -> float:
    margin = 15 * mm
    rect_h = 30 * mm
    rect_w = page_width - 2 * margin
    rect_x = margin
    rect_y = page_height - margin - rect_h

    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        img_w, img_h = logo.getSize()
        max_w = rect_w * 0.8
        max_h = 32 * mm
        scale = min(max_w / img_w, max_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        img_x = rect_x + (rect_w - draw_w) / 2
        img_y = rect_y + (rect_h - draw_h) / 2 - 2 * mm
        c.drawImage(logo, img_x, img_y, width=draw_w, height=draw_h, mask="auto")

    return rect_y


def build_pdf_declaracao_residencia(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    title_y = _draw_restituicao_header(c, page_width, page_height, logo_path)

    margin = 20 * mm
    y = title_y - 12 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(page_width / 2, y, "DECLARAÇÃO DE RESIDÊNCIA")
    y -= 14 * mm

    nome = data.get("nome_declarante", "").strip() or "____________________________"
    logradouro = data.get("logradouro", "").strip() or "____________________________"
    municipio = data.get("municipio", "").strip() or "____________________________"
    complemento = data.get("complemento", "").strip()
    observacoes = data.get("observacoes", "").strip()

    endereco = f"{logradouro}, município de {municipio}"
    if complemento:
        endereco = f"{endereco}, complemento: {complemento}"

    texto = (
        f"Eu, {nome}, declaro para os devidos fins que resido no endereço {endereco}. "
        "Firmo a presente declaração para os efeitos legais cabíveis."
    )
    if observacoes:
        texto = f"{texto} Observações: {observacoes}."

    c.setFont("Helvetica", 11)
    for linha in _wrap_text(texto, "Helvetica", 11, page_width - 2 * margin):
        c.drawString(margin, y, linha)
        y -= 6 * mm

    y -= 6 * mm
    c.drawRightString(page_width - margin, y, data.get("data", ""))

    sig_y = 35 * mm
    sig_w = 75 * mm
    sig_x = (page_width - sig_w) / 2
    c.line(sig_x, sig_y, sig_x + sig_w, sig_y)
    c.setFont("Helvetica", 10)
    c.drawCentredString(sig_x + sig_w / 2, sig_y - 5 * mm, nome)
    c.drawCentredString(sig_x + sig_w / 2, sig_y - 10 * mm, "Assinatura do declarante")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def render_declaracao_residencia():
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("## Declaração de residência")
        with st.form("form_declaracao_residencia"):
            st.text_input("Nome do declarante", key="dr_nome_declarante")
            st.text_input("Logradouro", key="dr_logradouro")
            st.text_input("Município", key="dr_municipio")
            st.text_input("Complemento", key="dr_complemento")
            st.text_area("Observações (opcional)", key="dr_observacoes", height=80)
            submitted = st.form_submit_button("Gerar")

        if submitted:
            logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
            data = {
                "nome_declarante": st.session_state.get("dr_nome_declarante", ""),
                "logradouro": st.session_state.get("dr_logradouro", ""),
                "municipio": st.session_state.get("dr_municipio", ""),
                "complemento": st.session_state.get("dr_complemento", ""),
                "observacoes": st.session_state.get("dr_observacoes", ""),
                "data": datetime.today().strftime("%d/%m/%Y"),
            }
            pdf_bytes = build_pdf_declaracao_residencia(data, logo_path)
            st.session_state["declaracao_residencia_pdf"] = pdf_bytes

            output_dir = Path(__file__).resolve().parents[1] / "pdf"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "declaracao_residencia.pdf"
            output_path.write_bytes(pdf_bytes)
            st.session_state["declaracao_residencia_pdf_path"] = output_path
            st.success("PDF gerado e salvo.")

        if "declaracao_residencia_pdf" in st.session_state:
            st.markdown("### Página de impressão")
            pdf_bytes = st.session_state["declaracao_residencia_pdf"]
            try:
                st.pdf(pdf_bytes)
            except StreamlitAPIException:
                st.info(
                    "Pré-visualização de PDF indisponível neste ambiente. "
                    "Para habilitar, instale: pip install streamlit[pdf]"
                )
            st.download_button(
                "Baixar PDF",
                data=pdf_bytes,
                file_name="declaracao_residencia.pdf",
                mime="application/pdf",
            )
            if "declaracao_residencia_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['declaracao_residencia_pdf_path']}")
