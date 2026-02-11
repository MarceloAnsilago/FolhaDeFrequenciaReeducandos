import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

VEICULO_MESES = [
    "Janeiro",
    "Fevereiro",
    "Marco",
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
VEICULO_ANOS = list(range(2026, 2037))

def build_pdf_veiculo(data: dict, logo_path: Path) -> bytes:
    buffer = BytesIO()
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    margin = 10 * mm
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
        rect_x + rect_w / 2, title_y + 2.2 * mm, "CONTROLE DE USO E SAIDA DE VEICULO"
    )

    info_y = title_y - 4 * mm
    info_h = 8 * mm
    c.rect(rect_x, info_y - info_h, rect_w, info_h)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(rect_x + 2 * mm, info_y - 7 * mm, f"ANO: {data['ano']} / MES: {data['mes']}")
    c.drawString(
        rect_x + 55 * mm,
        info_y - 7 * mm,
        f"NOME DA UNIDADE: {data['unidade'] or '______________________________'}",
    )
    c.drawString(
        rect_x + 140 * mm,
        info_y - 7 * mm,
        f"PLACA DO VEICULO: {data['placa']} ({data['modelo']})",
    )

    table_top = info_y - info_h
    bottom_area_h = 30 * mm
    table_bottom = margin + bottom_area_h
    table_height = table_top - table_bottom
    rows = 14
    row_h = table_height / rows

    col_widths = [18, 18, 18, 18, 16, 48, 82, 44]
    scale = rect_w / sum(col_widths)
    col_widths = [w * scale for w in col_widths]

    x = rect_x
    c.setLineWidth(0.5)
    for w in col_widths:
        c.line(x, table_bottom, x, table_top)
        x += w
    c.line(rect_x + rect_w, table_bottom, rect_x + rect_w, table_top)

    for i in range(rows + 1):
        y = table_top - i * row_h
        c.line(rect_x, y, rect_x + rect_w, y)

    headers = [
        "DATA",
        "HR SAIDA",
        "KM SAIDA",
        "HR CHEG",
        "KM CHEGADA",
        "DESTINO",
        "SERVICO REALIZADO DETALHADAMENTE",
        "NOME DO CONDUTOR POR EXTENSO",
    ]
    c.setFont("Helvetica-Bold", 6)
    x = rect_x
    y = table_top - row_h + 2 * mm
    for w, h in zip(col_widths, headers):
        c.drawCentredString(x + w / 2, y, h)
        x += w

    c.setFont("Helvetica", 7)
    first_col_x = rect_x + col_widths[0] / 2
    for i in range(1, rows):
        row_y = table_top - (i + 0.5) * row_h
        c.drawCentredString(first_col_x, row_y, "/    /")

    checklist_x = rect_x
    checklist_y = table_bottom - 6 * mm
    c.setFont("Helvetica-Bold", 7)
    c.drawString(checklist_x, checklist_y, "CHECKLIST:")
    c.setFont("Helvetica", 7)
    checklist_items = [
        "DOCUMENTO DE PORTE OBRIGATORIO ( )SIM ( )NAO",
        "CHAVE DE RODA ( )SIM ( )NAO",
        "MACACO ( )SIM ( )NAO",
        "TRIANGULO ( )SIM ( )NAO",
        "EXTINTOR ( )SIM ( )NAO",
        "ESTEPE ( )SIM ( )NAO",
    ]
    for idx, item in enumerate(checklist_items):
        c.drawString(checklist_x, checklist_y - (4 * mm) * (idx + 1), item)

    sig_y = margin + 8 * mm
    sig_x = rect_x + rect_w * 0.35
    sig_w = rect_w * 0.3
    c.line(sig_x, sig_y, sig_x + sig_w, sig_y)
    c.setFont("Helvetica", 7)
    c.drawCentredString(sig_x + sig_w / 2, sig_y - 4 * mm, "Assinatura do Chefe da Unidade")

    obs_x = rect_x + rect_w * 0.75
    obs_y = margin + 18 * mm
    c.setFont("Helvetica-Bold", 7)
    c.drawString(obs_x, obs_y, "OBS.:")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

