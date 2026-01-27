import calendar
from pathlib import Path
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader


LOGO_SUGESP = Path("assets/logo_sugesp.png")


def _wrap_text(c, texto, max_width, font_name, font_size):
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


def desenhar_cabecalho_sugesp(
    c,
    margem_topo=6 * mm,
    logo_altura=22 * mm,
):
    largura_pagina, altura_pagina = A4
    y_top = altura_pagina - margem_topo

    y_logo = y_top
    if LOGO_SUGESP.exists():
        logo = ImageReader(str(LOGO_SUGESP))
        w_px, h_px = logo.getSize()
        scale = (logo_altura / h_px) if h_px else 1
        draw_w = w_px * scale
        draw_h = h_px * scale
        x_logo = (largura_pagina - draw_w) / 2
        y_logo = y_top - draw_h
        c.drawImage(
            logo,
            x_logo,
            y_logo,
            draw_w,
            draw_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    y_texto = y_logo - 3 * mm
    x_centro = largura_pagina / 2

    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_centro, y_texto, "GOVERNO DO ESTADO DE RONDONIA")
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(
        x_centro,
        y_texto - 4 * mm,
        "SUPERINTENDENCIA DE GESTAO DOS GASTOS PUBLICOS ADMINISTRATIVOS - SUGESP",
    )

    return y_texto - 8 * mm


