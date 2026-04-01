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
    linhas = []
    for paragrafo in (text or "").splitlines():
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
    return linhas or [""]


def _draw_box(c: canvas.Canvas, x: float, y_top: float, w: float, h: float) -> None:
    c.setLineWidth(0.6)
    c.rect(x, y_top - h, w, h)


def _draw_labeled_box(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    w: float,
    h: float,
    label: str,
    value: str,
    value_size: float = 8.5,
    max_lines: int = 3,
) -> None:
    _draw_box(c, x, y_top, w, h)
    pad_x = 1.5 * mm
    c.setFont("Helvetica", value_size)
    linhas = _wrap_text(value, "Helvetica", value_size, w - 3 * mm)
    if label:
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(x + pad_x, y_top - 3.3 * mm, label)
        y = y_top - 7 * mm
    else:
        y = y_top - 4.7 * mm
    c.setFont("Helvetica", value_size)
    for linha in linhas[:max_lines]:
        c.drawString(x + pad_x, y, linha)
        y -= 3.8 * mm


def _draw_centered_text_box(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    w: float,
    h: float,
    linhas: list[str],
    font_name: str,
    font_size: float,
    leading: float,
) -> None:
    _draw_box(c, x, y_top, w, h)
    c.setFont(font_name, font_size)
    total_h = max(len(linhas) - 1, 0) * leading
    y = y_top - (h / 2) + (total_h / 2) + 1.2 * mm
    for linha in linhas:
        c.drawCentredString(x + (w / 2), y, linha)
        y -= leading


def _draw_header(c: canvas.Canvas, x: float, y_top: float, w: float, h: float, logo_path: Path) -> None:
    logo_w = 24 * mm
    gov_w = 72 * mm
    title_w = w - logo_w - gov_w

    _draw_box(c, x, y_top, logo_w, h)
    _draw_centered_text_box(
        c,
        x + logo_w,
        y_top,
        gov_w,
        h,
        [
            "GOVERNO DO ESTADO DE RONDONIA",
            "AGENCIA DE DEFESA AGROSILVOPASTORIL",
            "DO ESTADO DE RONDONIA - IDARON",
        ],
        "Helvetica-Bold",
        7.1,
        3.8 * mm,
    )
    _draw_centered_text_box(
        c,
        x + logo_w + gov_w,
        y_top,
        title_w,
        h,
        [
            "AUTORIZACAO PROVISORIA DE",
            "VIAGEM OU TRANSITO FORA DO",
            "HORARIO DE EXPEDIENTE",
        ],
        "Helvetica-Bold",
        7.8,
        4.2 * mm,
    )

    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        img_w, img_h = logo.getSize()
        max_w = logo_w - 4 * mm
        max_h = h - 4 * mm
        escala = min(max_w / img_w, max_h / img_h)
        draw_w = img_w * escala
        draw_h = img_h * escala
        c.drawImage(
            logo,
            x + (logo_w - draw_w) / 2,
            y_top - h + (h - draw_h) / 2,
            width=draw_w,
            height=draw_h,
            mask="auto",
        )


def _draw_label_row(c: canvas.Canvas, x: float, y_top: float, w: float, h: float, split: float) -> None:
    left_w = w * split
    right_w = w - left_w
    _draw_box(c, x, y_top, left_w, h)
    _draw_box(c, x + left_w, y_top, right_w, h)

    c.setFont("Helvetica-Bold", 7.6)
    baseline_y = y_top - h + (h * 0.42)
    c.drawCentredString(x + (left_w / 2), baseline_y, "OBJETIVO")
    c.drawCentredString(x + left_w + (right_w / 2), baseline_y, "DESTINO")


