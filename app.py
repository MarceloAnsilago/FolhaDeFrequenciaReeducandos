import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import re

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

try:
    from docx import Document
except ImportError:
    Document = None  # type: ignore

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

# session state defaults
DEFAULTS = {
    "secretaria": "",
    "reeducando": "",
    "funcao": "",
    "data_inclusao": "",
    "municipio": "",
    "cpf": "",
    "banco": "",
    "agencia": "",
    "conta": "",
    "tipo_conta": "",
    "endereco": "",
    "cep": "",
    "telefone": "",
    "data_preenchimento": "",
    "mes_label": list(MESES.keys())[0],
    "ano": list(range(2026, 2036))[0],
    "he": "07:30",
    "hs": "13:30",
    "feriados_texto": "",
}

for chave, valor in DEFAULTS.items():
    st.session_state.setdefault(chave, valor)


def _safe_index(options, value, default=0):
    try:
        return options.index(value)
    except Exception:
        return default


def _clean_text(texto: str) -> str:
    # normaliza espaços e sobe para maiúsculas para regex
    return re.sub(r"\s+", " ", texto).strip()


def _parse_campos(texto: str) -> dict:
    """Extrai campos do texto plano (PDF ou DOCX)."""
    norm = _clean_text(texto).upper()
    campos = {}

    def normaliza_tipo_conta(txt: str) -> str:
        t = txt.upper()
        if "CORRENTE" in t:
            return "Corrente"
        if "SAL" in t:  # SALÁRIO
            return "Salário"
        if "POUP" in t:
            return "Poupança"
        return txt

    def pega(padrao, grupo=1):
        m = re.search(padrao, norm)
        return m.group(grupo).strip() if m else ""

    campos["secretaria"] = pega(r"SECRETARIA:\s*(.+?)(?:\s+ANO:|$)")
    campos["ano"] = pega(r"ANO:\s*(\d{4})")
    campos["reeducando"] = pega(r"REEDUCANDO:\s*(.+?)(?:\s+M[ÊE]S:|$)")
    campos["mes_label"] = pega(r"M[ÊE]S:\s*([A-ZÇÃÕ]+)")
    campos["funcao"] = pega(r"FUNÇÃO:\s*(.+?)(?:\s+DATA DA INCLUSÃO:|$)")
    campos["data_inclusao"] = pega(r"DATA DA INCLUS[ÃA]O:\s*([\d/]+)")
    campos["municipio"] = pega(r"MUNIC[IÍ]PIO:\s*(.+?)(?:\s+CPF:|$)")
    campos["cpf"] = pega(r"CPF:\s*([\d.\-]+)")
    campos["banco"] = pega(r"BCO:\s*([A-Z0-9]+)")
    campos["agencia"] = pega(r"AG:\s*([A-Z0-9.\-]+)")
    campos["conta"] = pega(r"CONTA:\s*([A-Z0-9.\-]+)")
    campos["tipo_conta"] = normaliza_tipo_conta(pega(r"TIPO DE CONTA:\s*(.+)"))
    campos["endereco"] = pega(r"ENDEREÇO:\s*(.+?)(?:\s+CEP:|$)")
    campos["cep"] = pega(r"CEP:\s*([\d.\-]+)")
    campos["telefone"] = pega(r"TELEFONE:\s*([0-9\s\-]+)")
    campos["data_preenchimento"] = pega(r"DATA:\s*([0-9_/]+)")

    # remove repetições quando o texto veio duplicado no DOCX/PDF
    repetidos = {
        "secretaria": "SECRETARIA:",
        "reeducando": "REEDUCANDO:",
        "funcao": "FUNÇÃO:",
        "municipio": "MUNICÍPIO:",
        "endereco": "ENDEREÇO:",
    }
    for chave, marcador in repetidos.items():
        val = campos.get(chave, "")
        if val:
            up = val.upper()
            idx = up.find(marcador, len(marcador))  # procura segunda ocorrência
            if idx > 0:
                campos[chave] = val[:idx].strip()

    # ano para inteiro, se possível
    try:
        campos["ano"] = int(campos["ano"])
    except Exception:
        campos["ano"] = ""

    # saneia mês para opção conhecida
    mes_upper = campos.get("mes_label", "")
    if mes_upper in MESES:
        campos["mes_label"] = mes_upper
    elif mes_upper:
        # tenta capitalizar conforme dicionário
        for nome in MESES.keys():
            if nome.startswith(mes_upper[:3]):
                campos["mes_label"] = nome
                break

    return campos


