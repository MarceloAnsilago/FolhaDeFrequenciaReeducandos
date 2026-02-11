from datetime import datetime
from io import BytesIO
from pathlib import Path

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

def build_pdf_restituicao(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    margin = 15 * mm
    rect_h = 30 * mm
    rect_w = page_width - 2 * margin
    rect_x = margin
    rect_y = page_height - margin - rect_h

    c.setLineWidth(0.7)
    c.rect(rect_x, rect_y, rect_w, rect_h)

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

    title_h = 6 * mm
    title_y = rect_y - title_h
    c.setLineWidth(0.7)
    c.rect(rect_x, title_y, rect_w, title_h)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(
        rect_x + rect_w / 2,
        title_y + 2.2 * mm,
        "Requerimento de restituição de valor recolhido indevidamente",
    )

    x = margin
    y = title_y - 10 * mm
    line_h = 6 * mm

    def val_or_line(value: str) -> str:
        return value if value else "______________________________"

    def draw_label_value(label: str, value: str, y_pos: float) -> float:
        label_text = f"{label} "
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y_pos, label_text)
        c.setFont("Helvetica", 10)
        c.drawString(x + stringWidth(label_text, "Helvetica-Bold", 10), y_pos, value)
        return y_pos - line_h

    c.setFont("Helvetica-Bold", 10)
    c.drawString(
        x,
        y,
        "RESTITUIÇÃO DE VALOR RECOLHIDO INDEVIDAMENTE, REFERENTE A TAXAS",
    )
    y -= line_h

    def draw_checkbox(label: str, checked: bool, x_pos: float, y_pos: float) -> float:
        box = 4 * mm
        c.rect(x_pos, y_pos - 2.5 * mm, box, box)
        if checked:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos + 0.7 * mm, y_pos - 1.5 * mm, "X")
        c.setFont("Helvetica", 10)
        c.drawString(x_pos + box + 2 * mm, y_pos - 0.5 * mm, label)
        return x_pos + box + 2 * mm + stringWidth(label, "Helvetica", 10) + 6 * mm

    x_checks = x
    x_checks = draw_checkbox("GTA ONLINE", data.get("taxa_gta", False), x_checks, y)
    # Quebra a linha longa da multa para não estourar a página
    multa_label = (
        "MULTA DECORRENTES DA ATUAÇÃO DA AGÊNCIA DE DEFESA AGROSILVOPASTORIL "
        "DO ESTADO DE RONDÔNIA – IDARON"
    )
    box = 4 * mm
    y_multa = y - 6 * mm
    c.rect(x, y_multa - 2.5 * mm, box, box)
    if data.get("taxa_multa", False):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 0.7 * mm, y_multa - 1.5 * mm, "X")
    c.setFont("Helvetica", 10)
    label_x = x + box + 2 * mm
    max_w_label = page_width - margin - label_x
    for idx, linha in enumerate(_wrap_text(multa_label, "Helvetica", 10, max_w_label)):
        c.drawString(label_x, y_multa - (idx * 5 * mm), linha)
    y -= 6 * mm + (len(_wrap_text(multa_label, "Helvetica", 10, max_w_label)) * 5 * mm)

    y = draw_label_value("Nome:", val_or_line(data.get("nome", "")), y)
    y = draw_label_value("Nacionalidade:", val_or_line(data.get("nacionalidade", "")), y)
    y = draw_label_value("CPF/CNPJ:", val_or_line(data.get("cpf_cnpj", "")), y)
    y = draw_label_value("Residente e domiciliado:", val_or_line(data.get("residente", "")), y)
    y = draw_label_value("Município/Distrito:", val_or_line(data.get("municipio", "")), y)
    y = draw_label_value("Propriedade:", val_or_line(data.get("propriedade", "")), y)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "VEM REQUERER:")
    y -= line_h
    c.setFont("Helvetica", 10)
    vem_requerer = data.get("vem_requerer", "")
    max_w = page_width - 2 * margin
    for linha in _wrap_text(vem_requerer, "Helvetica", 10, max_w):
        c.drawString(x, y, linha)
        y -= 5 * mm
    y -= 2 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "JUSTIFICATIVA:")
    y -= line_h
    c.setFont("Helvetica", 10)
    justificativa = data.get("justificativa", "")
    for linha in _wrap_text(justificativa, "Helvetica", 10, max_w):
        c.drawString(x, y, linha)
        y -= 5 * mm

    y -= 2 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "DADOS DA CONTA BANCÁRIA PARA DEVOLUÇÃO:")
    y -= line_h

    y = draw_label_value("Nome do titular da conta:", val_or_line(data.get("titular", "")), y)
    y = draw_label_value("CPF:", val_or_line(data.get("conta_cpf", "")), y)
    y = draw_label_value("Banco:", val_or_line(data.get("banco", "")), y)
    y = draw_label_value("Agência:", val_or_line(data.get("agencia", "")), y)
    y = draw_label_value("Conta corrente:", val_or_line(data.get("conta_corrente", "")), y)
    y = draw_label_value("Número do banco:", val_or_line(data.get("numero_banco", "")), y)
    y = draw_label_value("Tipo:", val_or_line(data.get("tipo", "")), y)

    y -= 2 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "DECLARAÇÃO DE INEXISTÊNCIA DE PROCESSO DE RESTITUIÇÃO EM ANDAMENTO")
    y -= line_h
    c.setFont("Helvetica", 10)
    declaracao = data.get("declaracao", "")
    for linha in _wrap_text(declaracao, "Helvetica", 10, max_w):
        c.drawString(x, y, linha)
        y -= 5 * mm
    y -= 2 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "CÓDIGO DE BARRAS DO DARE (BOLETO):")
    y -= line_h
    y = draw_label_value("Código de barras:", val_or_line(data.get("codigo_barras", "")), y)

    local_data = f"{data.get('local', '')}, {data.get('data', '')}".strip(", ")
    y = draw_label_value("Local e data:", val_or_line(local_data), y)

    # assinatura centralizada no rodapé
    sig_y = margin + 12 * mm
    sig_w = 70 * mm
    sig_x = (page_width - sig_w) / 2
    c.line(sig_x, sig_y, sig_x + sig_w, sig_y)
    c.setFont("Helvetica", 9)
    nome_assinatura = data.get("nome", "").strip()
    if nome_assinatura:
        c.drawCentredString(sig_x + sig_w / 2, sig_y - 4 * mm, nome_assinatura)
    else:
        c.drawCentredString(sig_x + sig_w / 2, sig_y - 4 * mm, "Assinatura")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

