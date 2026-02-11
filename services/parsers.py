import re
from io import BytesIO

import streamlit as st

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

try:
    from docx import Document
except ImportError:
    Document = None  # type: ignore

from services.constants import MESES

def _safe_index(options, value, default=0):
    try:
        return options.index(value)
    except Exception:
        return default


def parse_feriados_text(texto):
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


def _clean_text(texto: str) -> str:
    # normaliza espaços e sobe para maiúsculas para regex
    return re.sub(r"\s+", " ", texto).strip()


def _parse_campos(texto: str) -> dict:
    """Extrai campos do texto plano (PDF ou DOCX)."""
    norm = _clean_text(texto).upper()
    campos = {}

    def normaliza_data(txt: str) -> str:
        if "_" in txt:
            return "__/__/____"
        bruto = txt.strip()
        digitos = re.sub(r"\D", "", bruto)
        if len(digitos) == 8:
            return f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
        if not digitos:
            return "__/__/____"
        return "__/__/____"

    def normaliza_tipo_conta(txt: str) -> str:
        t = txt.upper()
        t_norm = re.sub(r"\s+", " ", t)
        # prioridade: opção marcada com (X)
        if re.search(r"\(\s*X\s*\)\s*CORRENTE", t_norm):
            return "Corrente"
        if re.search(r"\(\s*X\s*\)\s*SAL[AA]RIO", t_norm):
            return "Salário"
        if re.search(r"\(\s*X\s*\)\s*POUPAN[CC]A", t_norm):
            return "Poupança"
        # fallback por palavra-chave
        if "POUP" in t:
            return "Poupança"
        if "SAL" in t:  # SALÁRIO
            return "Salário"
        if "CORRENTE" in t:
            return "Corrente"
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
    campos["data_preenchimento"] = normaliza_data(pega(r"DATA:\s*([0-9_/]+)"))

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


