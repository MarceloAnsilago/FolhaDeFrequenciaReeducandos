from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from streamlit.errors import StreamlitAPIException


LABEL_WIDTH_MM = 115
LABEL_HEIGHT_MM = 145
ROW_HEIGHTS_MM = [15, 35, 52, 20, 23]


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
            border: 1.5px solid #111;
            background: #fff;
            color: #111;
            font-family: Arial, sans-serif;
        }
        .etq-row {
            border-bottom: 1.5px solid #111;
            padding: 8px 12px;
            box-sizing: border-box;
        }
        .etq-row:last-child {
            border-bottom: none;
        }
        .etq-top {
            text-align: center;
            min-height: 72px;
        }
        .etq-top strong {
            font-size: 24px;
        }
        .etq-top span {
            font-size: 13px;
        }
        .etq-num {
            min-height: 140px;
            display: flex;
            align-items: center;
            gap: 18px;
        }
        .etq-num-left {
            font-size: 64px;
            font-weight: 700;
            line-height: 1;
        }
        .etq-num-right {
            font-size: 18px;
            line-height: 1.35;
        }
        .etq-middle {
            min-height: 145px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 18px;
            line-height: 1.2;
        }
        .etq-unit,
        .etq-month {
            text-align: center;
            font-size: 14px;
            line-height: 1.2;
        }
        .etq-unit strong,
        .etq-month strong {
            font-size: 17px;
        }
        .etq-obs {
            font-weight: 700;
        }
        </style>
        <div class="etq-wrap">
            <div class="etq-card">
                <div class="etq-row etq-top">
                    <div><strong>SETOR ORIGEM</strong> - <span>(setor responsavel pelo acondicionamento das GTA's, pode ser a Regional ou a propria unidade)</span></div>
                </div>
                <div class="etq-row etq-num">
                    <div class="etq-num-left">Nº</div>
                    <div class="etq-num-right">(Campo destinado ao uso do arquivo.<br>Nao preenche-lo nem encobrir com fita adesiva)</div>
                </div>
                <div class="etq-row etq-middle">
                    <div>
                        Nome do documento, sucinto e objetivo. Este campo pode ser alongado para baixo, ate que a etiqueta atinja o limite da desse espaco. Utilizar a maior fonte possivel, de acordo com o tamanho da informacao aqui contida.
                    </div>
                </div>
                <div class="etq-row etq-unit">
                    <strong>UNIDADE:</strong> Unidade a que se referem os documentos. Unidade pela qual se procurara quando se demandar pesquisa.<br>
                    <span class="etq-obs">Obs:</span> pode-se colocar GTA's mais de uma unidade. Nesse caso, todas as Unidades devem ser descritas nesse espaco e <span class="etq-obs">no campo abaixo so se podera colocar um unico mes.</span>
                </div>
                <div class="etq-row etq-month">
                    <strong>MES/ANO:</strong> pode-se colocar GTA's de mais de um mes. Nesse caso, todos os meses devem ser descritos nesse espaco e <span class="etq-obs">no campo acima so se podera colocar uma unidade.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _normalize_items(raw_text: str) -> list[str]:
    items = []
    for line in (raw_text or "").splitlines():
        cleaned = line.strip().lstrip("•").lstrip(".").strip()
        if cleaned:
            items.append(cleaned)
    return items


def _fit_font_size(text: str, max_width: float, font_name: str, base_size: int, min_size: int) -> int:
    text = (text or "").strip()
    if not text:
        return base_size

    font_size = base_size
    while font_size > min_size and stringWidth(text, font_name, font_size) > max_width:
        font_size -= 1
    return font_size


def _draw_centered_text(
    c: canvas.Canvas,
    text: str,
    x_center: float,
    y_center: float,
    max_width: float,
    base_size: int,
    min_size: int,
):
    text = (text or "").strip()
    font_name = "Helvetica-Bold"
    font_size = _fit_font_size(text, max_width, font_name, base_size, min_size)
    c.setFont(font_name, font_size)
    c.drawCentredString(x_center, y_center - (font_size * 0.35), text)


def build_pdf_etiqueta_arquivo(
    *,
    ulsav_topo: str,
    numero: str,
    itens_texto: str,
    ulsav_base: str,
    ano: str,
) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    label_width = LABEL_WIDTH_MM * mm
    label_height = LABEL_HEIGHT_MM * mm
    row_heights = [value * mm for value in ROW_HEIGHTS_MM]

    x = (page_width - label_width) / 2
    y = (page_height - label_height) / 2

    c.setLineWidth(0.8)
    c.rect(x, y, label_width, label_height)

    current_top = y + label_height
    row_centers = []
    for idx, row_height in enumerate(row_heights):
        row_top = current_top
        row_bottom = row_top - row_height
        row_centers.append((row_top + row_bottom) / 2)
        if idx < len(row_heights) - 1:
            c.line(x, row_bottom, x + label_width, row_bottom)
        current_top = row_bottom

    _draw_centered_text(
        c,
        (ulsav_topo or "").upper(),
        x + (label_width / 2),
        row_centers[0],
        label_width - (8 * mm),
        base_size=16,
        min_size=10,
    )

    numero_top = y + label_height - row_heights[0]
    c.setFont("Helvetica-Bold", 34)
    c.drawString(x + 3 * mm, numero_top - 12 * mm, "Nº")
    if numero:
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x + 24 * mm, numero_top - 11 * mm, numero.strip())

    itens = _normalize_items(itens_texto)
    middle_top = y + label_height - row_heights[0] - row_heights[1]
    middle_height = row_heights[2]
    start_y = middle_top - 8 * mm
    line_step = 7.5 * mm
    c.setFont("Helvetica-Bold", 12.5)
    for idx, item in enumerate(itens[:6]):
        y_line = start_y - (idx * line_step)
        if y_line < (middle_top - middle_height + 5 * mm):
            break
        c.drawString(x + 8 * mm, y_line, f"• {item}")

    _draw_centered_text(
        c,
        (ulsav_base or "").upper(),
        x + (label_width / 2),
        row_centers[3],
        label_width - (8 * mm),
        base_size=18,
        min_size=11,
    )

    _draw_centered_text(
        c,
        ano,
        x + (label_width / 2),
        row_centers[4],
        label_width - (8 * mm),
        base_size=22,
        min_size=14,
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def render_etiqueta_arquivo():
    st.session_state.setdefault("etiqueta_ulsav_topo", "ULSAV SÃO MIGUEL DO GUAPORÉ")
    st.session_state.setdefault("etiqueta_numero", "")
    st.session_state.setdefault("etiqueta_itens", "")
    st.session_state.setdefault("etiqueta_ulsav_base", "SÃO MIGUEL DO GUAPORÉ")
    st.session_state.setdefault("etiqueta_ano", "")

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.title("Etiqueta de Arquivo")
        st.caption("Etiqueta em PDF com medida aproximada de 11,5 x 14,5 cm.")
        _render_instruction_diagram()

        with st.form("form_etiqueta_arquivo"):
            st.text_input("ULSAV - parte superior", key="etiqueta_ulsav_topo")
            st.text_input("Número", key="etiqueta_numero")
            st.text_area(
                "Itens da pasta",
                key="etiqueta_itens",
                height=140,
                help="Digite um item por linha. Cada linha será gerada com ponto na frente.",
                placeholder="documento 1\ndocumento 2\ndocumento 3\ndocumento 4",
            )
            st.text_input("ULSAV - parte inferior", key="etiqueta_ulsav_base")
            st.text_input("Ano", key="etiqueta_ano")

            submit = st.form_submit_button("Gerar PDF")

        if submit:
            pdf_bytes = build_pdf_etiqueta_arquivo(
                ulsav_topo=st.session_state.get("etiqueta_ulsav_topo", ""),
                numero=st.session_state.get("etiqueta_numero", ""),
                itens_texto=st.session_state.get("etiqueta_itens", ""),
                ulsav_base=st.session_state.get("etiqueta_ulsav_base", ""),
                ano=st.session_state.get("etiqueta_ano", ""),
            )

            st.session_state["etiqueta_arquivo_pdf"] = pdf_bytes

            output_dir = Path(__file__).resolve().parents[1] / "pdf"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "Etiqueta arquivo.pdf"
            output_path.write_bytes(pdf_bytes)
            st.session_state["etiqueta_arquivo_pdf_path"] = output_path
            st.success("PDF gerado e salvo.")

        if "etiqueta_arquivo_pdf" in st.session_state:
            try:
                st.pdf(st.session_state["etiqueta_arquivo_pdf"])
            except StreamlitAPIException:
                st.info("Pré-visualização indisponível. Instale streamlit[pdf].")

            st.download_button(
                "Baixar PDF",
                data=st.session_state["etiqueta_arquivo_pdf"],
                file_name="Etiqueta arquivo.pdf",
                mime="application/pdf",
            )
            if "etiqueta_arquivo_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['etiqueta_arquivo_pdf_path']}")
