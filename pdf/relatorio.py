import calendar

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

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
    Desenha o cabeçalho oficial (logo) e o título do relatório,
    devolvendo a coordenada Y onde a tabela deve começar.
    """
    y_base = desenhar_cabecalho(c)

    largura_pagina, _ = A4
    x_centro = largura_pagina / 2

    c.setFont("Helvetica-Bold", 12)
    linha1 = f"RELATÓRIO DE ATIVIDADES EXECUTADAS PELO APENADO {reeducando}".upper()
    nome_mes = MESES_PT.get(mes, str(mes)).upper()
    linha2 = f"MÊS: {nome_mes}/{ano}"

    # Sobe a primeira linha e aumenta a folga para n?o grudar na linha de baixo
    y1 = y_base - 4 * mm   # primeira linha do t?tulo (mais afastada do cabe?alho)
    y2 = y1 - 4 * mm       # segunda linha (M?S: ...)

    c.drawCentredString(x_centro, y1, linha1)
    c.drawCentredString(x_centro, y2, linha2)

    # Espa?o entre o t?tulo e o cabe?alho da tabela (reduzido)
    y_tabela_top = y2 - 1 * mm
    return y_tabela_top


def desenhar_tabela_relatorio(
    c,
    mes,
    ano,
    municipio,
    atividade_base,
    feriados=None,
    y_top=None,
):
    """
    Desenha a tabela de atividades do mês.

    Se y_top for informado, usa exatamente essa posição como topo da tabela.
    Caso contrário, calcula um topo padrão com base no tamanho da página.
    """
    feriados = feriados or {}

    largura_pagina, _ = A4
    largura_tabela = 175 * mm
    largura_col_dia = 12 * mm
    largura_col_atividade = largura_tabela - largura_col_dia

    pad = 1.2 * mm
    fonte_header = ("Helvetica-Bold", 9)
    fonte_linha = ("Helvetica", 7.5)
    line_h = 8.0  # altura da linha em pontos

    # Caso não venha um y_top do cabeçalho, usa um valor padrão
    if y_top is None:
        y_top = c._pagesize[1] - 55 * mm

    # Centraliza a tabela na horizontal
    x = (largura_pagina - largura_tabela) / 2
    y = y_top

    def wrap_text(texto, max_width, font_name, font_size):
        """Quebra o texto em múltiplas linhas respeitando uma largura máxima."""
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
    cabecalho_alt = 5.5 * mm
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

    # Altura padr�o de linha baseada no texto de atividade normal
    texto_base = atividade_base.replace("{municipio}", municipio)
    linhas_base = wrap_text(
        texto_base,
        largura_col_atividade - pad * 2,
        fonte_linha[0],
        fonte_linha[1],
    )
    altura_base = len(linhas_base) * line_h + pad
    altura_minima = min(8 * mm, max(4.8 * mm, altura_base))

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

        altura_row = max(altura_minima, len(linhas) * line_h + pad)

        # Caixa da linha (borda externa)
        c.rect(x, y - altura_row, largura_tabela, altura_row, fill=0)
        # Linha vertical separando coluna do dia
        c.line(x + largura_col_dia, y - altura_row, x + largura_col_dia, y)

        # Coluna "Dia"
        c.setFont(*fonte_header)
        text_y = y - (altura_row / 2) + 0.5  # leve ajuste para o dia n�o encostar nas bordas
        c.drawCentredString(
            x + largura_col_dia / 2,
            text_y,
            f"{dia:02d}",
        )

        # Coluna "Atividade"
        c.setFont(*fonte_linha)
        bloco_altura = len(linhas) * line_h
        margem_superior = (altura_row - bloco_altura) / 2
        # Usa a mÇ®dia entre a posiÇõÇœ original e a centrada para nÇœo subir demais
        offset_antigo = pad + fonte_linha[1]
        offset_centrado = margem_superior + (line_h - fonte_linha[1]) / 2
        start_y = y - (offset_antigo + offset_centrado) / 2 - 0.5
        for i, linha in enumerate(linhas):
            c.drawString(
                x + largura_col_dia + pad,
                start_y - i * line_h,
                linha,
            )

        y -= altura_row

    # devolve a última posição Y, caso precise continuar o desenho depois
    return y