def _parse_campos_sugesp(texto: str) -> dict:
    norm = _clean_text(texto).upper()
    campos = {}

    def normaliza_data(txt: str) -> str:
        if "_" in txt:
            return "__/__/____"
        bruto = txt.strip()
        digitos = re.sub(r"\D", "", bruto)
        if len(digitos) == 8:
            return f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
        if not digitos:
            return "__/__/____"
        return "__/__/____"

    def pega(padrao, grupo=1):
        m = re.search(padrao, norm)
        return m.group(grupo).strip() if m else ""

    def remove_prefixo(valor: str, prefixo_regex: str) -> str:
        if not valor:
            return valor
        return re.sub(rf"^{prefixo_regex}\s*", "", valor, flags=re.IGNORECASE).strip()

    def corta_no_rotulo(valor: str, rotulo_regex: str) -> str:
        if not valor:
            return valor
        m = re.search(rotulo_regex, valor, flags=re.IGNORECASE)
        if not m:
            return valor
        # se o rótulo aparece no meio, mantém apenas a parte antes dele
        if m.start() > 0:
            return valor[: m.start()].strip()
        # se por algum motivo começar com rótulo, remove e retorna o restante
        return re.sub(rf"^{rotulo_regex}\s*", "", valor, flags=re.IGNORECASE).strip()

    campos["sugesp_unidade"] = pega(r"UNIDADE:\s*(.+?)(?:\s+ANO:|$)")
    campos["sugesp_ano"] = pega(r"ANO:\s*(\d{4})")
    campos["sugesp_sub_unidade"] = pega(r"SUB\s*UNIDADE:\s*(.+?)(?:\s+M[ÃŠE]S:|$)")
    campos["sugesp_mes_label"] = pega(r"M[ÃŠE]S:\s*([A-ZÃ‡ÃƒÃ•]+)")
    campos["sugesp_setor_lotacao"] = pega(r"SETOR DE LOTA[ÇC][ÃA]O:\s*(.+?)(?:\s+SERVIDOR:|$)")
    campos["sugesp_servidor"] = pega(r"SERVIDOR:\s*(.+?)(?:\s+MATR[IÍ]CULA:|$)")
    campos["sugesp_matricula"] = pega(r"MATR[IÍ]CULA:\s*([0-9]+)")
    campos["sugesp_sigla"] = pega(r"MATR[IÍ]CULA:\s*[0-9]+\s*([A-Z]{2,4})\b")
    campos["sugesp_cargo"] = pega(r"CARGO:\s*(.+?)(?:\s+DIA|$)")
    campos["sugesp_endereco"] = pega(r"ENDERE[ÇC]O:\s*(.+?)(?:\s+CEP:|$)")
    campos["sugesp_cep"] = pega(r"CEP:\s*([\d.\-]+)")
    campos["sugesp_telefone"] = pega(r"TELEFONE:\s*([0-9()\s\-]+)")
    campos["sugesp_email"] = pega(r"EMAIL:\s*([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})")
    campos["sugesp_cpf"] = pega(r"CPF:\s*([\d.\-]+)")
    campos["sugesp_data_preenchimento"] = normaliza_data(pega(r"DATA:\s*([0-9_/]+)"))

    # fallback: pega a sigla da celula abaixo do MES (entre MES e CARGO/DIA)
    sigla = campos.get("sugesp_sigla", "")
    if not sigla or sigla in {"MATR", "MES", "ANO"}:
        m = re.search(r"M[ÊE]S:\s*[A-ZÇÃÕ]+(.*?)(?:CARGO:|DIA)", norm)
        if m:
            trecho = m.group(1)
            tokens = re.findall(r"\b[A-Z]{2,4}\b", trecho)
            for tok in tokens:
                if tok not in {"MATR", "MES", "ANO"}:
                    sigla = tok
            if sigla:
                campos["sugesp_sigla"] = sigla

    repetidos_regex = {
        "sugesp_unidade": r"UNIDADE:",
        "sugesp_sub_unidade": r"SUB\s+UNIDADE:",
        "sugesp_setor_lotacao": r"SETOR DE LOTA[ÇC][ÃA]O:",
        "sugesp_servidor": r"SERVIDOR:",
        "sugesp_cargo": r"CARGO:",
        "sugesp_endereco": r"ENDERE[ÇC]O:",
        "sugesp_telefone": r"TELEFONE:",
        "sugesp_email": r"EMAIL:",
        "sugesp_cpf": r"CPF:",
    }
    for chave, marcador in repetidos_regex.items():
        val = campos.get(chave, "")
        if not val:
            continue
        up = val.upper()
        matches = list(re.finditer(marcador, up))
        if len(matches) > 1:
            campos[chave] = val[: matches[1].start()].strip()
        elif len(matches) == 1 and matches[0].start() > 0:
            campos[chave] = val[: matches[0].start()].strip()

    # remove prefixos duplicados que sobram no valor
    campos["sugesp_unidade"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_unidade", ""), r"UNIDADE:"), r"UNIDADE:"
    )
    # quando o PDF cola "2026 SUB" na mesma linha, corta antes do ano/sub
    unidade_val = campos.get("sugesp_unidade", "")
    if unidade_val:
        m = re.search(r"\b20\d{2}\b\s*SUB", unidade_val, flags=re.IGNORECASE)
        if m:
            unidade_val = unidade_val[: m.start()].strip()
        m = re.search(r"\bSUB\s+UNIDADE:", unidade_val, flags=re.IGNORECASE)
        if m:
            unidade_val = unidade_val[: m.start()].strip()
        campos["sugesp_unidade"] = unidade_val
    campos["sugesp_sub_unidade"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_sub_unidade", ""), r"SUB\s+UNIDADE:"), r"SUB\s+UNIDADE:"
    )
    campos["sugesp_setor_lotacao"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_setor_lotacao", ""), r"SETOR DE LOTA[ÇC][ÃA]O:"),
        r"SETOR DE LOTA[ÇC][ÃA]O:",
    )
    campos["sugesp_servidor"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_servidor", ""), r"SERVIDOR:"), r"SERVIDOR:"
    )
    campos["sugesp_cargo"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_cargo", ""), r"CARGO:"), r"CARGO:"
    )
    campos["sugesp_endereco"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_endereco", ""), r"ENDERE[ÇC]O:"), r"ENDERE[ÇC]O:"
    )
    campos["sugesp_telefone"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_telefone", ""), r"TELEFONE:"), r"TELEFONE:"
    )
    campos["sugesp_email"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_email", ""), r"EMAIL:"), r"EMAIL:"
    )
    campos["sugesp_cpf"] = corta_no_rotulo(
        remove_prefixo(campos.get("sugesp_cpf", ""), r"CPF:"), r"CPF:"
    )

    # ano para inteiro, se possivel
    try:
        campos["sugesp_ano"] = int(campos["sugesp_ano"])
    except Exception:
        campos["sugesp_ano"] = ""

    # saneia mes
    mes_upper = campos.get("sugesp_mes_label", "")
    if mes_upper in MESES:
        campos["sugesp_mes_label"] = mes_upper
    elif mes_upper:
        for nome in MESES.keys():
            if nome.startswith(mes_upper[:3]):
                campos["sugesp_mes_label"] = nome
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
