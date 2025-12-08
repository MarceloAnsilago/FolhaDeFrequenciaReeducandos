from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import calendar

from pdf.cabecalho import desenhar_cabecalho


MESES_PT = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
}


def gerar_relatorio_cabecalho(
    c,
    secretaria,
    ano,
    mes,
    reeducando,
    funcao,
    municipio,
    endereco,
    cep,
    telefone,
    data_preenchimento,
):
    """
    Desenha o cabeçalho oficial (logo) e o título do relatório.
    """
    # usa o mesmo cabeçalho oficial da folha de ponto
    y_base = desenhar_cabecalho(c)

    # título do relatório
    largura_pagina, _ = A4
    x_centro = largura_pagina / 2
    c.setFont("Helvetica-Bold", 12)

    linha1 = f"RELATÓRIO DE ATIVIDADES EXECUTADAS PELO APENADO {reeducando}".upper()
    nome_mes = MESES_PT.get(mes, str(mes)).upper()
    linha2 = f"MÊS: {nome_mes}/{ano}"

    y1 = y_base - 6 * mm
    y2 = y1 - 4 * mm

    c.drawCentredString(x_centro, y1, linha1)
    c.drawCentredString(x_centro, y2, linha2)

    return y2 - 2 * mm


def desenhar_tabela_relatorio(
    c,
    mes,
    ano,
    municipio,
    atividade_base,
    feriados=None,
    y_top=None,
):
    feriados = feriados or {}
    largura_pagina, _ = A4
    largura_tabela = 175 * mm
    largura_col_dia = 12 * mm
    largura_col_atividade = largura_tabela - largura_col_dia
    pad = 1 * mm
    fonte_header = ("Helvetica-Bold", 9)
    fonte_linha = ("Helvetica", 7.5)
    line_h = 8

    if y_top is None:
        y_top = c._pagesize[1] - 32 * mm

    x = (largura_pagina - largura_tabela) / 2
    y = y_top

    def wrap_text(texto, max_width, font_name, font_size):
        palavras = texto.split()
        linhas = []
        atual = ""
        for palavra in palavras:
            cand = palavra if not atual else f"{atual} {palavra}"
            if c.stringWidth(cand, font_name, font_size) <= max_width:
                atual = cand
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
        return linhas or [""]

    # Cabeçalho da tabela
    cabecalho_alt = 6 * mm
    c.setFont(*fonte_header)
    c.rect(x, y - cabecalho_alt, largura_tabela, cabecalho_alt, fill=0)
    c.line(x + largura_col_dia, y - cabecalho_alt, x + largura_col_dia, y)
    c.drawCentredString(
        x + largura_col_dia / 2,
        y - cabecalho_alt / 2 - 3,
        "Dia",
    )
    c.drawCentredString(
        x + largura_col_dia + (largura_col_atividade / 2),
        y - cabecalho_alt / 2 - 3,
        "Atividade",
    )
    y -= cabecalho_alt

    dias_no_mes = calendar.monthrange(ano, mes)[1]
    for dia in range(1, dias_no_mes + 1):
        dow = calendar.weekday(ano, mes, dia)
        if dow == 5:
            atividade = "SÁBADO"
        elif dow == 6:
            atividade = "DOMINGO"
        elif dia in feriados:
            atividade = feriados[dia].strip().upper()
        else:
            atividade = atividade_base.replace("{municipio}", municipio)

        linhas = wrap_text(
            atividade,
            largura_col_atividade - pad * 2,
            fonte_linha[0],
            fonte_linha[1],
        )
        altura_row = max(4.5 * mm, len(linhas) * line_h + pad)

        # caixa da linha
        c.rect(x, y - altura_row, largura_tabela, altura_row, fill=0)
        c.line(x + largura_col_dia, y - altura_row, x + largura_col_dia, y)

        # dia
        c.setFont(*fonte_header)
        c.drawCentredString(
            x + largura_col_dia / 2,
            y - (altura_row / 2) - 3,
            f"{dia:02d}",
        )

        # atividade
        c.setFont(*fonte_linha)
        start_y = y - pad - fonte_linha[1]
        for i, linha in enumerate(linhas):
            c.drawString(
                x + largura_col_dia + pad,
                start_y - i * line_h,
                linha,
            )

        y -= altura_row

    return y
