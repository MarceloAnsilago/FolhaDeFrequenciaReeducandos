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


def _wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    lines = []
    for paragraph in (text or "").splitlines():
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if stringWidth(candidate, font_name, font_size) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)

    return lines or [""]


def _draw_cell_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    font_name: str = "Helvetica",
    font_size: int = 8,
    align: str = "center",
    bold: bool = False,
):
    chosen_font = "Helvetica-Bold" if bold else font_name
    lines = _wrap_text(text, chosen_font, font_size, w - 3 * mm)
    line_height = font_size * 1.2
    total_height = len(lines) * line_height
    start_y = y + (h + total_height) / 2 - font_size

    c.setFont(chosen_font, font_size)
    for idx, line in enumerate(lines[:4]):
        draw_y = start_y - idx * line_height
        if align == "left":
            c.drawString(x + 1.5 * mm, draw_y, line)
        elif align == "right":
            c.drawRightString(x + w - 1.5 * mm, draw_y, line)
        else:
            c.drawCentredString(x + w / 2, draw_y, line)


def _parse_items(raw_text: str) -> list[dict]:
    items = []
    for line in (raw_text or "").splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        items.append({"descricao": cleaned})
    return items


def _draw_document_header(
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


def build_pdf_guia_malote(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    header_bottom_y = _draw_document_header(c, page_width, page_height, logo_path)

    box_w = 70 * mm
    box_h = 7 * mm
    margin = 15 * mm
    box_x = page_width - margin - box_w
    box_y = header_bottom_y - 1.5 * mm

    c.setLineWidth(0.7)
    c.rect(box_x, box_y, box_w, box_h)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(box_x + box_w / 2, box_y + 2.2 * mm, "GUIA N°")

    table_x = margin
    table_w = 105 * mm
    table_h = box_h * 3
    table_y = box_y - table_h - 3 * mm
    col_w = table_w / 2
    header_h = box_h
    value_h = table_h - header_h

    c.rect(table_x, table_y, table_w, table_h)
    c.line(table_x + col_w, table_y, table_x + col_w, table_y + table_h)
    c.line(table_x, table_y + value_h, table_x + table_w, table_y + value_h)

    _draw_cell_text(
        c,
        "ORIGEM",
        table_x,
        table_y + value_h,
        col_w,
        header_h,
        font_size=8,
        align="left",
        bold=True,
    )
    _draw_cell_text(
        c,
        "DESTINO",
        table_x + col_w,
        table_y + value_h,
        col_w,
        header_h,
        font_size=8,
        align="left",
        bold=True,
    )
    _draw_cell_text(
        c,
        data.get("origem_resumo", ""),
        table_x,
        table_y,
        col_w,
        value_h,
        font_size=8,
        align="left",
    )
    _draw_cell_text(
        c,
        data.get("destino_resumo", ""),
        table_x + col_w,
        table_y,
        col_w,
        value_h,
        font_size=8,
        align="left",
    )

    title_y = table_y - 8 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(
        page_width / 2,
        title_y,
        "GUIA DE REMESSA DE CORRESPONDENCIA PARA MALOTE",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def build_pdf_guia_malote_v2(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    header_bottom_y = _draw_document_header(c, page_width, page_height, logo_path)
    margin = 15 * mm

    guia_w = 70 * mm
    guia_h = 7 * mm
    guia_x = page_width - margin - guia_w
    guia_y = header_bottom_y - 1.5 * mm

    c.setLineWidth(0.7)
    c.rect(guia_x, guia_y, guia_w, guia_h)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(
        guia_x + guia_w / 2,
        guia_y + 2.2 * mm,
        data.get("identificacao_guia", "GUIA N°"),
    )

    resumo_x = margin
    resumo_w = 105 * mm
    resumo_h = guia_h * 3
    resumo_y = guia_y - resumo_h - 3 * mm
    resumo_col_w = resumo_w / 2
    resumo_header_h = guia_h
    resumo_value_h = resumo_h - resumo_header_h

    c.rect(resumo_x, resumo_y, resumo_w, resumo_h)
    c.line(resumo_x + resumo_col_w, resumo_y, resumo_x + resumo_col_w, resumo_y + resumo_h)
    c.line(resumo_x, resumo_y + resumo_value_h, resumo_x + resumo_w, resumo_y + resumo_value_h)

    _draw_cell_text(
        c,
        "ORIGEM",
        resumo_x,
        resumo_y + resumo_value_h,
        resumo_col_w,
        resumo_header_h,
        font_size=8,
        align="left",
        bold=True,
    )
    _draw_cell_text(
        c,
        "DESTINO",
        resumo_x + resumo_col_w,
        resumo_y + resumo_value_h,
        resumo_col_w,
        resumo_header_h,
        font_size=8,
        align="left",
        bold=True,
    )
    _draw_cell_text(
        c,
        data.get("origem_resumo", ""),
        resumo_x,
        resumo_y,
        resumo_col_w,
        resumo_value_h,
        font_size=8,
        align="left",
    )
    _draw_cell_text(
        c,
        data.get("destino_resumo", ""),
        resumo_x + resumo_col_w,
        resumo_y,
        resumo_col_w,
        resumo_value_h,
        font_size=8,
        align="left",
    )

    title_y = resumo_y - 8 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_width / 2, title_y, "GUIA DE REMESSA DE CORRESPONDENCIA PARA MALOTE")

    tabela_x = margin
    tabela_w = page_width - (2 * margin)
    col_widths = [15 * mm, 37 * mm, 41 * mm, tabela_w - 93 * mm]
    tabela_header_h = 12 * mm
    tabela_row_h = 17 * mm
    itens = data.get("itens", [])
    row_count = max(len(itens), 1)
    tabela_h = tabela_header_h + (row_count * tabela_row_h)
    tabela_top_y = title_y - 4 * mm
    tabela_y = tabela_top_y - tabela_h

    c.rect(tabela_x, tabela_y, tabela_w, tabela_h)

    current_x = tabela_x
    for width in col_widths[:-1]:
        current_x += width
        c.line(current_x, tabela_y, current_x, tabela_y + tabela_h)

    c.line(
        tabela_x,
        tabela_y + tabela_h - tabela_header_h,
        tabela_x + tabela_w,
        tabela_y + tabela_h - tabela_header_h,
    )

    headers = ["ORDE\nM", "ORIGEM", "DESTINO", "DESCRIÇÃO"]
    draw_x = tabela_x
    for idx, header in enumerate(headers):
        _draw_cell_text(
            c,
            header,
            draw_x,
            tabela_y + tabela_h - tabela_header_h,
            col_widths[idx],
            tabela_header_h,
            font_size=8,
            bold=True,
        )
        draw_x += col_widths[idx]

    if not itens:
        itens = [{"origem": "", "destino": "", "descricao": ""}]

    for row_idx, item in enumerate(itens):
        row_bottom = tabela_y + tabela_h - tabela_header_h - ((row_idx + 1) * tabela_row_h)
        if row_idx < len(itens) - 1:
            c.line(tabela_x, row_bottom, tabela_x + tabela_w, row_bottom)

        values = [
            str(row_idx + 1),
            data.get("origem_resumo", ""),
            data.get("destino_resumo", ""),
            item.get("descricao", ""),
        ]

        draw_x = tabela_x
        for col_idx, value in enumerate(values):
            _draw_cell_text(
                c,
                value,
                draw_x,
                row_bottom,
                col_widths[col_idx],
                tabela_row_h,
                font_size=8,
            )
            draw_x += col_widths[col_idx]

    rodape_y = tabela_y - 18 * mm
    c.setFont("Helvetica", 10)
    c.drawString(tabela_x, rodape_y, f"DATA:  {data.get('data_envio', '')}.")
    c.drawString(tabela_x + 110 * mm, rodape_y, "RECEBIMENTO")

    assinatura_y = rodape_y - 25 * mm
    left_x1 = tabela_x
    left_x2 = tabela_x + 58 * mm
    right_x1 = tabela_x + 108 * mm
    right_x2 = tabela_x + 166 * mm
    c.line(left_x1, assinatura_y, left_x2, assinatura_y)
    c.line(right_x1, assinatura_y, right_x2, assinatura_y)

    c.setFont("Helvetica", 9)
    c.drawCentredString((left_x1 + left_x2) / 2, assinatura_y - 6 * mm, data.get("assinatura_nome", ""))
    c.setFont("Helvetica", 7)
    c.drawCentredString((left_x1 + left_x2) / 2, assinatura_y - 10 * mm, data.get("assinatura_cargo", ""))
    c.drawCentredString(
        (left_x1 + left_x2) / 2,
        assinatura_y - 14 * mm,
        f"MATRICULA: {data.get('assinatura_matricula', '')}",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def render_guia_malote():
    st.title("Guia de Malote")
    st.caption("Gera a guia em PDF no mesmo padrao dos outros modulos.")

    defaults = {
        "guia_malote_numero": "",
        "guia_malote_ano": "",
        "guia_malote_supervisao": "",
        "guia_malote_origem_resumo": "",
        "guia_malote_destino_resumo": "",
        "guia_malote_data_envio": datetime.today().strftime("%d/%m/%Y"),
        "guia_malote_itens": "",
        "guia_malote_assinatura_nome": "",
        "guia_malote_assinatura_cargo": "",
        "guia_malote_assinatura_matricula": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    with st.form("form_guia_malote"):
        st.markdown("### Dados da guia")
        guia_col1, guia_col2 = st.columns(2)
        with guia_col1:
            st.text_input("Numero da guia", key="guia_malote_numero")
            st.text_input("Ano", key="guia_malote_ano")
            st.text_input("Data de envio", key="guia_malote_data_envio", placeholder="17/04/2026")
        with guia_col2:
            st.text_input("Supervisao regional", key="guia_malote_supervisao")
            st.text_input("Origem resumo", key="guia_malote_origem_resumo")
            st.text_input("Destino resumo", key="guia_malote_destino_resumo")

        st.markdown("### Dados do responsavel")
        resp_col1, resp_col2 = st.columns(2)
        with resp_col1:
            st.text_input("Nome da assinatura", key="guia_malote_assinatura_nome")
            st.text_input("Cargo da assinatura", key="guia_malote_assinatura_cargo")
        with resp_col2:
            st.text_input("Matricula da assinatura", key="guia_malote_assinatura_matricula")

        st.text_area(
            "Descricoes da tabela",
            key="guia_malote_itens",
            height=140,
            placeholder="Processo administrativo\nNota fiscal avulsa de servicos",
            help="Use uma linha por item. Cada linha sera usada como descricao.",
        )

        submit = st.form_submit_button("Gerar PDF")

    if submit:
        numero = (st.session_state.get("guia_malote_numero", "") or "").strip()
        ano = (st.session_state.get("guia_malote_ano", "") or "").strip()
        itens = _parse_items(st.session_state.get("guia_malote_itens", ""))

        data = {
            "supervisao_regional": st.session_state.get("guia_malote_supervisao", "").strip(),
            "identificacao_guia": f"GUIA N° {numero}/{ano}".strip("/") if numero or ano else "",
            "origem_resumo": st.session_state.get("guia_malote_origem_resumo", "").strip(),
            "destino_resumo": st.session_state.get("guia_malote_destino_resumo", "").strip(),
            "data_envio": st.session_state.get("guia_malote_data_envio", "").strip(),
            "itens": itens,
            "assinatura_nome": st.session_state.get("guia_malote_assinatura_nome", "").strip(),
            "assinatura_cargo": st.session_state.get("guia_malote_assinatura_cargo", "").strip(),
            "assinatura_matricula": st.session_state.get("guia_malote_assinatura_matricula", "").strip(),
        }

        logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
        pdf_bytes = build_pdf_guia_malote_v2(data, logo_path)
        st.session_state["guia_malote_pdf"] = pdf_bytes

        output_dir = Path(__file__).resolve().parents[1] / "pdf"
        output_dir.mkdir(parents=True, exist_ok=True)
        if numero and ano:
            file_name = f"GUIA DE MALOTE {numero} {ano}.pdf"
        elif numero:
            file_name = f"GUIA DE MALOTE {numero}.pdf"
        elif ano:
            file_name = f"GUIA DE MALOTE {ano}.pdf"
        else:
            file_name = "GUIA DE MALOTE.pdf"
        output_path = output_dir / file_name
        output_path.write_bytes(pdf_bytes)
        st.session_state["guia_malote_pdf_path"] = output_path
        st.success("PDF gerado e salvo.")

    if "guia_malote_pdf" in st.session_state:
        try:
            st.pdf(st.session_state["guia_malote_pdf"])
        except StreamlitAPIException:
            st.info("Pre-visualizacao indisponivel. Instale streamlit[pdf].")

        numero = (st.session_state.get("guia_malote_numero", "") or "").strip()
        ano = (st.session_state.get("guia_malote_ano", "") or "").strip()
        if numero and ano:
            file_name = f"GUIA DE MALOTE {numero} {ano}.pdf"
        elif numero:
            file_name = f"GUIA DE MALOTE {numero}.pdf"
        elif ano:
            file_name = f"GUIA DE MALOTE {ano}.pdf"
        else:
            file_name = "GUIA DE MALOTE.pdf"

        st.download_button(
            "Baixar PDF",
            data=st.session_state["guia_malote_pdf"],
            file_name=file_name,
            mime="application/pdf",
        )
        if "guia_malote_pdf_path" in st.session_state:
            st.caption(f"Salvo em: {st.session_state['guia_malote_pdf_path']}")
