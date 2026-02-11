import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from textwrap import dedent

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

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

def build_pdf_declaracao_nada_consta(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    margin = 20 * mm
    y = page_height - margin

    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        img_w, img_h = logo.getSize()
        max_w = page_width - 2 * margin
        max_h = 25 * mm
        scale = min(max_w / img_w, max_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale
        img_x = (page_width - draw_w) / 2
        y -= draw_h
        c.drawImage(logo, img_x, y, width=draw_w, height=draw_h, mask="auto")
        y -= 10 * mm
    else:
        y -= 10 * mm

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2, y, "DECLARAÇÃO")
    y -= 12 * mm

    c.setFont("Helvetica", 11)
    for linha in [
        data.get("destinatario", ""),
        "Requerente",
        data.get("nome_caps", ""),
        data.get("vocativo", ""),
    ]:
        if linha:
            c.drawString(margin, y, linha)
            y -= 6 * mm

    corpo = data.get("corpo", "")
    if corpo:
        y -= 2 * mm
        for linha in _wrap_text(corpo, "Helvetica", 11, page_width - 2 * margin):
            c.drawString(margin, y, linha)
            y -= 5 * mm

    y -= 6 * mm
    c.drawString(margin, y, "Atenciosamente,")
    y -= 14 * mm

    servidor_nome = data.get("servidor_nome") or data.get("nome_caps", "")
    servidor_cargo = data.get("servidor_cargo", "")
    servidor_matricula = data.get("servidor_matricula", "")
    incluir_assinatura_requerente = data.get("incluir_assinatura_requerente", True)
    requerente_nome = data.get("nome_caps", "").strip()
    requerente_cpf = data.get("cpf", "").strip()
    requerente_rg = data.get("rg", "").strip()

    if servidor_nome:
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_width / 2, y, servidor_nome)
        y -= 6 * mm
    if servidor_cargo:
        c.setFont("Helvetica", 10)
        c.drawCentredString(page_width / 2, y, f"Cargo: {servidor_cargo}")
        y -= 5 * mm
    if servidor_matricula:
        c.setFont("Helvetica", 10)
        c.drawCentredString(page_width / 2, y, f"Matricula: {servidor_matricula}")
        y -= 5 * mm

    if incluir_assinatura_requerente and (requerente_nome or requerente_cpf or requerente_rg):
        y -= 10 * mm
        if requerente_nome:
            c.setFont("Helvetica", 11)
            c.drawCentredString(page_width / 2, y, requerente_nome)
            y -= 6 * mm
        docs_requerente = []
        if requerente_cpf:
            docs_requerente.append(f"CPF: {requerente_cpf}")
        if requerente_rg:
            docs_requerente.append(f"RG: {requerente_rg}")
        if docs_requerente:
            c.setFont("Helvetica", 10)
            c.drawCentredString(page_width / 2, y, " | ".join(docs_requerente))
            y -= 5 * mm
        c.setFont("Helvetica", 10)
        c.drawCentredString(page_width / 2, y, "Assinatura do requerente")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