def render_veiculos():
    st.title("Entrada e Saida de Veiculos")

    st.session_state.setdefault("veiculo_show_print", False)
    st.session_state.setdefault(
        "veiculo_form_data",
        {
            "mes": VEICULO_MESES[0],
            "ano": VEICULO_ANOS[0],
            "placa": "",
            "modelo": "",
            "unidade": "",
        },
    )

    with st.form("form_veiculo"):
        mes = st.selectbox("Mes", VEICULO_MESES)
        ano = st.selectbox("Ano", VEICULO_ANOS)
        unidade = st.text_input("Nome da unidade", placeholder="ULSAV SMG")
        placa = st.text_input("Placa do veiculo", placeholder="NDI 2293")
        modelo = st.text_input("Modelo do veiculo", placeholder="TOYOTA HILUX")
        submitted = st.form_submit_button("Gerar")

    if submitted:
        st.success("Formulario enviado")
        st.session_state["veiculo_form_data"] = {
            "mes": mes,
            "ano": ano,
            "unidade": unidade,
            "placa": placa,
            "modelo": modelo,
        }
        st.session_state["veiculo_show_print"] = True

    if st.session_state["veiculo_show_print"]:
        data = st.session_state["veiculo_form_data"]

        logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_inferior_dir.jpg"
        logo_b64 = ""
        if logo_path.exists():
            logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")

        st.markdown("## Pagina de impressao")
        pdf_bytes = build_pdf_veiculo(data, logo_path)
        st.download_button(
            "Baixar PDF",
            data=pdf_bytes,
            file_name="controle_uso_saida_veiculo.pdf",
            mime="application/pdf",
        )

        st.markdown(
            f"""
            <style>
            :root {{
                --a4-landscape-width: 297mm;
                --a4-landscape-height: 210mm;
            }}
            .print-page {{
                width: min(100%, var(--a4-landscape-width));
                height: var(--a4-landscape-height);
                border: 1px solid #999;
                padding: 10mm;
                box-sizing: border-box;
                margin: 0 auto;
                background: #fff;
            }}
            .top-rect {{
                width: 100%;
                height: 30mm;
                border: 1px solid #222;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
                margin-bottom: 0;
            }}
            .titulo-linha {{
                width: 100%;
                height: 6mm;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                letter-spacing: 0.5px;
                margin-bottom: 6mm;
                border-left: 1px solid #222;
                border-right: 1px solid #222;
                border-bottom: 1px solid #222;
            }}
            .top-rect img {{
                max-height: 32mm;
                max-width: 80%;
                object-fit: contain;
                margin-bottom: 2mm;
            }}
            .info-row {{
                border: 1px solid #222;
                border-top: none;
                height: 8mm;
                display: flex;
                align-items: center;
                font-size: 10px;
                padding: 0 4mm;
                gap: 12mm;
                box-sizing: border-box;
            }}
            .tabela {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10px;
            }}
            .tabela th, .tabela td {{
                border: 1px solid #222;
                padding: 1mm 1mm;
                height: 7mm;
            }}
            .tabela th {{
                font-weight: 700;
                text-align: center;
            }}
            .tabela td:first-child {{
                text-align: center;
                vertical-align: middle;
            }}
            .bottom-area {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 6mm;
                margin-top: 12mm;
                font-size: 10px;
            }}
            .checklist {{
                font-size: 9px;
                line-height: 1.4;
            }}
            .assinatura {{
                display: flex;
                align-items: flex-end;
                justify-content: center;
            }}
            .assinatura .linha {{
                width: 70%;
                border-top: 1px solid #222;
                text-align: center;
                padding-top: 2mm;
                font-size: 9px;
            }}
            .obs {{
                font-size: 9px;
                justify-self: end;
            }}
            @media screen {{
                .print-page {{
                    aspect-ratio: 297 / 210;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                }}
            }}
            </style>
            <div class="print-page">
                <div class="top-rect">
                    {"<img src='data:image/jpg;base64," + logo_b64 + "' alt='Logo' />" if logo_b64 else ""}
                </div>
                <div class="titulo-linha">CONTROLE DE USO E SAIDA DE VEICULO</div>
                <div class="info-row">
                    <div><strong>ANO:</strong> {data["ano"]} / <strong>MES:</strong> {data["mes"]}</div>
                    <div><strong>NOME DA UNIDADE:</strong> {data["unidade"] or "__________________________"}</div>
                    <div><strong>PLACA DO VEICULO:</strong> {data["placa"]} ({data["modelo"]})</div>
                </div>
                <table class="tabela">
                    <thead>
                        <tr>
                            <th>DATA</th>
                            <th>HR SAIDA</th>
                            <th>KM SAIDA</th>
                            <th>HR CHEG</th>
                            <th>KM CHEGADA</th>
                            <th>DESTINO</th>
                            <th>SERVICO REALIZADO DETALHADAMENTE</th>
                            <th>NOME DO CONDUTOR POR EXTENSO</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(["<tr>" + "".join(["<td>" + ("/    /" if i == 0 else "&nbsp;") + "</td>" for i in range(8)]) + "</tr>" for _ in range(14)])}
                    </tbody>
                </table>
                <div class="bottom-area">
                    <div class="checklist">
                        <strong>CHECKLIST:</strong><br/>
                        DOCUMENTO DE PORTE OBRIGATORIO ( )SIM ( )NAO<br/>
                        CHAVE DE RODA ( )SIM ( )NAO<br/>
                        MACACO ( )SIM ( )NAO<br/>
                        TRIANGULO ( )SIM ( )NAO<br/>
                        EXTINTOR ( )SIM ( )NAO<br/>
                        ESTEPE ( )SIM ( )NAO
                    </div>
                    <div class="assinatura">
                        <div class="linha">Assinatura do Chefe da Unidade</div>
                    </div>
                    <div class="obs"><strong>OBS.:</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
