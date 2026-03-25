from datetime import date, datetime
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
    margin = 20 * mm
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


def _draw_label_value(c: canvas.Canvas, x: float, y: float, label: str, value: str) -> float:
    c.setFont("Helvetica-Bold", 10)
    label_text = f"{label} "
    c.drawString(x, y, label_text)
    c.setFont("Helvetica", 10)
    c.drawString(x + stringWidth(label_text, "Helvetica-Bold", 10), y, value)
    return y - 6 * mm


def _safe_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _fmt_date(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    if value:
        return str(value)
    return ""


def _sync_field_from_source(source_key: str, target_key: str):
    source_value = st.session_state.get(source_key, "")
    target_value = st.session_state.get(target_key, "")
    prev_source_key = f"_{target_key}_prev_source"
    prev_source_value = st.session_state.get(prev_source_key, "")

    if target_value in ("", prev_source_value):
        st.session_state[target_key] = source_value

    st.session_state[prev_source_key] = source_value


def _build_declaracao_texto(data: dict) -> tuple[str, str]:
    nome = data.get("nome", "").strip() or "____________________________"
    nacionalidade = data.get("nacionalidade", "").strip() or "____________________________"
    profissao = data.get("profissao", "").strip() or "____________________________"
    rg = data.get("rg", "").strip() or "____________________________"
    orgao_emissor = data.get("orgao_emissor", "").strip()
    cpf_cnpj = data.get("cpf_cnpj", "").strip() or "____________________________"
    ulsav = data.get("ulsav", "").strip() or "____________________________"
    endereco = data.get("endereco", "").strip() or "____________________________"
    municipio = data.get("municipio", "").strip() or "____________________________"
    uf = data.get("uf", "").strip() or "RO"

    rg_completo = f"{rg} {orgao_emissor}".strip()

    texto_principal = (
        f"Declaramos para os devidos fins de direito, que {nome}, {nacionalidade}, "
        f"{profissao}, portador(a) do RG n.º {rg_completo}, e do CPF/CNPJ n.º {cpf_cnpj}, "
        "encontra-se com rebanho da espécie SUÍNA devidamente regular quanto ao "
        f"cumprimento das exigências sanitárias e cadastrado junto à ULSAV de {ulsav}, "
        f"localizado no endereço: {endereco}, no município de {municipio} - {uf}."
    )
    texto_responsabilidade = (
        "A IDARON não certifica a relação jurídica de posse que o(s) titular(es) da "
        "ficha de controle sanitário possui(em) com os animais (bens) abaixo declarados, "
        "e as informações do rebanho foram prestadas pelo produtor, sendo, portanto, de "
        "sua inteira responsabilidade."
    )
    return texto_principal, texto_responsabilidade


def _draw_table_header(
    c: canvas.Canvas, col_x: list[float], y_top: float, row_h: float, header_h: float
) -> float:
    labels = [
        "Reprodutor",
        "Matriz",
        "Leitão M",
        "Leitão F",
        "Idade e Sexo\nnão relev.",
        "Total de\nAnimais",
    ]

    c.rect(col_x[0], y_top - header_h, col_x[-1] - col_x[0], header_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 8.5)

    for idx, label in enumerate(labels):
        x_left = col_x[idx]
        x_right = col_x[idx + 1]
        linhas = label.split("\n")
        y_text = y_top - 4.8 * mm
        if len(linhas) == 2:
            y_text = y_top - 3.4 * mm
        for linha_idx, linha in enumerate(linhas):
            c.drawCentredString((x_left + x_right) / 2, y_text - linha_idx * 3.8 * mm, linha)

    return y_top - header_h


def _draw_estratificacao_table(c: canvas.Canvas, x: float, y_top: float, width: float, data: dict) -> float:
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y_top, "Estratificação - SUÍNOS")
    y_top -= 2 * mm

    col_widths = [24 * mm, 24 * mm, 24 * mm, 24 * mm, 32 * mm, 28 * mm]
    scale = width / sum(col_widths)
    col_widths = [w * scale for w in col_widths]
    col_x = [x]
    for item in col_widths:
        col_x.append(col_x[-1] + item)

    header_h = 10 * mm
    row_h = 8 * mm
    table_top = y_top
    body_top = _draw_table_header(c, col_x, table_top, row_h, header_h)

    c.setLineWidth(0.7)
    c.rect(x, body_top - row_h, width, row_h)
    for x_line in col_x[1:-1]:
        c.line(x_line, table_top - header_h - row_h, x_line, table_top)

    valores = [
        str(_safe_int(data.get("reprodutor"))),
        str(_safe_int(data.get("matriz"))),
        str(_safe_int(data.get("leitao_m"))),
        str(_safe_int(data.get("leitao_f"))),
        str(_safe_int(data.get("idade_sexo_nao_relevante"))),
        str(_safe_int(data.get("total_animais"))),
    ]

    c.setFont("Helvetica-Bold", 10)
    for idx, valor in enumerate(valores):
        c.drawCentredString((col_x[idx] + col_x[idx + 1]) / 2, body_top - 5.2 * mm, valor)

    return body_top - row_h - 4 * mm


