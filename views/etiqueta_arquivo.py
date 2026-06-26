import base64
from io import BytesIO
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from streamlit.errors import StreamlitAPIException


LABEL_WIDTH_MM = 115
MONTH_HEADER_HEIGHT_MM = 14
ROW_HEIGHTS_MM = [MONTH_HEADER_HEIGHT_MM, MONTH_HEADER_HEIGHT_MM, MONTH_HEADER_HEIGHT_MM]
MONTH_SEPARATOR_HEIGHT_MM = MONTH_HEADER_HEIGHT_MM / 2
MONTH_BODY_MIN_HEIGHT_MM = 0
MONTH_BODY_TOP_PADDING_MM = 5
MONTH_BODY_BOTTOM_PADDING_MM = 2
PAGE_MARGIN_MM = 15
LABEL_GAP_MM = 8
OUTPUT_FILENAME = "modelo etiqueta para caixa arquivo.pdf"
TEXT_FONT = "Helvetica-Bold"
TEXT_SIZE = 12
MIN_TEXT_SIZE = 6
MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
CURRENT_YEAR = date.today().year
YEARS = list(range(2012, CURRENT_YEAR + 1))


def _normalize_text(text: str) -> str:
    normalized = " ".join((text or "").strip().split())
    return normalized


def _fit_single_line_text(text: str, max_width: float, font_name: str, base_size: int, min_size: int):
    normalized = _normalize_text(text)
    font_size = base_size
    while font_size >= min_size:
        if stringWidth(normalized, font_name, font_size) <= max_width:
            return font_size, normalized
        font_size -= 1
    return min_size, normalized


def _draw_double_line(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float):
    c.line(x1, y1, x2, y2)


def _draw_inner_horizontal_line(c: canvas.Canvas, x: float, y: float, width: float):
    _draw_double_line(c, x, y, x + width, y)


def _draw_vertical_borders(c: canvas.Canvas, x: float, y_top: float, y_bottom: float, width: float):
    _draw_double_line(c, x, y_top, x, y_bottom)
    _draw_double_line(c, x + width, y_top, x + width, y_bottom)


def _draw_row(c: canvas.Canvas, label: str, value: str, x: float, y_top: float, width: float, height: float):
    padding_x = 5 * mm

    full_text = f"{label} {(value or '').upper()}".strip()
    text_width = width - (2 * padding_x)
    font_size, line = _fit_single_line_text(full_text, text_width, TEXT_FONT, TEXT_SIZE, MIN_TEXT_SIZE)
    text_y = y_top - (height / 2) - (font_size / 3)

    c.setFont(TEXT_FONT, font_size)
    c.drawString(x + padding_x, text_y, line)


def _draw_centered_row(c: canvas.Canvas, text: str, x: float, y_top: float, width: float, height: float):
    padding_x = 5 * mm
    text = (text or "").upper()
    text_width = width - (2 * padding_x)
    font_size, line = _fit_single_line_text(text, text_width, TEXT_FONT, TEXT_SIZE, MIN_TEXT_SIZE)
    text_y = y_top - (height / 2) - (font_size / 3)

    c.setFont(TEXT_FONT, font_size)
    c.drawCentredString(x + width / 2, text_y, line)


