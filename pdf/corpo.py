from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import calendar

def desenhar_tabela(c, ano, mes):
    largura_pagina, altura_pagina = A4

    # ------------------------------
    # Configuração básica
    # ------------------------------
    MESES_PT = {
        1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
        5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
        9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO",
    }
    nome_mes = MESES_PT.get(mes, "")

    # Valores de exemplo (depois parametrizamos)
    nome_reeducando = "ADENIR BELING"
    funcao = "AUXILIAR DE SERVIÇOS GERAIS"
    data_inclusao = "11/11/2019"
    municipio = "SÃO MIGUEL DO GUAPORÉ"
    cpf = "753.210.922-49"
    banco = "01"
    agencia = "2292-6"
    conta = "23.061-8"

    # Posição da tabela logo abaixo do cabeçalho
    y_top = altura_pagina - 50 * mm   # ajuste fino

    # Largura da tabela: 14,8 cm (não estoura a margem)
    largura_tabela = 148 * mm
    altura_titulo  = 7 * mm           # 1ª linha
    altura_linha   = 6 * mm           # demais linhas

    # Centraliza a tabela na página
    x = (largura_pagina - largura_tabela) / 2

    # padding interno
    pad = 1.5 * mm

    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    # ------------------------------------------------------------
    # 1ª LINHA – REGISTRO INDIVIDUAL DE PONTO
    # ------------------------------------------------------------
    y1 = y_top - altura_titulo
    c.rect(x, y1, largura_tabela, altura_titulo, fill=0)

    c.setFont("Helvetica-Bold", 12)   # Arial Black 12 ~
    c.drawCentredString(
        x + largura_tabela / 2,
        y1 + (altura_titulo / 2) - 4,
        "REGISTRO INDIVIDUAL DE PONTO"
    )
    y_atual = y1

    # ------------------------------------------------------------
    # 2ª LINHA – SECRETARIA / ANO (linha corta antes do ANO)
    # ------------------------------------------------------------
    y2 = y_atual - altura_linha
    c.rect(x, y2, largura_tabela, altura_linha, fill=0)

    c.setFont("Helvetica-Bold", 11)
    texto_ano = f"ANO: {ano}"
    largura_texto_ano = c.stringWidth(texto_ano, "Helvetica-Bold", 11)

    x_ano = x + largura_tabela - pad - largura_texto_ano
    x_div1 = x_ano - pad
    c.line(x_div1, y2, x_div1, y2 + altura_linha)

    c.drawString(
        x + pad,
        y2 + (altura_linha / 2) - 3,
        "SECRETARIA: SECRETARIA DE ESTADO DA JUSTIÇA-SEJUS"
    )
    c.drawString(
        x_ano,
        y2 + (altura_linha / 2) - 3,
        texto_ano
    )
    y_atual = y2

    # ------------------------------------------------------------
    # 3ª LINHA – REEDUCANDO / MÊS
    # ------------------------------------------------------------
    y3 = y_atual - altura_linha
    c.rect(x, y3, largura_tabela, altura_linha, fill=0)

    largura_reeducando = largura_tabela * 0.70
    c.line(x + largura_reeducando, y3, x + largura_reeducando, y3 + altura_linha)

    c.drawString(
        x + pad,
        y3 + (altura_linha / 2) - 3,
        f"REEDUCANDO: {nome_reeducando}"
    )
    c.drawString(
        x + largura_reeducando + pad,
        y3 + (altura_linha / 2) - 3,
        f"MÊS: {nome_mes}"
    )
    y_atual = y3

    # ------------------------------------------------------------
    # 4ª LINHA – FUNÇÃO
    # ------------------------------------------------------------
    y4 = y_atual - altura_linha
    c.rect(x, y4, largura_tabela, altura_linha, fill=0)

    c.drawString(
        x + pad,
        y4 + (altura_linha / 2) - 3,
        f"FUNÇÃO: {funcao}"
    )
    y_atual = y4

    # ------------------------------------------------------------
    # 5ª LINHA – DATA DA INCLUSÃO / MUNICÍPIO
    # ------------------------------------------------------------
    y5 = y_atual - altura_linha
    c.rect(x, y5, largura_tabela, altura_linha, fill=0)

    c.setFont("Helvetica-Bold", 11)
    texto_data = f"DATA DA INCLUSÃO: {data_inclusao}"
    largura_texto_data = c.stringWidth(texto_data, "Helvetica-Bold", 11)

    x_fim_data = x + pad + largura_texto_data + 2
    c.line(x_fim_data, y5, x_fim_data, y5 + altura_linha)

    c.drawString(
        x + pad,
        y5 + (altura_linha / 2) - 3,
        texto_data
    )
    c.drawString(
        x_fim_data + pad,
        y5 + (altura_linha / 2) - 3,
        f"MUNICÍPIO: {municipio}"
    )
    y_atual = y5

    # ------------------------------------------------------------
    # 6ª LINHA – CPF / BCO / AG / CONTA
    # ------------------------------------------------------------
    y6 = y_atual - altura_linha
    c.rect(x, y6, largura_tabela, altura_linha, fill=0)

    larg_cpf = largura_tabela * 0.45
    larg_bco = largura_tabela * 0.13
    x_cpf_fim = x + larg_cpf
    x_bco_fim = x_cpf_fim + larg_bco

    c.line(x_cpf_fim, y6, x_cpf_fim, y6 + altura_linha)
    c.line(x_bco_fim, y6, x_bco_fim, y6 + altura_linha)

    c.drawString(
        x + pad,
        y6 + (altura_linha / 2) - 3,
        f"CPF: {cpf}"
    )
    c.drawString(
        x_cpf_fim + pad,
        y6 + (altura_linha / 2) - 3,
        f"BCO: {banco}"
    )
    c.drawString(
        x_bco_fim + pad,
        y6 + (altura_linha / 2) - 3,
        f"AG: {agencia} CONTA: {conta}"
    )
    y_atual = y6

    # ------------------------------------------------------------
    # 7ª LINHA – TIPO DE CONTA
    # ------------------------------------------------------------
    y7 = y_atual - altura_linha
    c.rect(x, y7, largura_tabela, altura_linha, fill=0)

    c.drawString(
        x + pad,
        y7 + (altura_linha / 2) - 3,
        "TIPO DE CONTA: (X) CORRENTE ( ) SALÁRIO ( ) POUPANÇA"
    )

    # ------------------------------------------------------------
    # Espaço entre a primeira tabela e a segunda tabela
    # ------------------------------------------------------------
    espaco_entre_tabelas = 2 * mm
    y_atual = y7 - espaco_entre_tabelas

    # ============================================================
    # CABEÇALHO DA SEGUNDA TABELA
    # DIA | HE | ENTRADA MANHA | HS | SAÍDA TARDE | (coluna OBS)
    # ============================================================
    altura_cabecalho_dias = 6 * mm

    # --------------------------------------------------------
    # larguras das colunas (ultima mais estreita, ganho vai
    # para ENTRADA MANHA e SAÍDA TARDE)
    # --------------------------------------------------------
    largura_col_dia = 12 * mm
    largura_col_he  = 10 * mm
    largura_col_hs2 = 10 * mm

    # largura fixa (mais estreita) para a coluna de observações
    largura_col_extra = 20 * mm

    # o que sobra será dividido entre ENTRADA MANHA e SAÍDA TARDE
    largura_restante = (
        largura_tabela
        - (largura_col_dia + largura_col_he + largura_col_hs2 + largura_col_extra)
    )
    largura_col_entra = largura_restante / 2.0
    largura_col_saida = largura_restante / 2.0

    x0 = x
    x1 = x0 + largura_col_dia
    x2 = x1 + largura_col_he
    x3 = x2 + largura_col_entra
    x4 = x3 + largura_col_hs2
    x5 = x4 + largura_col_saida
    x6 = x5 + largura_col_extra  # = x + largura_tabela

    # cabeçalho só até SAÍDA TARDE (NÃO pega a última coluna)
    y_header = y_atual - altura_cabecalho_dias
    c.rect(x0, y_header, x5 - x0, altura_cabecalho_dias, fill=0)

    for xv in (x1, x2, x3, x4, x5):
        c.line(xv, y_header, xv, y_header + altura_cabecalho_dias)

    c.setFont("Helvetica-Bold", 9)

    c.drawCentredString((x0 + x1) / 2,
                        y_header + (altura_cabecalho_dias / 2) - 3,
                        "DIA")
    c.drawCentredString((x1 + x2) / 2,
                        y_header + (altura_cabecalho_dias / 2) - 3,
                        "HE")
    c.drawCentredString((x2 + x3) / 2,
                        y_header + (altura_cabecalho_dias / 2) - 3,
                        "ENTRADA MANHA")
    c.drawCentredString((x3 + x4) / 2,
                        y_header + (altura_cabecalho_dias / 2) - 3,
                        "HS")
    c.drawCentredString((x4 + x5) / 2,
                        y_header + (altura_cabecalho_dias / 2) - 3,
                        "SAÍDA TARDE")
    # última coluna SEM cabeçalho

    y_atual = y_header

    # ============================================================
    # LINHAS DOS DIAS (última coluna SEM linhas internas)
    # ============================================================
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    altura_linha_dia = 6 * mm

    c.setFont("Helvetica-Bold", 9)

    # topo da tabela de dias fica logo abaixo do cabeçalho
    y_top_tabela = y_header
    y_ultima_linha = y_top_tabela

    for dia in range(1, dias_no_mes + 1):
        y_row = y_ultima_linha - altura_linha_dia

        # retângulo DA LINHA até SAÍDA TARDE (não entra na última coluna)
        c.rect(x0, y_row, x5 - x0, altura_linha_dia, fill=0)

        # divisões internas até SAÍDA TARDE
        for xv in (x1, x2, x3, x4, x5):
            c.line(xv, y_row, xv, y_row + altura_linha_dia)

        # DIA centralizado
        dia_str = f"{dia:02d}"
        c.drawCentredString(
            (x0 + x1) / 2,
            y_row + (altura_linha_dia / 2) - 3,
            dia_str
        )

        y_ultima_linha = y_row

    # ============================================================
    # COLUNA EXTRA ÚNICA (SEM LINHAS INTERNAS, SEM CABEÇALHO)
    # ============================================================
    # coluna extra deve fechar até a linha superior do cabeçalho
    y_top_coluna_extra = y_header + altura_cabecalho_dias
    altura_coluna_extra = y_top_coluna_extra - y_ultima_linha
    c.rect(x5, y_ultima_linha, largura_col_extra, altura_coluna_extra, fill=0)

    # Texto a ser repetido com espaço entre blocos
    bloco_texto = [
        "HORARIO",
        "CORRIDO",
        "DE",
        "ACORDO",
        "COM",
        "O DEC.",
        "N° 11619",
        "DE 7:30",
        "HE AS",
        "13:30 HS",
    ]

    c.setFont("Helvetica-Bold", 7)

    line_h = 9  # altura aproximada da linha em pontos
    linhas_por_bloco = len(bloco_texto) + 1  # +1 linha em branco
    altura_bloco = linhas_por_bloco * line_h

    # quantos blocos cabem na coluna
    num_blocos = max(1, int(altura_coluna_extra // altura_bloco))

    x_centro = x5 + largura_col_extra / 2
    y_texto = y_top_tabela - line_h  # começa um pouco abaixo do topo

    for _ in range(num_blocos):
        for linha in bloco_texto:
            if y_texto < y_ultima_linha + line_h:
                break
            c.drawCentredString(x_centro, y_texto, linha)
            y_texto -= line_h
        # linha em branco entre um bloco e outro
        y_texto -= line_h
        if y_texto < y_ultima_linha + line_h:
            break

    return y_ultima_linha