def desenhar_tabela_sugesp(
    c,
    *,
    ano,
    mes,
    mes_label,
    unidade,
    sub_unidade,
    setor_lotacao,
    servidor,
    matricula,
    sigla,
    cargo,
    he,
    hs,
    feriados,
    endereco,
    cep,
    telefone,
    email,
    cpf,
    data_preenchimento,
    y_top,
):
    largura_pagina, _ = A4
    tabela_largura = 180 * mm
    x = (largura_pagina - tabela_largura) / 2

    # colunas do modelo (dxa): 568, 624, 3770, 709, 1976, 1851, 709
    dxa_cols = [568, 624, 3770, 709, 1976, 1851, 709]
    scale = tabela_largura / sum(dxa_cols)
    cols = [w * scale for w in dxa_cols]
    x0 = x
    x1 = x0 + cols[0]
    x2 = x1 + cols[1]
    x3 = x2 + cols[2]
    x4 = x3 + cols[3]
    x5 = x4 + cols[4]
    x6 = x5 + cols[5]
    x7 = x6 + cols[6]

    altura_titulo = 6 * mm
    altura_linha = 5 * mm

    c.setLineWidth(0.7)
    c.setFont("Helvetica-Bold", 10)

    y = y_top

    # linha 1: titulo e ANO
    y1 = y - altura_titulo
    c.rect(x0, y1, x5 - x0, altura_titulo, fill=0)
    c.rect(x5, y1, x7 - x5, altura_titulo, fill=0)
    c.drawCentredString(x0 + (x5 - x0) / 2, y1 + 2 * mm, "REGISTRO INDIVIDUAL DE PONTO")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x5 + 2 * mm, y1 + 1.5 * mm, "ANO:")
    y = y1

    # linha 2: unidade e ano (altura dinamica para 2 linhas)
    unidade_texto = f"UNIDADE: {unidade}"
    linhas_unidade = _wrap_text(c, unidade_texto, (x5 - x0) - 4 * mm, "Helvetica-Bold", 9)
    altura_unidade = max(altura_linha, (len(linhas_unidade[:2]) * 3.2 * mm) + 1.6 * mm)
    y2 = y - altura_unidade
    c.rect(x0, y2, x5 - x0, altura_unidade, fill=0)
    c.rect(x5, y2, x7 - x5, altura_unidade, fill=0)
    y_unidade = y2 + altura_unidade - 3.4 * mm
    c.setFont("Helvetica-Bold", 9)
    for linha in linhas_unidade[:2]:
        c.drawString(x0 + 2 * mm, y_unidade, linha)
        y_unidade -= 3.4 * mm
    c.drawCentredString(x5 + (x7 - x5) / 2, y2 + (altura_unidade / 2) - 2, str(ano))
    y = y2

    # linhas 3 a 5: sub unidade / setor / servidor (mes a direita com merge)
    y3 = y - altura_linha
    c.rect(x0, y3, x5 - x0, altura_linha, fill=0)
    c.drawString(x0 + 2 * mm, y3 + 1.5 * mm, f"SUB UNIDADE: {sub_unidade}")

    # coluna direita (mes) mesclada por 3 linhas
    c.rect(x5, y3 - 2 * altura_linha, x7 - x5, 3 * altura_linha, fill=0)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x5 + (x7 - x5) / 2, y3 - altura_linha + 1.5 * mm, f"MES: {mes_label}")

    y4 = y3 - altura_linha
    c.rect(x0, y4, x5 - x0, altura_linha, fill=0)
    c.drawString(x0 + 2 * mm, y4 + 1.5 * mm, f"SETOR DE LOTACAO: {setor_lotacao}")

    y5 = y4 - altura_linha
    c.rect(x0, y5, x5 - x0, altura_linha, fill=0)
    c.drawString(x0 + 2 * mm, y5 + 1.5 * mm, f"SERVIDOR: {servidor}")
    y = y5

    # linha 6: matricula e sigla
    y6 = y - altura_linha
    c.rect(x0, y6, x5 - x0, altura_linha, fill=0)
    c.rect(x5, y6, x7 - x5, altura_linha, fill=0)
    c.drawString(x0 + 2 * mm, y6 + 1.5 * mm, f"MATRICULA: {matricula}")
    if sigla:
        c.drawCentredString(x5 + (x7 - x5) / 2, y6 + 1.5 * mm, sigla)
    y = y6

    # linha 7: cargo
    y7 = y - altura_linha
    c.rect(x0, y7, x5 - x0, altura_linha, fill=0)
    c.rect(x5, y7, x7 - x5, altura_linha, fill=0)
    c.drawString(x0 + 2 * mm, y7 + 1.5 * mm, f"CARGO: {cargo}")
    y = y7

    # cabecalho da tabela de dias
    altura_header_dias = 5 * mm
    y_header = y - altura_header_dias
    c.rect(x0, y_header, x6 - x0, altura_header_dias, fill=0)
    for xv in (x1, x2, x3, x4):
        c.line(xv, y_header, xv, y_header + altura_header_dias)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString((x0 + x1) / 2, y_header + 1.5 * mm, "DIA")
    c.drawCentredString((x1 + x2) / 2, y_header + 1.5 * mm, "Hr")
    c.drawCentredString((x2 + x3) / 2, y_header + 1.5 * mm, "ENTRADA")
    c.drawCentredString((x3 + x4) / 2, y_header + 1.5 * mm, "Hr")
    c.drawCentredString((x4 + x6) / 2, y_header + 1.5 * mm, "SAIDA")

    # coluna decreto (unica)
    total_dias = 31
    altura_linha_dia = 5 * mm
    y_dias_bottom = y_header - total_dias * altura_linha_dia
    c.rect(x6, y_dias_bottom, x7 - x6, y_header + altura_header_dias - y_dias_bottom, fill=0)

    decreto = (
        "DECRETO N 14828, DE 23 DE DEZEMBRO DE 2009. "
        "DOE N 1395, DE 22 DE DEZEMBRO DE 2009."
    )
    c.saveState()
    c.translate((x6 + x7) / 2, (y_header + altura_header_dias + y_dias_bottom) / 2)
    c.rotate(90)
    max_width = (y_header + altura_header_dias - y_dias_bottom) - 4 * mm
    linhas = _wrap_text(c, decreto, max_width, "Helvetica-Bold", 7)
    total_h = len(linhas) * 8
    y_text = total_h / 2 - 7
    c.setFont("Helvetica-Bold", 7)
    for linha in linhas:
        c.drawCentredString(0, y_text, linha)
        y_text -= 8
    c.restoreState()

    dias_no_mes = calendar.monthrange(int(ano), int(mes))[1]
    feriados = feriados or {}

    for dia in range(1, total_dias + 1):
        y_row = y_header - dia * altura_linha_dia
        is_valido = dia <= dias_no_mes
        is_feriado = dia in feriados
        dow = calendar.weekday(int(ano), int(mes), dia) if is_valido else None
        is_sabado = dow == 5
        is_domingo = dow == 6

        if is_sabado or is_domingo:
            c.setFillColorRGB(0.85, 0.85, 0.85)
            c.rect(x0, y_row, x6 - x0, altura_linha_dia, fill=1)
            c.setFillColorRGB(0, 0, 0)
        else:
            c.rect(x0, y_row, x6 - x0, altura_linha_dia, fill=0)

        for xv in (x1, x2, x3, x4):
            c.line(xv, y_row, xv, y_row + altura_linha_dia)

        c.setFont("Helvetica-Bold", 8)
        dia_str = f"{dia:02d}" if is_valido else ""
        c.drawCentredString((x0 + x1) / 2, y_row + 1.5 * mm, dia_str)

        texto_hr1 = ""
        texto_hr2 = ""
        texto_entrada = ""
        texto_saida = ""

        if is_valido:
            if is_sabado:
                texto_hr1 = "---"
                texto_hr2 = "---"
                texto_entrada = "SABADO"
                texto_saida = "SABADO"
            elif is_domingo:
                texto_hr1 = "---"
                texto_hr2 = "---"
                texto_entrada = "DOMINGO"
                texto_saida = "DOMINGO"
            elif is_feriado:
                texto_hr1 = "---"
                texto_hr2 = "---"
                texto_entrada = feriados[dia].upper()
                texto_saida = feriados[dia].upper()
            else:
                texto_hr1 = he or ""
                texto_hr2 = hs or ""

        c.setFont("Helvetica-Bold", 8)
        if texto_hr1:
            c.drawCentredString((x1 + x2) / 2, y_row + 1.5 * mm, texto_hr1)
        if texto_hr2:
            c.drawCentredString((x3 + x4) / 2, y_row + 1.5 * mm, texto_hr2)

        if texto_entrada:
            linhas = _wrap_text(c, texto_entrada, (x3 - x2) - 2 * mm, "Helvetica-Bold", 7)
            y_text = y_row + 2.5 * mm + (len(linhas) - 1) * 3
            for linha in linhas:
                c.drawCentredString((x2 + x3) / 2, y_text, linha)
                y_text -= 3
        if texto_saida:
            linhas = _wrap_text(c, texto_saida, (x6 - x4) - 2 * mm, "Helvetica-Bold", 7)
            y_text = y_row + 2.5 * mm + (len(linhas) - 1) * 3
            for linha in linhas:
                c.drawCentredString((x4 + x6) / 2, y_text, linha)
                y_text -= 3

    # rodape
    y_footer_top = y_dias_bottom - 2 * mm
    footer_cols = [3119, 567, 1737, 1807, 2977]
    f_scale = tabela_largura / sum(footer_cols)
    fw = [w * f_scale for w in footer_cols]
    f0 = x0
    f1 = f0 + fw[0]
    f2 = f1 + fw[1]
    f3 = f2 + fw[2]
    f4 = f3 + fw[3]
    f5 = f4 + fw[4]

    row1_h = 6 * mm
    row2_h = 6 * mm
    row3_h = 6 * mm
    row4_h = 10 * mm

    y_r1 = y_footer_top - row1_h
    c.rect(x0, y_r1, tabela_largura, row1_h, fill=0)
    c.setFont("Helvetica", 8)
    c.drawString(x0 + 2 * mm, y_r1 + 1.5 * mm, f"ENDERECO: {endereco} CEP: {cep}")

    y_r2 = y_r1 - row2_h
    c.rect(x0, y_r2, tabela_largura, row2_h, fill=0)
    # TELEFONE | EMAIL | CPF
    b1 = f0 + fw[0] + fw[1]
    b2 = f0 + fw[0] + fw[1] + fw[2] + fw[3]
    c.line(b1, y_r2, b1, y_r2 + row2_h)
    c.line(b2, y_r2, b2, y_r2 + row2_h)
    c.drawString(x0 + 2 * mm, y_r2 + 1.5 * mm, f"TELEFONE: {telefone}")
    c.drawString(b1 + 2 * mm, y_r2 + 1.5 * mm, f"EMAIL: {email}")
    c.drawString(b2 + 2 * mm, y_r2 + 1.5 * mm, f"CPF: {cpf}")

    y_r3 = y_r2 - row3_h
    c.rect(x0, y_r3, tabela_largura, row3_h, fill=0)
    # DATA | devolucao
    c.line(f1, y_r3, f1, y_r3 + row3_h)
    c.drawString(x0 + 2 * mm, y_r3 + 1.5 * mm, f"DATA: {data_preenchimento}")
    c.setFont("Helvetica", 7)
    c.drawString(f1 + 2 * mm, y_r3 + 1.5 * mm, "Devolver esta folha ate o 1o dia util do mes seguinte na SUGESP-CGP")

    y_r4 = y_r3 - row4_h
    c.setFont("Helvetica", 8)
    c.rect(x0, y_r4, tabela_largura, row4_h, fill=0)
    split_sig = f0 + fw[0] + fw[1] + fw[2]
    c.line(split_sig, y_r4, split_sig, y_r4 + row4_h)
    c.drawCentredString((x0 + split_sig) / 2, y_r4 + row4_h - 4 * mm, "Assinatura do servidor")
    c.drawCentredString((split_sig + x0 + tabela_largura) / 2, y_r4 + row4_h - 4 * mm, "Visto do Chefe")

    # espaco para assinaturas
    y_r5 = y_r4 - row4_h
    c.rect(x0, y_r5, tabela_largura, row4_h, fill=0)
    c.line(split_sig, y_r5, split_sig, y_r5 + row4_h)

    # texto legal
    legal = (
        "COM AMPARO LEGAL NA INSTRUCAO NORMATIVA N 001/SEAD, 29/03/2006, "
        "PUBLICADA NO DOE N 0487, DE 03/04/2006. E OBRIGATORIO NO REGISTRO DE PONTO: "
        "NOME COMPLETO; NUMERO DA MATRICULA; CARGO; ORGAO DE LOTACAO E SUBLOTACAO; "
        "ENDERECO COMPLETO; ASSINATURA DO SERVIDOR DEVERA SER POR EXTENSO, COM CANETA "
        "ESFEROGRAFICA PRETA OU AZUL, SEM RASURAS, DEVIDAMENTE CERTIFICADO PELO CHEFE "
        "IMEDIATO, ATRAVES DE ASSINATURA E RESPECTIVO CARIMBO DE IDENTIFICACAO (DEC.5442/91)"
    )
    max_width = tabela_largura - 4 * mm
    c.setFont("Helvetica-Bold", 6.5)
    linhas = _wrap_text(c, legal, max_width, "Helvetica-Bold", 6.5)
    line_h = 2.6 * mm
    legal_h = max(10 * mm, (len(linhas) * line_h) + 3 * mm)
    y_legal = y_r5 - legal_h
    c.setFillColorRGB(0.75, 0.75, 0.75)
    c.rect(x0, y_legal, tabela_largura, legal_h, fill=1)
    c.setFillColorRGB(0, 0, 0)
    y_text = y_legal + legal_h - 3 * mm
    for linha in linhas:
        c.drawString(x0 + 2 * mm, y_text, linha)
        y_text -= line_h

    return y_legal


def gerar_pdf_sugesp(data):
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle("Folha de ponto SUGESP")

    y_top = desenhar_cabecalho_sugesp(c)
    desenhar_tabela_sugesp(c, y_top=y_top, **data)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