def _wrap_text_line(line: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    words = line.split()
    if not words:
        return []

    wrapped_lines = []
    current_line = words[0]
    for word in words[1:]:
        candidate = f"{current_line} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current_line = candidate
        else:
            wrapped_lines.append(current_line)
            current_line = word
    wrapped_lines.append(current_line)
    return wrapped_lines


def _split_text_lines(text: str, max_width: float | None = None) -> list[str]:
    lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if line:
            if max_width:
                lines.extend(_wrap_text_line(line, max_width, TEXT_FONT, TEXT_SIZE))
            else:
                lines.append(line)
    return lines


def _month_body_height(line_count: int):
    return (
        (MONTH_BODY_TOP_PADDING_MM * mm)
        + (max(1, line_count) * TEXT_SIZE * 1.45)
        + (MONTH_BODY_BOTTOM_PADDING_MM * mm)
    )


def _max_month_lines_for_height(body_height: float):
    usable_height = body_height - (MONTH_BODY_TOP_PADDING_MM * mm) - (MONTH_BODY_BOTTOM_PADDING_MM * mm)
    return max(1, int(usable_height // (TEXT_SIZE * 1.45)))


def _draw_month_section(
    c: canvas.Canvas,
    *,
    month: str,
    year: int,
    lines: list[str],
    x: float,
    y_top: float,
    width: float,
    header_height: float,
    body_height: float,
    separator_height: float,
):
    padding_x = 5 * mm
    inner_x = x
    inner_width = width
    header_y = y_top - (header_height / 2) - (TEXT_SIZE / 3)
    body_top = y_top - header_height
    body_bottom = body_top - body_height
    separator_bottom = body_bottom - separator_height

    c.setFont(TEXT_FONT, TEXT_SIZE)
    c.drawString(x + padding_x, header_y, f"MÊS/ANO: {month.upper()}/{year}")
    _draw_inner_horizontal_line(c, x, body_top, width)

    line_height = TEXT_SIZE * 1.45
    cursor_y = body_top - (MONTH_BODY_TOP_PADDING_MM * mm)
    for line in lines:
        if cursor_y < body_bottom + (MONTH_BODY_BOTTOM_PADDING_MM * mm):
            break
        c.drawString(x + padding_x, cursor_y, line)
        cursor_y -= line_height

    c.rect(inner_x, separator_bottom, inner_width, separator_height, stroke=1, fill=0)
    c.setFillColorRGB(127 / 255, 127 / 255, 127 / 255)
    c.rect(
        inner_x + 0.4,
        separator_bottom + 0.4,
        inner_width - 0.8,
        separator_height - 0.8,
        stroke=0,
        fill=1,
    )
    c.setFillColorRGB(0, 0, 0)
    return separator_bottom


def _draw_fixed_header(
    c: canvas.Canvas,
    *,
    supervisao_regional: str,
    unidade: str,
    caixa: str,
    x: float,
    y_top: float,
    width: float,
    row_heights: list[float],
):
    c.setLineWidth(0.8)
    c.setFillColorRGB(0, 0, 0)
    _draw_inner_horizontal_line(c, x, y_top, width)

    rows = [
        ("SUPERVISÃO REGIONAL:", supervisao_regional),
        ("UNIDADE:", unidade),
    ]

    cursor_top = y_top
    for index, (label, value) in enumerate(rows):
        row_height = row_heights[index]
        _draw_row(c, label, value, x, cursor_top, width, row_height)
        cursor_top -= row_height
        _draw_inner_horizontal_line(c, x, cursor_top, width)

    _draw_centered_row(c, f"CAIXA Nº: {caixa}", x, cursor_top, width, row_heights[2])
    cursor_top -= row_heights[2]
    _draw_inner_horizontal_line(c, x, cursor_top, width)
    return cursor_top


def _render_instruction_diagram():
    st.markdown(
        """
        <style>
        .etq-wrap {
            display: flex;
            justify-content: center;
            margin: 0.5rem 0 1.25rem 0;
        }
        .etq-card {
            width: 430px;
            border: 4px double #111;
            background: #fff;
            color: #111;
            font-family: Helvetica, Arial, sans-serif;
        }
        .etq-row {
            min-height: 48px;
            border-bottom: 4px double #111;
            padding: 6px 18px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .etq-row:last-child {
            border-bottom: none;
        }
        .etq-label {
            font-size: 14px;
            font-weight: 700;
            flex: 0 0 auto;
        }
        .etq-value {
            font-size: 14px;
            font-weight: 700;
            line-height: 1.15;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .etq-row-center {
            justify-content: center;
        }
        </style>
        <div class="etq-wrap">
            <div class="etq-card">
                <div class="etq-row">
                    <div class="etq-label">SUPERVISÃO REGIONAL:</div>
                    <div class="etq-value">&nbsp;</div>
                </div>
                <div class="etq-row">
                    <div class="etq-label">UNIDADE:</div>
                    <div class="etq-value">&nbsp;</div>
                </div>
                <div class="etq-row etq-row-center">
                    <div class="etq-label">CAIXA Nº: *</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_pdf_etiqueta_arquivo(
    *,
    supervisao_regional: str,
    unidade: str,
    caixa: str,
    month_sections: list[dict] | None = None,
    label_cards: list[dict] | None = None,
) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    label_width = LABEL_WIDTH_MM * mm
    row_heights = [value * mm for value in ROW_HEIGHTS_MM]
    month_sections = month_sections or []
    month_header_height = MONTH_HEADER_HEIGHT_MM * mm
    month_separator_height = MONTH_SEPARATOR_HEIGHT_MM * mm
    month_body_min_height = MONTH_BODY_MIN_HEIGHT_MM * mm

    x = (page_width - label_width) / 2
    page_margin = PAGE_MARGIN_MM * mm
    page_top = page_height - page_margin
    page_bottom = page_margin
    label_gap = LABEL_GAP_MM * mm
    cursor_top = page_top

    cards = label_cards or [
        {
            "supervisao_regional": supervisao_regional,
            "unidade": unidade,
            "caixa": caixa,
            "month_sections": month_sections or [],
        }
    ]

    def build_month_layouts(sections: list[dict]):
        layouts = []
        text_width = label_width - (2 * 5 * mm)
        for section in sections:
            lines = _split_text_lines(section.get("text", ""), text_width) or [""]
            body_height = max(
                month_body_min_height,
                _month_body_height(len(lines)),
            )
            layouts.append((section, lines, body_height))
        return layouts

    def finish_card(y_start: float, y_bottom: float):
        _draw_vertical_borders(c, x, y_start, y_bottom, label_width)
        _draw_inner_horizontal_line(c, x, y_bottom, label_width)

    def draw_header(card: dict, y_top: float):
        return _draw_fixed_header(
            c,
            supervisao_regional=card.get("supervisao_regional", ""),
            unidade=card.get("unidade", ""),
            caixa=card.get("caixa", ""),
            x=x,
            y_top=y_top,
            width=label_width,
            row_heights=row_heights,
        )

    def start_new_page(card: dict):
        nonlocal cursor_top
        c.showPage()
        cursor_top = page_top
        card_start_top = cursor_top
        cursor_top = draw_header(card, card_start_top)
        return card_start_top

    fresh_page_available = page_top - sum(row_heights) - page_bottom

    for card_index, card in enumerate(cards):
        if card_index > 0:
            cursor_top -= label_gap

        month_layouts = build_month_layouts(card.get("month_sections", []))
        required_height = sum(row_heights)
        if month_layouts:
            _section, _lines, first_body_height = month_layouts[0]
            first_section_height = month_header_height + first_body_height + month_separator_height
            if first_section_height <= fresh_page_available:
                required_height += first_section_height
            else:
                required_height += month_header_height + _month_body_height(1) + month_separator_height

        if cursor_top - required_height < page_bottom:
            c.showPage()
            cursor_top = page_top

        card_start_top = cursor_top
        cursor_top = draw_header(card, card_start_top)

        for section, lines, body_height in month_layouts:
            section_height = month_header_height + body_height + month_separator_height
            if section_height <= fresh_page_available and cursor_top - section_height < page_bottom:
                finish_card(card_start_top, cursor_top)
                card_start_top = start_new_page(card)

            line_index = 0
            while line_index < len(lines):
                available_height = cursor_top - page_bottom
                remaining_lines = len(lines) - line_index
                remaining_body_height = max(month_body_min_height, _month_body_height(remaining_lines))
                remaining_section_height = month_header_height + remaining_body_height + month_separator_height

                if remaining_section_height <= available_height:
                    lines_to_draw = lines[line_index:]
                    fragment_body_height = remaining_body_height
                else:
                    fragment_available_body_height = available_height - month_header_height - month_separator_height
                    if fragment_available_body_height <= _month_body_height(1):
                        finish_card(card_start_top, cursor_top)
                        card_start_top = start_new_page(card)
                        continue
                    max_lines = min(
                        remaining_lines,
                        _max_month_lines_for_height(fragment_available_body_height),
                    )
                    lines_to_draw = lines[line_index:line_index + max_lines]
                    fragment_body_height = _month_body_height(len(lines_to_draw))

                cursor_top = _draw_month_section(
                    c,
                    month=section.get("month", ""),
                    year=section.get("year", CURRENT_YEAR),
                    lines=lines_to_draw,
                    x=x,
                    y_top=cursor_top,
                    width=label_width,
                    header_height=month_header_height,
                    body_height=fragment_body_height,
                    separator_height=month_separator_height,
                )
                line_index += len(lines_to_draw)
                if line_index < len(lines):
                    finish_card(card_start_top, cursor_top)
                    card_start_top = start_new_page(card)

        finish_card(card_start_top, cursor_top)

    if not cards:
        cursor_top = draw_header(
            {
                "supervisao_regional": supervisao_regional,
                "unidade": unidade,
                "caixa": caixa,
            },
            cursor_top,
        )
        finish_card(page_top, cursor_top)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _current_label_card(month_sections: list[dict]) -> dict:
    return {
        "supervisao_regional": st.session_state.get("etiqueta_supervisao_regional", ""),
        "unidade": st.session_state.get("etiqueta_unidade", ""),
        "caixa": st.session_state.get("etiqueta_caixa", ""),
        "month_sections": [
            {
                "month": section.get("month", ""),
                "year": section.get("year", CURRENT_YEAR),
                "text": section.get("text", ""),
            }
            for section in month_sections
        ],
    }


def _label_card_title(card: dict, index: int) -> str:
    months = card.get("month_sections", [])
    month_text = ", ".join(f"{item.get('month', '')}/{item.get('year', '')}" for item in months[:2])
    if len(months) > 2:
        month_text = f"{month_text}..."
    return f"Etiqueta {index} - Caixa {card.get('caixa', '') or '*'}" + (f" - {month_text}" if month_text else "")


def _store_etiqueta_pdf(pdf_bytes: bytes):
    st.session_state["etiqueta_arquivo_pdf"] = pdf_bytes

    output_dir = Path(__file__).resolve().parents[1] / "pdf"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_FILENAME
    output_path.write_bytes(pdf_bytes)
    st.session_state["etiqueta_arquivo_pdf_path"] = output_path


def _build_current_pdf(month_sections: list[dict]) -> bytes:
    cards = st.session_state.get("etiqueta_cards", [])
    return build_pdf_etiqueta_arquivo(
        supervisao_regional=st.session_state.get("etiqueta_supervisao_regional", ""),
        unidade=st.session_state.get("etiqueta_unidade", ""),
        caixa=st.session_state.get("etiqueta_caixa", ""),
        month_sections=month_sections,
        label_cards=cards if cards else None,
    )


def _render_pdf_viewer(pdf_bytes: bytes):
    try:
        st.pdf(pdf_bytes)
    except StreamlitAPIException:
        st.info("Pré-visualização indisponível. Instale streamlit[pdf].")

def _render_open_pdf_button(pdf_bytes: bytes):
    pdf_base64 = base64.b64encode(pdf_bytes).decode("ascii")
    components.html(
        f"""
        <button id="open-pdf" type="button">Abrir PDF</button>
        <script>
        const pdfBase64 = "{pdf_base64}";
        function pdfUrl() {{
            const binary = atob(pdfBase64);
            const bytes = new Uint8Array(binary.length);
            for (let index = 0; index < binary.length; index++) {{
                bytes[index] = binary.charCodeAt(index);
            }}
            const blob = new Blob([bytes], {{ type: "application/pdf" }});
            return URL.createObjectURL(blob);
        }}
        document.getElementById("open-pdf").addEventListener("click", () => {{
            window.open(pdfUrl(), "_blank");
        }});
        </script>
        <style>
        button {{
            appearance: none;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: #ffffff;
            color: #111827;
            font: 14px/1.2 sans-serif;
            padding: 9px 14px;
            margin: 0 8px 0 0;
            cursor: pointer;
        }}
        button:hover {{
            border-color: #9ca3af;
            background: #f9fafb;
        }}
        </style>
        """,
        height=48,
        scrolling=False,
    )


def render_etiqueta_arquivo():
    st.session_state.setdefault("etiqueta_supervisao_regional", "")
    st.session_state.setdefault("etiqueta_unidade", "")
    st.session_state.setdefault("etiqueta_caixa", "*")
    st.session_state.setdefault("etiqueta_cards", [])
    for month in MONTHS:
        st.session_state.setdefault(f"etiqueta_mes_{month.lower()}", False)
        st.session_state.setdefault(f"etiqueta_ano_{month.lower()}", CURRENT_YEAR)

    col_left, col_mid, col_right = st.columns([0.1, 8, 0.1])
    with col_mid:
        st.title("Etiqueta de Arquivo")

        st.text_input("Supervisão regional", key="etiqueta_supervisao_regional")
        st.text_input("Unidade", key="etiqueta_unidade")
        st.text_input("Caixa", key="etiqueta_caixa")
        st.markdown("Meses")
        month_sections = []
        for month in MONTHS:
            month_key = month.lower()
            month_col, year_col = st.columns([2, 1])
            with month_col:
                checked = st.checkbox(month, key=f"etiqueta_mes_{month_key}")
            with year_col:
                st.selectbox(
                    f"Ano - {month}",
                    YEARS,
                    index=YEARS.index(st.session_state.get(f"etiqueta_ano_{month_key}", CURRENT_YEAR)),
                    key=f"etiqueta_ano_{month_key}",
                    disabled=not checked,
                    label_visibility="collapsed",
                )
            if checked:
                year = st.session_state.get(f"etiqueta_ano_{month_key}", CURRENT_YEAR)
                text_key = f"etiqueta_texto_{month_key}"
                default_text = f"{month} / {year}"
                st.session_state.setdefault(text_key, "")
                with st.expander(default_text, expanded=True):
                    st.text_area(
                        "Texto",
                        key=text_key,
                        height=100,
                        label_visibility="collapsed",
                    )
                month_sections.append(
                    {
                        "month": month,
                        "year": year,
                        "text": st.session_state.get(text_key, ""),
                    }
                )

        include = False
        show_include = "etiqueta_arquivo_pdf" in st.session_state or bool(st.session_state["etiqueta_cards"])
        if show_include:
            button_col_gerar, button_col_incluir = st.columns([1, 1])
            with button_col_gerar:
                submit = st.button("Gerar PDF")
            with button_col_incluir:
                include = st.button("Incluir")
        else:
            submit = st.button("Gerar PDF")

        if include:
            st.session_state["etiqueta_cards"].append(_current_label_card(month_sections))
            _store_etiqueta_pdf(_build_current_pdf(month_sections))
            st.success("Etiqueta incluÃ­da.")

        if st.session_state["etiqueta_cards"]:
            st.markdown("Etiquetas incluÃ­das")
            remove_index = None
            for index, card in enumerate(st.session_state["etiqueta_cards"], start=1):
                card_col, remove_col = st.columns([4, 1])
                with card_col:
                    st.info(_label_card_title(card, index))
                with remove_col:
                    if st.button("Remover", key=f"etiqueta_remover_{index}"):
                        remove_index = index - 1
            if remove_index is not None:
                del st.session_state["etiqueta_cards"][remove_index]
                if st.session_state["etiqueta_cards"]:
                    _store_etiqueta_pdf(_build_current_pdf(month_sections))
                else:
                    st.session_state.pop("etiqueta_arquivo_pdf", None)
                    st.session_state.pop("etiqueta_arquivo_pdf_path", None)
                st.rerun()

        if submit:
            if not st.session_state["etiqueta_cards"]:
                st.session_state["etiqueta_cards"].append(_current_label_card(month_sections))
            _store_etiqueta_pdf(_build_current_pdf(month_sections))
            st.success("PDF gerado e salvo.")

        if "etiqueta_arquivo_pdf" in st.session_state:
            try:
                _render_pdf_viewer(st.session_state["etiqueta_arquivo_pdf"])
            except StreamlitAPIException:
                st.info("Pré-visualização indisponível. Instale streamlit[pdf].")

            open_col, download_col = st.columns([1, 1])
            with open_col:
                _render_open_pdf_button(st.session_state["etiqueta_arquivo_pdf"])
            with download_col:
                st.download_button(
                    "Baixar PDF",
                    data=st.session_state["etiqueta_arquivo_pdf"],
                    file_name=OUTPUT_FILENAME,
                    mime="application/pdf",
                )
            if "etiqueta_arquivo_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['etiqueta_arquivo_pdf_path']}")