def _draw_labeled_box(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    height: float,
    label: str,
    value: str,
    value_font: int = 8,
) -> None:
    c.rect(x, y_top - height, width, height)
    c.setFont("Helvetica-Bold", 6.3)
    c.drawString(x + 1.2 * mm, y_top - 2.8 * mm, label)
    c.setFont("Helvetica", value_font)
    linhas = _wrap_text(value or "", "Helvetica", value_font, width - 2.6 * mm)
    y_text = y_top - 6.4 * mm
    for linha in linhas[:3]:
        c.drawString(x + 1.2 * mm, y_text, linha)
        y_text -= 3.4 * mm


def _draw_imovel_section(c: canvas.Canvas, x: float, y_top: float, width: float, data: dict) -> float:
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(x, y_top, "Dados do Imóvel Rural aonde os animais se encontram")
    y_top -= 2 * mm

    row1_h = 9 * mm
    row2_h = 9 * mm
    row3_h = 9 * mm

    cpf_w = 34 * mm
    nome_w = 78 * mm
    cod_prop_w = width - cpf_w - nome_w
    _draw_labeled_box(c, x, y_top, cpf_w, row1_h, "CPF/CNPJ DO PROP.", data.get("cpf_cnpj_prop", ""))
    _draw_labeled_box(c, x + cpf_w, y_top, nome_w, row1_h, "NOME DO PROP. DO IMÓVEL", data.get("nome_prop_imovel", ""))
    _draw_labeled_box(c, x + cpf_w + nome_w, y_top, cod_prop_w, row1_h, "CÓD. PROPRIEDADE PGA", data.get("cod_propriedade_pga", ""))
    y_top -= row1_h

    vinculo_w = 78 * mm
    abertura_w = 52 * mm
    exploracao_w = width - vinculo_w - abertura_w
    _draw_labeled_box(c, x, y_top, vinculo_w, row2_h, "Tipo de Vínculo do Pecuarista com a Terra", data.get("tipo_vinculo", ""))
    _draw_labeled_box(c, x + vinculo_w, y_top, abertura_w, row2_h, "Data de abertura da ficha", data.get("data_abertura_ficha", ""))
    _draw_labeled_box(c, x + vinculo_w + abertura_w, y_top, exploracao_w, row2_h, "CÓD. EXPLORAÇÃO PGA", data.get("cod_exploracao_pga", ""))
    y_top -= row2_h

    local_data = data.get("local_data_extenso", "").strip()
    c.setFont("Helvetica", 9)
    c.drawString(x, y_top - 5 * mm, local_data)
    y_top -= row3_h

    return y_top


def _draw_observacoes_section(c: canvas.Canvas, x: float, y_top: float, width: float, observacoes: str) -> float:
    texto = (observacoes or "").strip()
    if not texto:
        return y_top

    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x, y_top, "Observações:")
    y_top -= 5 * mm

    c.setFont("Helvetica", 9)
    for linha in _wrap_text(texto, "Helvetica", 9, width):
        c.drawString(x, y_top, linha)
        y_top -= 4.4 * mm

    return y_top - 3 * mm


def _draw_emitente_section(c: canvas.Canvas, x: float, y_top: float, width: float, data: dict) -> float:
    numero = data.get("numero_declaracao", "").strip() or "____________________________"
    c.setFont("Helvetica-Bold", 8.8)
    c.drawRightString(x + width, y_top, f"DECLARAÇÃO - N.º {numero}")
    y_top -= 5 * mm

    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x, y_top, "Identificação do Emitente:")
    y_top -= 5 * mm

    y_top = _draw_label_value(c, x, y_top, "Nome:", data.get("emitente_nome", "").strip() or "____________________________")
    y_top = _draw_label_value(c, x, y_top, "Cargo:", data.get("emitente_cargo", "").strip() or "____________________________")
    y_top = _draw_label_value(c, x, y_top, "Matrícula:", data.get("emitente_matricula", "").strip() or "____________________________")
    return y_top