def _ler_upload(arquivo) -> str:
    """Lê PDF ou DOCX enviado e devolve texto contínuo."""
    if not arquivo:
        return ""
    nome = arquivo.name.lower()
    dados = arquivo.read()
    if nome.endswith(".pdf"):
        if PdfReader is None:
            st.error("Instale PyPDF2 (pip install PyPDF2) para ler PDFs.")
            return ""
        reader = PdfReader(BytesIO(dados))
        textos = []
        for pagina in reader.pages:
            textos.append(pagina.extract_text() or "")
        return "\n".join(textos)
    if nome.endswith(".docx"):
        if Document is None:
            st.error("Instale python-docx (pip install python-docx) para ler DOCX.")
            return ""
        try:
            doc = Document(BytesIO(dados))
            linhas = []
            # parágrafos soltos
            for p in doc.paragraphs:
                if p.text and p.text.strip():
                    linhas.append(p.text)
            # textos das tabelas
            for tabela in doc.tables:
                for linha in tabela.rows:
                    for celula in linha.cells:
                        if celula.text and celula.text.strip():
                            linhas.append(celula.text)
            return "\n".join(linhas)
        except Exception as e:
            st.error(f"Erro ao ler DOCX: {e}")
            return ""
    return ""


def gerar_pdf(
    ano,
    mes,
    he,
    hs,
    endereco,
    cep,
    telefone,
    data_preenchimento,
    secretaria,
    reeducando,
    funcao,
    data_inclusao,
    municipio,
    cpf,
    banco,
    agencia,
    conta,
    tipo_conta,
    feriados=None,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Define título interno do PDF
    c.setTitle("Folha de ponto")

    # Cabeçalho oficial
    y_top = desenhar_cabecalho(c)

    # Corpo
    desenhar_tabela(
        c,
        ano=ano,
        mes=mes,
        he=he,
        hs=hs,
        y_top=y_top,
        feriados=feriados or {},
        endereco=endereco,
        cep=cep,
        telefone=telefone,
        data_preenchimento=data_preenchimento,
        secretaria=secretaria,
        reeducando=reeducando,
        funcao=funcao,
        data_inclusao=data_inclusao,
        municipio=municipio,
        cpf=cpf,
        banco=banco,
        agencia=agencia,
        conta=conta,
        tipo_conta=tipo_conta,
    )

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


st.title("Gerador de Folha de Ponto")

with st.expander("Importar dados (PDF ou DOCX)", expanded=False):
    arquivo = st.file_uploader("Selecione o PDF ou DOCX da última folha", type=["pdf", "docx"])
    if arquivo:
        texto = _ler_upload(arquivo)
        if not texto:
            st.warning("Não consegui ler o arquivo enviado.")
        else:
            campos = _parse_campos(texto)
            st.session_state.update({k: v for k, v in campos.items() if v})
            st.success("Campos preenchidos a partir do arquivo.")

with st.expander("Dados do Reeducando", expanded=True):
    secretaria_input = st.text_input("Secretaria", key="secretaria")
    reeducando_input = st.text_input("Reeducando", key="reeducando")
    funcao_input = st.text_input("Função", key="funcao")
    data_inclusao_input = st.text_input("Data da inclusão", key="data_inclusao")
    municipio_input = st.text_input("Município", key="municipio")

    col_doc = st.columns(3)
    with col_doc[0]:
        cpf_input = st.text_input("CPF", key="cpf")
    with col_doc[1]:
        banco_input = st.text_input("Banco (BCO)", key="banco")
    with col_doc[2]:
        agencia_input = st.text_input("Agência (AG)", key="agencia")
    conta_input = st.text_input("Conta", key="conta")
    tipo_opcoes = ["Corrente", "Salário", "Poupança", "Outro"]
    tipo_atual = st.session_state.get("tipo_conta", "")
    if tipo_atual not in tipo_opcoes or tipo_atual == "":
        tipo_radio = "Outro"
        tipo_outro_val = tipo_atual
    else:
        tipo_radio = tipo_atual
        tipo_outro_val = ""
    col_tipo = st.columns([1, 1])
    with col_tipo[0]:
        tipo_radio_sel = st.radio("Tipo de conta", tipo_opcoes, index=tipo_opcoes.index(tipo_radio))
    with col_tipo[1]:
        tipo_outro_val = st.text_input("Outro (se aplicável)", value=tipo_outro_val, key="tipo_conta_outro")
    # valor final do tipo de conta
    if tipo_radio_sel == "Outro":
        tipo_conta_input = tipo_outro_val
    else:
        tipo_conta_input = tipo_radio_sel

    endereco_input = st.text_input("Endereço", key="endereco")
    col_contato = st.columns(3)
    with col_contato[0]:
        cep_input = st.text_input("CEP", key="cep")
    with col_contato[1]:
        telefone_input = st.text_input("Telefone", key="telefone")
    with col_contato[2]:
        data_input = st.text_input("Data", key="data_preenchimento")

with st.expander("Preencher dados da folha", expanded=True):
    # saneia valores de mês/ano antes de criar os widgets
    if st.session_state.get("mes_label") not in MESES:
        st.session_state["mes_label"] = list(MESES.keys())[0]
    anos_opcoes = list(range(2026, 2036))
    ano_atual_ss = st.session_state.get("ano", anos_opcoes[0])
    if not isinstance(ano_atual_ss, int):
        try:
            ano_atual_ss = int(ano_atual_ss)
        except Exception:
            ano_atual_ss = anos_opcoes[0]
    if ano_atual_ss not in anos_opcoes:
        ano_atual_ss = anos_opcoes[0]
    st.session_state["ano"] = ano_atual_ss

    col_mes, col_ano = st.columns(2)
    with col_mes:
        mes_opcoes = list(MESES.keys())
        mes_label = st.selectbox("Mês", mes_opcoes, key="mes_label")
    with col_ano:
        ano = st.selectbox("Ano", anos_opcoes, key="ano")

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
        he_default = st.session_state.get("he", opcoes_he[0])
        he_index = _safe_index(opcoes_he, he_default, 0)
        he = st.selectbox("Horário de entrada (HE)", opcoes_he, index=he_index, key="he")
    with col_hs:
        hs_default = st.session_state.get("hs", opcoes_hs[0])
        hs_index = _safe_index(opcoes_hs, hs_default, 0)
        hs = st.selectbox("Horário de saída (HS)", opcoes_hs, index=hs_index, key="hs")

    feriados_texto = st.text_area(
        "Feriados (formato: dia-descrição, separados por vírgulas. Ex.: 1-Confraternização Universal, 15-Feriado Inventado, 21-Dia Tal)",
        value=st.session_state.get("feriados_texto", ""),
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
            st.session_state["feriados_texto"] = feriados_texto
            st.session_state["pdf"] = gerar_pdf(
                ano=ano,
                mes=MESES[mes_label],
                he=he,
                hs=hs,
                endereco=endereco_input,
                cep=cep_input,
                telefone=telefone_input,
                data_preenchimento=data_input,
                secretaria=secretaria_input,
                reeducando=reeducando_input,
                funcao=funcao_input,
                data_inclusao=data_inclusao_input,
                municipio=municipio_input,
                cpf=cpf_input,
                banco=banco_input,
                agencia=agencia_input,
                conta=conta_input,
                tipo_conta=tipo_conta_input,
                feriados=feriados_dict,
            )
            st.success("PDF gerado com sucesso!")

# Botão de download
if "pdf" in st.session_state:
    st.download_button(
        "⬇️ Baixar PDF",
        data=st.session_state["pdf"],
        file_name="folha.pdf",
        mime="application/pdf",
    )