def _draw_route_row(
    c: canvas.Canvas, x: float, y_top: float, w: float, h: float, data: dict, is_saida: bool
) -> tuple[float, float]:
    left_w = w * 0.46
    km_w = w * 0.12

    prefixo = "SAIDA" if is_saida else "CHEGADA"
    valor_data = data.get("saida_texto" if is_saida else "chegada_texto", "")
    valor_km = data.get("km_saida" if is_saida else "km_chegada", "")

    _draw_labeled_box(c, x, y_top, left_w, h, f"{prefixo}:", valor_data, value_size=8.5, max_lines=2)
    _draw_labeled_box(c, x + left_w, y_top, km_w, h, "KM:", valor_km, value_size=8.5, max_lines=2)
    return left_w + km_w, w - left_w - km_w


def _draw_formulario(c: canvas.Canvas, x: float, y_top: float, w: float, data: dict, logo_path: Path) -> None:
    y = y_top

    header_h = 19 * mm
    vehicle_h = 11 * mm
    section_label_h = 6 * mm
    objetivo_h = 18 * mm
    servidor_h = 23 * mm
    route_h = 10 * mm
    obs_h = 8 * mm

    _draw_header(c, x, y, w, header_h, logo_path)
    y -= header_h

    veiculo = f"PLACA {data.get('placa', '').strip()}    TIPO/MODELO: {data.get('tipo_modelo', '').strip()}"
    _draw_labeled_box(c, x, y, w, vehicle_h, "VEICULO", veiculo, value_size=8.8, max_lines=2)
    y -= vehicle_h

    _draw_label_row(c, x, y, w, section_label_h, 0.6)
    y -= section_label_h

    left_w = w * 0.6
    right_w = w - left_w
    _draw_labeled_box(c, x, y, left_w, objetivo_h, "", data.get("objetivo", ""), value_size=8.4, max_lines=4)
    _draw_labeled_box(c, x + left_w, y, right_w, objetivo_h, "", data.get("destino", ""), value_size=8.4, max_lines=4)
    y -= objetivo_h

    servidor_linhas = [
        f"SERVIDOR: {data.get('servidor', '').strip()}",
        f"CARGO/FUNCAO: {data.get('cargo_funcao', '').strip()}",
        f"MATRICULA: {data.get('matricula', '').strip()}",
        (
            "HABILITACAO: "
            f"{data.get('habilitacao', '').strip()}    - CATEGORIA: {data.get('categoria', '').strip()}    "
            f"- VALIDADE: {data.get('validade', '').strip()}"
        ),
    ]
    _draw_labeled_box(c, x, y, w, servidor_h, "", "\n".join(servidor_linhas), value_size=8.4, max_lines=5)
    y -= servidor_h

    resp_x, resp_w = _draw_route_row(c, x, y, w, route_h, data, is_saida=True)
    y -= route_h

    _draw_route_row(c, x, y, w, route_h, data, is_saida=False)
    _draw_labeled_box(
        c,
        x + resp_x,
        y + route_h,
        resp_w,
        route_h * 2,
        "Responsavel Transporte:",
        data.get("responsavel_transporte", ""),
        value_size=8.3,
        max_lines=4,
    )
    y -= route_h

    observacao = data.get("observacao", "").strip()
    _draw_labeled_box(c, x, y, w, obs_h, "OBS:", observacao, value_size=8.1, max_lines=2)