def render_declaracao_nada_consta():
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("## Declaracao de nada consta")
        st.session_state.setdefault("dnc_show_page", False)
        st.session_state.setdefault("dnc_page_data", {})
        with st.form("form_declaracao_nada_consta"):
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                st.radio("Sexo", ["Masculino", "Feminino"], key="dnc_sexo", horizontal=True)
            with col_c:
                st.date_input("Data", key="dnc_data", value=datetime.today())
            st.text_input("Nome", key="dnc_nome")
            st.text_input("CPF", key="dnc_cpf")
            st.text_input("RG", key="dnc_rg")
            st.text_input("Endereco", key="dnc_endereco")
            st.text_input("Municipio", key="dnc_municipio")
            st.markdown("---")
            st.text_input("Nome do servidor", key="dnc_servidor_nome")
            st.text_input("Cargo", key="dnc_servidor_cargo")
            st.text_input("Matricula", key="dnc_servidor_matricula")
            st.checkbox(
                "acrescentar assinatura do requerente",
                key="dnc_incluir_assinatura_requerente",
                value=True,
            )
            submitted = st.form_submit_button("Gerar")

        if submitted:
            sexo = st.session_state.get("dnc_sexo")
            destinatario = "Ao Ilustrissimo Sr." if sexo == "Masculino" else "A Ilustrissima Sra."
            vocativo = "Ilmo Sr." if sexo == "Masculino" else "Ilma Sra."
            nome = st.session_state.get("dnc_nome", "").strip()
            nome_caps = nome.upper()
            cpf = st.session_state.get("dnc_cpf", "").strip()
            rg = st.session_state.get("dnc_rg", "").strip()
            endereco = st.session_state.get("dnc_endereco", "").strip()
            municipio = st.session_state.get("dnc_municipio", "").strip()
            servidor_nome = st.session_state.get("dnc_servidor_nome", "").strip()
            servidor_cargo = st.session_state.get("dnc_servidor_cargo", "").strip()
            servidor_matricula = st.session_state.get("dnc_servidor_matricula", "").strip()
            incluir_assinatura_requerente = st.session_state.get(
                "dnc_incluir_assinatura_requerente", True
            )
            data_valor = st.session_state.get("dnc_data", datetime.today())
            data_solicitacao = data_valor.strftime("%d/%m/%Y")
            doc_partes = []
            if cpf:
                doc_partes.append(f"CPF {cpf}")
            if rg:
                doc_partes.append(f"RG {rg}")
            doc_identificacao = ", ".join(doc_partes)
            doc_segmento = f"{doc_identificacao}, " if doc_identificacao else ""

            corpo = (
                "Ao tempo que aproveitamos para cumprimentar Vossa Senhoria, "
                f"e em resposta a solicitacao de {data_solicitacao} e seus anexos, declaramos que, "
                f"{nome_caps}, {doc_segmento}residente e domiciliado {endereco}, no municipio de {municipio}, "
                "NAO POSSUI FICHA DE CADASTRO DE BENS SEMOVENTE ATIVA, na Agencia IDARON na presente data."
            )

            st.session_state["dnc_page_data"] = {
                "destinatario": destinatario,
                "vocativo": vocativo,
                "nome_caps": nome_caps,
                "cpf": cpf,
                "rg": rg,
                "corpo": corpo,
                "servidor_nome": servidor_nome,
                "servidor_cargo": servidor_cargo,
                "servidor_matricula": servidor_matricula,
                "incluir_assinatura_requerente": incluir_assinatura_requerente,
            }
            st.session_state["dnc_show_page"] = True

        if st.session_state.get("dnc_show_page"):
            data = st.session_state.get("dnc_page_data", {})
            nome_caps = data.get("nome_caps") or "____________________________"
            nome_caps_bruto = data.get("nome_caps", "").strip()
            cpf = data.get("cpf", "")
            rg = data.get("rg", "")
            servidor_nome = data.get("servidor_nome") or nome_caps
            servidor_cargo = data.get("servidor_cargo", "")
            servidor_matricula = data.get("servidor_matricula", "")
            incluir_assinatura_requerente = data.get("incluir_assinatura_requerente", True)
            cargo_label = f"Cargo: {servidor_cargo}" if servidor_cargo else ""
            matricula_label = f"Matricula: {servidor_matricula}" if servidor_matricula else ""
            requerente_docs = []
            if cpf:
                requerente_docs.append(f"CPF: {cpf}")
            if rg:
                requerente_docs.append(f"RG: {rg}")
            requerente_docs_label = " | ".join(requerente_docs)
            assinatura_requerente_html = ""
            if incluir_assinatura_requerente and (nome_caps_bruto or cpf or rg):
                docs_html = (
                    f'<div class="dnc-muted">{requerente_docs_label}</div>'
                    if requerente_docs_label
                    else ""
                )
                assinatura_requerente_html = (
                    f'<div class="dnc-sign"><div>{nome_caps_bruto}</div>'
                    f"{docs_html}"
                    '<div class="dnc-muted">Assinatura do requerente</div></div>'
                )

            logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
            logo_b64 = ""
            if logo_path.exists():
                logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")

            st.markdown(
                dedent(
                    f"""
                <style>
                :root {{
                    --a4-width: 210mm;
                    --a4-height: 297mm;
                }}
                .dnc-page {{
                    width: min(100%, var(--a4-width));
                    min-height: var(--a4-height);
                    border: 1px solid #999;
                    padding: 20mm;
                    box-sizing: border-box;
                    margin: 0 auto;
                    background: #fff;
                    font-family: Arial, sans-serif;
                    font-size: 12pt;
                    color: #111;
                }}
                .dnc-header {{
                    width: 100%;
                    height: auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-sizing: border-box;
                    margin-bottom: 10mm;
                }}
                .dnc-header img {{
                    max-height: 26mm;
                    max-width: 80%;
                    object-fit: contain;
                }}
                .dnc-title {{
                    text-align: center;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 12mm;
                }}
                .dnc-block {{
                    margin-bottom: 6mm;
                }}
                .dnc-body {{
                    text-align: justify;
                    text-indent: 2em;
                    line-height: 1.5;
                    margin: 10mm 0;
                }}
                .dnc-sign {{
                    margin-top: 22mm;
                    text-align: center;
                }}
                .dnc-muted {{
                    font-size: 10pt;
                }}
                @media screen {{
                    .dnc-page {{
                        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                    }}
                }}
                </style>
                <div class="dnc-page">
                    <div class="dnc-header">
                        {"<img src='data:image/jpg;base64," + logo_b64 + "' alt='Logo' />" if logo_b64 else ""}
                    </div>
                    <div class="dnc-title">DECLARAÇÃO</div>
                    <div class="dnc-block">{data.get("destinatario", "")}</div>
                    <div class="dnc-block">Requerente</div>
                    <div class="dnc-block"><strong>{nome_caps}</strong></div>
                    <div class="dnc-block">{data.get("vocativo", "")}</div>
                    <div class="dnc-body">{data.get("corpo", "")}</div>
                    <div class="dnc-block">Atenciosamente,</div>
                    <div class="dnc-sign">
                        <div>{servidor_nome}</div>
                        <div class="dnc-muted">{cargo_label}</div>
                        <div class="dnc-muted">{matricula_label}</div>
                    </div>
                    {assinatura_requerente_html}
                </div>
                """
                ),
                unsafe_allow_html=True,
            )

            st.markdown("### Pagina de impressao")
            pdf_bytes = build_pdf_declaracao_nada_consta(
                {
                    "destinatario": data.get("destinatario", ""),
                    "vocativo": data.get("vocativo", ""),
                    "nome_caps": nome_caps,
                    "corpo": data.get("corpo", ""),
                    "servidor_nome": servidor_nome,
                    "servidor_cargo": servidor_cargo,
                    "servidor_matricula": servidor_matricula,
                    "cpf": cpf,
                    "rg": rg,
                    "incluir_assinatura_requerente": incluir_assinatura_requerente,
                },
                logo_path,
            )
            st.download_button(
                "Baixar PDF",
                data=pdf_bytes,
                file_name="declaracao_nada_consta.pdf",
                mime="application/pdf",
            )
