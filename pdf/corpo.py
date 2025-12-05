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

    # Valores de exemplo (depois podemos parametrizar)
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

    # padding interno (margem esquerda/direita dentro das células)
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
    # 2ª LINHA – SECRETARIA / ANO  (divisão exata antes do ANO)
    # ------------------------------------------------------------
    y2 = y_atual - altura_linha
    c.rect(x, y2, largura_tabela, altura_linha, fill=0)

    c.setFont("Helvetica-Bold", 11)

    # Texto ANO
    texto_ano = f"ANO: {ano}"
    largura_texto_ano = c.stringWidth(texto_ano, "Helvetica-Bold", 11)

    # posição do ANO alinhado à direita
    x_ano = x + largura_tabela - pad - largura_texto_ano

    # 🚨 NOVO: linha vertical exatamente antes do texto ANO
    x_div1 = x_ano - pad
    c.line(x_div1, y2, x_div1, y2 + altura_linha)

    # texto SECRETARIA (vai até onde der)
    c.drawString(
        x + pad,
        y2 + (altura_linha / 2) - 3,
        "SECRETARIA: SECRETARIA DE ESTADO DA JUSTIÇA-SEJUS"
    )

    # escreve ANO
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
    # 4ª LINHA – FUNÇÃO (linha inteira)
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
    #  (linha vai até o fim do último dígito do ano)
    # ------------------------------------------------------------
    y5 = y_atual - altura_linha
    c.rect(x, y5, largura_tabela, altura_linha, fill=0)

    c.setFont("Helvetica-Bold", 11)

    texto_data = f"DATA DA INCLUSÃO: {data_inclusao}"
    largura_texto_data = c.stringWidth(texto_data, "Helvetica-Bold", 11)

    # posição exata onde termina o texto da data + folguinha
    x_fim_data = x + pad + largura_texto_data + 2  # 2 px de respiro

    # linha vertical exatamente no fim da data
    c.line(x_fim_data, y5, x_fim_data, y5 + altura_linha)

    # escreve a data
    c.drawString(
        x + pad,
        y5 + (altura_linha / 2) - 3,
        texto_data
    )

    # escreve o município logo após a linha
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

    y_atual = y7

    # Aqui embaixo começaremos o cabeçalho da tabela de dias/horas depois
    return y_atual