def build_pdf_declaracao_cadastral_suinos(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    title_y = _draw_restituicao_header(c, page_width, page_height, logo_path)

    margin = 20 * mm
    width = page_width - 2 * margin
    y = title_y - 8 * mm

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(page_width / 2, y, "DECLARAÇÃO CADASTRAL - SUÍNOS")
    y -= 8 * mm

    ulsav = data.get("ulsav", "").strip() or "____________________________"
    numero = data.get("numero_declaracao", "").strip() or "____________________________"
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_width / 2, y, f"ULSAV: {ulsav}")
    y -= 5.5 * mm
    c.drawCentredString(page_width / 2, y, f"DECLARAÇÃO - N.º: {numero}")
    y -= 7 * mm

    texto_principal, texto_responsabilidade = _build_declaracao_texto(data)
    c.setFont("Helvetica", 9.5)
    for linha in _wrap_text(texto_principal, "Helvetica", 9.5, width):
        c.drawString(margin, y, linha)
        y -= 4.6 * mm

    y -= 1 * mm
    for linha in _wrap_text(texto_responsabilidade, "Helvetica", 9.5, width):
        c.drawString(margin, y, linha)
        y -= 4.6 * mm

    y -= 2 * mm
    y = _draw_estratificacao_table(c, margin, y, width, data)
    y = _draw_imovel_section(c, margin, y, width, data)
    y = _draw_observacoes_section(c, margin, y - 1 * mm, width, data.get("observacoes", ""))
    _draw_emitente_section(c, margin, y, width, data)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def render_declaracao_cadastral_suinos():
    st.session_state.setdefault("dcs_reprodutor", 0)
    st.session_state.setdefault("dcs_matriz", 0)
    st.session_state.setdefault("dcs_leitao_m", 0)
    st.session_state.setdefault("dcs_leitao_f", 0)
    st.session_state.setdefault("dcs_idade_sexo_nao_relevante", 0)
    st.session_state.setdefault("dcs_data_abertura_ficha", date.today())
    st.session_state.setdefault("dcs_data_documento", date.today())
    st.session_state.setdefault(
        "dcs_observacoes",
        "Acompanha um print do cadastro no sistema eletronico de informações da agencia SIS IDARON.",
    )

    total_animais = (
        _safe_int(st.session_state.get("dcs_reprodutor"))
        + _safe_int(st.session_state.get("dcs_matriz"))
        + _safe_int(st.session_state.get("dcs_leitao_m"))
        + _safe_int(st.session_state.get("dcs_leitao_f"))
        + _safe_int(st.session_state.get("dcs_idade_sexo_nao_relevante"))
    )

    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("## Declaração cadastral - suínos")

        st.text_input("ULSAV", key="dcs_ulsav")
        st.text_input("Número da declaração (ex.: 0165/2026)", key="dcs_numero_declaracao")
        st.text_input("Nome do produtor", key="dcs_nome")

        col_dados = st.columns(2)
        with col_dados[0]:
            st.text_input("Nacionalidade", key="dcs_nacionalidade", value="brasileiro(a)")
        with col_dados[1]:
            st.text_input("Profissão", key="dcs_profissao", value="suinocultor(a)")

        col_docs = st.columns(2)
        with col_docs[0]:
            st.text_input("RG", key="dcs_rg")
        with col_docs[1]:
            st.text_input("Órgão expedidor", key="dcs_orgao_emissor", value="SSP/RO")

        st.text_input("CPF/CNPJ", key="dcs_cpf_cnpj")
        st.text_input("Endereço da propriedade", key="dcs_endereco")

        _sync_field_from_source("dcs_ulsav", "dcs_municipio")
        col_local = st.columns(2)
        with col_local[0]:
            st.text_input("Município", key="dcs_municipio")
        with col_local[1]:
            st.text_input("UF", key="dcs_uf", value="RO")

        st.markdown("### Estratificação - suínos")
        col_animais = st.columns(3)
        with col_animais[0]:
            st.number_input("Reprodutor", key="dcs_reprodutor", min_value=0, step=1)
            st.number_input("Leitão M", key="dcs_leitao_m", min_value=0, step=1)
        with col_animais[1]:
            st.number_input("Matriz", key="dcs_matriz", min_value=0, step=1)
            st.number_input("Leitão F", key="dcs_leitao_f", min_value=0, step=1)
        with col_animais[2]:
            st.number_input("Idade e sexo não relevante", key="dcs_idade_sexo_nao_relevante", min_value=0, step=1)
            st.text_input("Total de animais", value=str(total_animais), disabled=True)

        st.markdown("### Dados do imóvel rural")
        st.caption("Nome e CPF/CNPJ do proprietário são preenchidos automaticamente com os dados do produtor, mas podem ser alterados se necessário.")
        _sync_field_from_source("dcs_nome", "dcs_nome_prop_imovel")
        _sync_field_from_source("dcs_cpf_cnpj", "dcs_cpf_cnpj_prop")
        col_prop = st.columns(2)
        with col_prop[0]:
            st.text_input("CPF/CNPJ do proprietário do imóvel", key="dcs_cpf_cnpj_prop")
            st.text_input("Tipo de vínculo do pecuarista com a terra", key="dcs_tipo_vinculo", value="PROPRIETÁRIO")
        with col_prop[1]:
            st.text_input("Nome do proprietário do imóvel", key="dcs_nome_prop_imovel")
            st.text_input("Cód. propriedade PGA", key="dcs_cod_propriedade_pga")
            st.text_input("Cód. exploração PGA", key="dcs_cod_exploracao_pga")

        col_ficha = st.columns(2)
        with col_ficha[0]:
            st.date_input("Data de abertura da ficha", key="dcs_data_abertura_ficha", value=date.today())
        with col_ficha[1]:
            st.date_input("Data do documento", key="dcs_data_documento", value=date.today())

        st.text_area("Observações", key="dcs_observacoes", height=70)

        st.markdown("### Identificação do emitente")
        st.text_input("Nome do emitente", key="dcs_emitente_nome")
        col_emit = st.columns(2)
        with col_emit[0]:
            st.text_input("Cargo", key="dcs_emitente_cargo")
        with col_emit[1]:
            st.text_input("Matrícula", key="dcs_emitente_matricula")

        gerar = st.button("Gerar PDF")

        if gerar:
            logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
            data_documento = st.session_state.get("dcs_data_documento", date.today())
            municipio = st.session_state.get("dcs_municipio", "").strip()
            data_texto = _fmt_date(data_documento)
            local_data_extenso = f"{municipio}, {data_texto}." if municipio else data_texto
            data = {
                "ulsav": st.session_state.get("dcs_ulsav", ""),
                "numero_declaracao": st.session_state.get("dcs_numero_declaracao", ""),
                "nome": st.session_state.get("dcs_nome", ""),
                "nacionalidade": st.session_state.get("dcs_nacionalidade", ""),
                "profissao": st.session_state.get("dcs_profissao", ""),
                "rg": st.session_state.get("dcs_rg", ""),
                "orgao_emissor": st.session_state.get("dcs_orgao_emissor", ""),
                "cpf_cnpj": st.session_state.get("dcs_cpf_cnpj", ""),
                "endereco": st.session_state.get("dcs_endereco", ""),
                "municipio": st.session_state.get("dcs_municipio", ""),
                "uf": st.session_state.get("dcs_uf", ""),
                "reprodutor": _safe_int(st.session_state.get("dcs_reprodutor")),
                "matriz": _safe_int(st.session_state.get("dcs_matriz")),
                "leitao_m": _safe_int(st.session_state.get("dcs_leitao_m")),
                "leitao_f": _safe_int(st.session_state.get("dcs_leitao_f")),
                "idade_sexo_nao_relevante": _safe_int(st.session_state.get("dcs_idade_sexo_nao_relevante")),
                "total_animais": total_animais,
                "cpf_cnpj_prop": st.session_state.get("dcs_cpf_cnpj_prop", ""),
                "nome_prop_imovel": st.session_state.get("dcs_nome_prop_imovel", ""),
                "cod_propriedade_pga": st.session_state.get("dcs_cod_propriedade_pga", ""),
                "observacoes": st.session_state.get("dcs_observacoes", ""),
                "tipo_vinculo": st.session_state.get("dcs_tipo_vinculo", ""),
                "data_abertura_ficha": _fmt_date(st.session_state.get("dcs_data_abertura_ficha")),
                "cod_exploracao_pga": st.session_state.get("dcs_cod_exploracao_pga", ""),
                "local_data_extenso": local_data_extenso,
                "emitente_nome": st.session_state.get("dcs_emitente_nome", ""),
                "emitente_cargo": st.session_state.get("dcs_emitente_cargo", ""),
                "emitente_matricula": st.session_state.get("dcs_emitente_matricula", ""),
            }
            pdf_bytes = build_pdf_declaracao_cadastral_suinos(data, logo_path)
            st.session_state["declaracao_cadastral_suinos_pdf"] = pdf_bytes

            output_dir = Path(__file__).resolve().parents[1] / "pdf"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "declaracao_cadastral_suinos.pdf"
            output_path.write_bytes(pdf_bytes)
            st.session_state["declaracao_cadastral_suinos_pdf_path"] = output_path
            st.success("PDF gerado e salvo.")

        if "declaracao_cadastral_suinos_pdf" in st.session_state:
            st.markdown("### Página de impressão")
            pdf_bytes = st.session_state["declaracao_cadastral_suinos_pdf"]
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
                file_name="declaracao_cadastral_suinos.pdf",
                mime="application/pdf",
            )
            if "declaracao_cadastral_suinos_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['declaracao_cadastral_suinos_pdf_path']}")