def build_pdf_autorizacao_viagem_manual(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    x = 10 * mm
    w = page_width - 20 * mm
    top_margin = 10 * mm
    form_h = 105 * mm
    gap = 11 * mm

    top1 = page_height - top_margin
    top2 = top1 - form_h - gap

    _draw_formulario(c, x, top1, w, data, logo_path)

    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(page_width / 2, top2 + 5 * mm, "2a VIA PARA O SETOR")

    _draw_formulario(c, x, top2, w, data, logo_path)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def render_autorizacao_viagem_manual():
    st.session_state.setdefault("avm_observacao", "VEICULO ENTREGUE EM PERFEITO ESTADO DE CONSERVACAO")

    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("## Autorização de viagem manual")
        st.caption("O PDF replica o primeiro quadro do modelo duas vezes na mesma folha.")

        with st.form("form_autorizacao_viagem_manual"):
            col_veiculo = st.columns(2)
            with col_veiculo[0]:
                st.text_input("Placa", key="avm_placa")
            with col_veiculo[1]:
                st.text_input("Tipo/modelo", key="avm_tipo_modelo")

            st.text_area("Objetivo", key="avm_objetivo", height=100)
            st.text_area("Destino", key="avm_destino", height=80)

            st.text_input("Servidor", key="avm_servidor")
            col_servidor = st.columns(3)
            with col_servidor[0]:
                st.text_input("Cargo/função", key="avm_cargo_funcao")
            with col_servidor[1]:
                st.text_input("Matrícula", key="avm_matricula")
            with col_servidor[2]:
                st.text_input("Habilitação", key="avm_habilitacao")

            col_cnh = st.columns(2)
            with col_cnh[0]:
                st.text_input("Categoria", key="avm_categoria")
            with col_cnh[1]:
                st.text_input("Validade", key="avm_validade", placeholder="18/12/2033")

            col_saida = st.columns(3)
            with col_saida[0]:
                st.text_input("Saída", key="avm_saida_texto", placeholder="25/03/2026 07:30")
            with col_saida[1]:
                st.text_input("KM saída", key="avm_km_saida")
            with col_saida[2]:
                st.text_input("Responsável transporte", key="avm_responsavel_transporte")

            col_chegada = st.columns(2)
            with col_chegada[0]:
                st.text_input("Chegada", key="avm_chegada_texto", placeholder="25/03/2026 18:00")
            with col_chegada[1]:
                st.text_input("KM chegada", key="avm_km_chegada")

            st.text_area("Observação", key="avm_observacao", height=70)
            submitted = st.form_submit_button("Gerar PDF")

        if submitted:
            logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_sugesp.png"
            data = {
                "placa": st.session_state.get("avm_placa", ""),
                "tipo_modelo": st.session_state.get("avm_tipo_modelo", ""),
                "objetivo": st.session_state.get("avm_objetivo", ""),
                "destino": st.session_state.get("avm_destino", ""),
                "servidor": st.session_state.get("avm_servidor", ""),
                "cargo_funcao": st.session_state.get("avm_cargo_funcao", ""),
                "matricula": st.session_state.get("avm_matricula", ""),
                "habilitacao": st.session_state.get("avm_habilitacao", ""),
                "categoria": st.session_state.get("avm_categoria", ""),
                "validade": st.session_state.get("avm_validade", ""),
                "saida_texto": st.session_state.get("avm_saida_texto", ""),
                "km_saida": st.session_state.get("avm_km_saida", ""),
                "responsavel_transporte": st.session_state.get("avm_responsavel_transporte", ""),
                "chegada_texto": st.session_state.get("avm_chegada_texto", ""),
                "km_chegada": st.session_state.get("avm_km_chegada", ""),
                "observacao": st.session_state.get("avm_observacao", ""),
            }
            pdf_bytes = build_pdf_autorizacao_viagem_manual(data, logo_path)
            st.session_state["autorizacao_viagem_manual_pdf"] = pdf_bytes

            output_dir = Path(__file__).resolve().parents[1] / "pdf"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "autorizacao_viagem_manual.pdf"
            output_path.write_bytes(pdf_bytes)
            st.session_state["autorizacao_viagem_manual_pdf_path"] = output_path
            st.success("PDF gerado e salvo.")

        if "autorizacao_viagem_manual_pdf" in st.session_state:
            st.markdown("### Página de impressão")
            pdf_bytes = st.session_state["autorizacao_viagem_manual_pdf"]
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
                file_name="autorizacao_viagem_manual.pdf",
                mime="application/pdf",
            )
            if "autorizacao_viagem_manual_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['autorizacao_viagem_manual_pdf_path']}")
