import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from pdf.cabecalho import desenhar_cabecalho
from pdf.corpo import desenhar_tabela


st.set_page_config(page_title="Folha de Ponto", layout="centered")

MESES = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARÇO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}


def gerar_pdf(ano, mes, he, hs, feriados=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Define título interno do PDF
    c.setTitle("Folha de ponto")

    # Cabeçalho oficial
    y_top = desenhar_cabecalho(c)

    # Corpo
    desenhar_tabela(c, ano=ano, mes=mes, he=he, hs=hs, y_top=y_top, feriados=feriados or {})

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

col_mes, col_ano = st.columns(2)
with col_mes:
    mes_label = st.selectbox("Mês", list(MESES.keys()), index=0)
with col_ano:
    ano = st.selectbox("Ano", list(range(2026, 2036)), index=0)

# opções de horário
opcoes_he = [
    f"{h:02d}:{m:02d}"
    for h in range(5, 10)
    for m in (0, 30)
    if (h < 9 or (h == 9 and m == 0))
]
opcoes_hs = [
    f"{h:02d}:{m:02d}"
    for h in range(10, 18)
    for m in (0, 30)
    if not (h == 10 and m == 0)  # começa em 10:30
]

col_he, col_hs = st.columns(2)
with col_he:
    he = st.selectbox("Horário de entrada (HE)", opcoes_he, index=opcoes_he.index("07:30") if "07:30" in opcoes_he else 0)
with col_hs:
    hs = st.selectbox("Horário de saída (HS)", opcoes_hs, index=opcoes_hs.index("13:30") if "13:30" in opcoes_hs else 0)

feriados_texto = st.text_area(
    "Feriados (formato: dia-descrição, separados por vírgulas. Ex.: 1-Confraternização Universal, 15-Feriado Inventado, 21-Dia Tal)",
    value="",
    help=(
        "Use dia-descrição, separados por vírgulas. Ex.: 1-Confraternização Universal, "
        "15-Feriado inventado, 21-Dia tal (dia entre 1 e 31). "
        "Exemplo para colar: 1-Confraternização Universal, 15-Feriado Inventado, 21-Dia Tal."
    ),
)

st.write("""
Selecione o mês e o ano, gere o PDF com o cabeçalho oficial e depois baixe o arquivo.
""")

# Botão para gerar PDF
if st.button("Gerar PDF"):
    def parse_feriados(texto):
        feriados_dict = {}
        erros = []
        for raw_bloco in texto.split(","):
            bloco = raw_bloco.strip()
            if not bloco:
                continue
            if "-" not in bloco:
                erros.append(f'"{bloco}" (faltou "-")')
                continue
            dia_str, _, nome = bloco.partition("-")
            dia_str = dia_str.strip()
            nome = nome.strip()
            try:
                dia = int(dia_str)
            except ValueError:
                erros.append(f'"{bloco}" (dia inválido)')
                continue
            if not (1 <= dia <= 31):
                erros.append(f'"{bloco}" (dia fora de 1-31)')
                continue
            if not nome:
                erros.append(f'"{bloco}" (descrição vazia)')
                continue
            feriados_dict[dia] = nome
        return feriados_dict, erros

    feriados_dict, erros = parse_feriados(feriados_texto)
    if erros:
        st.error("Revise os feriados informados: " + "; ".join(erros))
    else:
        st.session_state["pdf"] = gerar_pdf(ano=ano, mes=MESES[mes_label], he=he, hs=hs, feriados=feriados_dict)
        st.success("PDF gerado com sucesso!")

# Botão de download
if "pdf" in st.session_state:
    st.download_button(
        "⬇️ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