def render_restituicao():
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.markdown("## Requerimento de restituição de valor recolhido indevidamente")
        with st.form("form_restituicao_inicial"):
            st.markdown("### Dados do requerente")
            st.text_input("Nome:", key="rest_nome")
            st.text_input("Nacionalidade?", key="rest_nacionalidade", value="Brasileiro(a)")
            st.text_input("CPF/CNPJ:", key="rest_cpf_cnpj")
            st.text_input("Residente e domiciliado", key="rest_residente")
            st.text_input("Municipio/distrito?", key="rest_municipio")
            st.text_input("Propiedade", key="rest_propiedade")
            st.markdown("### Taxas")
            st.checkbox("GTA Online", key="rest_taxa_gta")
            st.checkbox("Multa decorrente da atuação da IDARON", key="rest_taxa_multa")
            st.text_area(
                "Vem requerer:",
                value=(
                    "A restituição do valor recolhido indevidamente, referente ao pagamento de GTA Online, "
                    "conforme razões expostas a seguir:"
                ),
                height=90,
                key="rest_vem_requerer",
            )
            st.text_area(
                "Justificativa",
                value=(
                    "O requerente enviou o DARE para um dos filhos pagar, "
                    "que estava fora de área, em seguida enviou para a filha que pagou, "
                    "quando o filho entrou em área pagou novamente em duplicidade."
                ),
                height=140,
                key="rest_justificativa",
            )
            st.markdown("### DADOS DA CONTA BANCÁRIA PARA DEVOLUÇÃO:")
            st.text_input("Nome do titular da conta", key="rest_conta_titular")
            st.text_input("CPF", key="rest_conta_cpf")
            st.text_input("Banco", key="rest_conta_banco")
            st.text_input("Agência", key="rest_conta_agencia")
            st.text_input("Conta corrente", key="rest_conta_corrente")
            st.text_input("Número do banco", key="rest_conta_numero_banco")
            st.text_input("Tipo", key="rest_conta_tipo")
            st.markdown("### CÓDIGO DE BARRAS DO DARE (BOLETO):")
            st.text_input("Código de barras", key="rest_dare_codigo")
            st.text_input("Local", key="rest_local")
            st.date_input("Data", key="rest_data", value=datetime.today())
            st.text_area(
                "Declaração de inexistência de processo de restituição em andamento",
                value=(
                    "Declaro, para os devidos fins, que não existe outro processo de restituição "
                    "referente ao pagamento desta GTA em andamento no âmbito da IDARON."
                ),
                height=90,
                key="rest_declaracao",
            )
            submitted = st.form_submit_button("Salvar")

        if submitted:
            logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
            data = {
                "nome": st.session_state.get("rest_nome", ""),
                "nacionalidade": st.session_state.get("rest_nacionalidade", ""),
                "cpf_cnpj": st.session_state.get("rest_cpf_cnpj", ""),
                "residente": st.session_state.get("rest_residente", ""),
                "municipio": st.session_state.get("rest_municipio", ""),
                "propriedade": st.session_state.get("rest_propiedade", ""),
                "taxa_gta": st.session_state.get("rest_taxa_gta", False),
                "taxa_multa": st.session_state.get("rest_taxa_multa", False),
                "vem_requerer": st.session_state.get("rest_vem_requerer", ""),
                "justificativa": st.session_state.get("rest_justificativa", ""),
                "titular": st.session_state.get("rest_conta_titular", ""),
                "conta_cpf": st.session_state.get("rest_conta_cpf", ""),
                "banco": st.session_state.get("rest_conta_banco", ""),
                "agencia": st.session_state.get("rest_conta_agencia", ""),
                "conta_corrente": st.session_state.get("rest_conta_corrente", ""),
                "numero_banco": st.session_state.get("rest_conta_numero_banco", ""),
                "tipo": st.session_state.get("rest_conta_tipo", ""),
                "codigo_barras": st.session_state.get("rest_dare_codigo", ""),
                "declaracao": st.session_state.get("rest_declaracao", ""),
                "local": st.session_state.get("rest_local", ""),
                "data": st.session_state.get("rest_data", datetime.today()).strftime("%d/%m/%Y"),
            }
            pdf_bytes = build_pdf_restituicao(data, logo_path)
            st.session_state["restituicao_pdf"] = pdf_bytes

            output_dir = Path(__file__).resolve().parents[1] / "pdf"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "requerimento_restituicao.pdf"
            output_path.write_bytes(pdf_bytes)
            st.session_state["restituicao_pdf_path"] = output_path
            st.success("PDF gerado e salvo.")

        if "restituicao_pdf" in st.session_state:
            st.download_button(
                "Baixar PDF",
                data=st.session_state["restituicao_pdf"],
                file_name="requerimento_restituicao.pdf",
                mime="application/pdf",
            )
            if "restituicao_pdf_path" in st.session_state:
                st.caption(f"Salvo em: {st.session_state['restituicao_pdf_path']}")
