from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

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

    # Por enquanto, valores fixos de exemplo
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

    largura_tabela = 156 * mm         # largura medida no Word
    altura_titulo  = 7 * mm           # 1ª linha
    altura_linha   = 6 * mm           # demais linhas

    x = (largura_pagina - largura_tabela) / 2

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

    # y_atual = base da última linha desenhada
    y_atual = y1

    # ------------------------------------------------------------
    # 2ª LINHA – SECRETARIA / ANO
    # ------------------------------------------------------------
    y2 = y_atual - altura_linha
    c.rect(x, y2, largura_tabela, altura_linha, fill=0)

    largura_secretaria = largura_tabela * 0.78
    c.line(x + largura_secretaria, y2, x + largura_secretaria, y2 + altura_linha)

    c.setFont("Helvetica-Bold", 11)   # Arial 11 ~
    c.drawString(
        x + 2 * mm,
        y2 + (altura_linha / 2) - 3,
        "SECRETARIA: SECRETARIA DE ESTADO DA JUSTIÇA-SEJUS"
    )

    texto_ano = f"ANO: {ano}"
    c.drawString(
        x + largura_secretaria + 2 * mm,
        y2 + (altura_linha / 2) - 3,
        texto_ano
    )

    y_atual = y2

    # ------------------------------------------------------------
    # 3ª LINHA – REEDUCANDO / MÊS
    # ------------------------------------------------------------
    y3 = y_atual - altura_linha
    c.rect(x, y3, largura_tabela, altura_linha, fill=0)

    largura_reeducando = largura_tabela * 0.78
    c.line(x + largura_reeducando, y3, x + largura_reeducando, y3 + altura_linha)

    c.drawString(
        x + 2 * mm,
        y3 + (altura_linha / 2) - 3,
        f"REEDUCANDO: {nome_reeducando}"
    )
    c.drawString(
        x + largura_reeducando + 2 * mm,
        y3 + (altura_linha / 2) - 3,
        f"MÊS: {nome_mes}"
    )

    y_atual = y3

    # ------------------------------------------------------------
    # 4ª LINHA – FUNÇÃO (linha inteira)
    # ------------------------------------------------------------
    y4 = y_atual - altura_linha
    c.rect(x, y4, largura_tabela, altura_linha, fill=0)

    c.drawString(
        x + 2 * mm,
        y4 + (altura_linha / 2) - 3,
        f"FUNÇÃO: {funcao}"
    )

    y_atual = y4

    # ------------------------------------------------------------
    # 5ª LINHA – DATA DA INCLUSÃO / MUNICÍPIO
    # ------------------------------------------------------------
    y5 = y_atual - altura_linha
    c.rect(x, y5, largura_tabela, altura_linha, fill=0)

    largura_data = largura_tabela * 0.5
    c.line(x + largura_data, y5, x + largura_data, y5 + altura_linha)

    c.drawString(
        x + 2 * mm,
        y5 + (altura_linha / 2) - 3,
        f"DATA DA INCLUSÃO: {data_inclusao}"
    )
    c.drawString(
        x + largura_data + 2 * mm,
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
        x + 2 * mm,
        y6 + (altura_linha / 2) - 3,
        f"CPF: {cpf}"
    )
    c.drawString(
        x_cpf_fim + 2 * mm,
        y6 + (altura_linha / 2) - 3,
        f"BCO: {banco}"
    )
    c.drawString(
        x_bco_fim + 2 * mm,
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
        x + 2 * mm,
        y7 + (altura_linha / 2) - 3,
        "TIPO DE CONTA: (X) CORRENTE ( ) SALÁRIO ( ) POUPANÇA"
    )

    y_atual = y7

    # Aqui embaixo começaremos o cabeçalho da tabela dos dias/horas
    return y_atual
