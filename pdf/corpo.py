from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import calendar
from textwrap import wrap

def desenhar_tabela(
    c,
    ano,
    mes,
    he=None,
    hs=None,
    y_top=None,
    feriados=None,
    endereco=None,
    cep=None,
    telefone=None,
    data_preenchimento=None,
    secretaria=None,
    reeducando=None,
    funcao=None,
    data_inclusao=None,
    municipio=None,
    cpf=None,
    banco=None,
    agencia=None,
    conta=None,
    tipo_conta=None,
):
    largura_pagina, altura_pagina = A4
    feriados = feriados or {}

    # ------------------------------
    # Configuração básica
    # ------------------------------
    MESES_PT = {
        1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
        5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
        9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO",
    }
    nome_mes = MESES_PT.get(mes, "")

    # Valores padrão (podem ser sobrescritos pelos parâmetros)
    secretaria = secretaria or ""
    nome_reeducando = reeducando or ""
    funcao = funcao or ""
    data_inclusao = data_inclusao or ""
    endereco = endereco or ""
    cep = cep or ""
    telefone = telefone or ""
    municipio = municipio or ""
    cpf = cpf or ""
    banco = banco or ""
    agencia = agencia or ""
    conta = conta or ""
    tipo_conta = tipo_conta or ""
    data_preenchimento = data_preenchimento or ""

    # Posição da tabela: usa valor fornecido pelo cabeçalho ou cai no padrão
    if y_top is None:
        y_top = altura_pagina - 34 * mm   # margem padrão caso não venha coordenada do cabeçalho

    # Largura da tabela: 14,8 cm (não estoura a margem)
    largura_tabela = 148 * mm
    altura_titulo  = 6 * mm           # 1ª linha
    altura_linha   = 5 * mm           # demais linhas

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
        f"SECRETARIA: {secretaria}"
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
        f"TIPO DE CONTA: {tipo_conta}"
    )

    # ------------------------------------------------------------
    # Espaço entre a primeira tabela e a segunda tabela
    # ------------------------------------------------------------
    espaco_entre_tabelas = 1 * mm
    y_atual = y7 - espaco_entre_tabelas

    # ============================================================
    # CABEÇALHO DA SEGUNDA TABELA
    # DIA | HE | ENTRADA MANHA | HS | SAÍDA TARDE | (coluna OBS)
    # ============================================================
    altura_cabecalho_dias = 5 * mm

    # --------------------------------------------------------
    # larguras das colunas (ultima mais estreita, ganho vai
    # para ENTRADA MANHA e SAÍDA TARDE)
    # --------------------------------------------------------
    largura_col_dia = 12 * mm
    largura_col_he  = 10 * mm
    largura_col_hs2 = 10 * mm

    # largura fixa (mais estreita) para a coluna de observações
    largura_col_extra = 14 * mm  # coluna de observações mais estreita

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

    def wrap_text(texto, max_width, font_name, font_size):
        """Quebra o texto para caber na largura disponível."""
        palavras = texto.split()
        linhas = []
        atual = ""
        for palavra in palavras:
            candidato = palavra if not atual else f"{atual} {palavra}"
            if c.stringWidth(candidato, font_name, font_size) <= max_width:
                atual = candidato
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
        return linhas or [""]

    def draw_wrapped_centered(texto, x_centro, y_row, largura_coluna, font_name, font_size):
        max_width = max(largura_coluna - (pad * 2), 1)
        linhas = wrap_text(texto, max_width, font_name, font_size)
        line_height = font_size + 2
        base_centro = y_row + (altura_linha_dia / 2) - 3
        start_y = base_centro + ((len(linhas) - 1) * line_height) / 2
        for idx, linha in enumerate(linhas):
            y_texto = start_y - idx * line_height
            c.setFont(font_name, font_size)
            c.drawCentredString(x_centro, y_texto, linha)

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
    total_linhas = 31
    altura_linha_dia = 5 * mm

    c.setFont("Helvetica-Bold", 9)

    # topo da tabela de dias fica logo abaixo do cabeçalho
    y_top_tabela = y_header
    y_ultima_linha = y_top_tabela

    for dia in range(1, total_linhas + 1):
        y_row = y_ultima_linha - altura_linha_dia

        # retângulo DA LINHA até SAÍDA TARDE (não entra na última coluna)
        c.rect(x0, y_row, x5 - x0, altura_linha_dia, fill=0)

        # divisões internas até SAÍDA TARDE
        for xv in (x1, x2, x3, x4, x5):
            c.line(xv, y_row, xv, y_row + altura_linha_dia)

        # DIA centralizado + marcação de fins de semana, feriados e horários
        if dia <= dias_no_mes:
            dia_str = f"{dia:02d}"
            dow = calendar.weekday(ano, mes, dia)
            feriado_desc = feriados.get(dia)
            entrada_texto = ""
            saida_texto = ""

            if dow == 5:  # sábado
                he_text = "S"
                hs_text = "S"
                entrada_texto = "SABADO"
                saida_texto = "SABADO"
            elif dow == 6:  # domingo
                he_text = "D"
                hs_text = "D"
                entrada_texto = "DOMINGO"
                saida_texto = "DOMINGO"
            else:
                he_text = he or ""
                hs_text = hs or ""

            if feriado_desc:
                he_text = "F"
                hs_text = "F"
                texto_feriado = feriado_desc.strip().upper()
                entrada_texto = texto_feriado
                saida_texto = texto_feriado
        else:
            dia_str = "---"
            he_text = ""
            hs_text = ""
            entrada_texto = ""
            saida_texto = ""

        c.drawCentredString(
            (x0 + x1) / 2,
            y_row + (altura_linha_dia / 2) - 3,
            dia_str
        )

        if he_text:
            c.drawCentredString(
                (x1 + x2) / 2,
                y_row + (altura_linha_dia / 2) - 3,
                he_text
            )
        if entrada_texto:
            fonte = "Helvetica-Bold"
            tamanho = 7 if feriados.get(dia) else 9
            draw_wrapped_centered(
                entrada_texto,
                (x2 + x3) / 2,
                y_row,
                largura_col_entra,
                fonte,
                tamanho,
            )
        if hs_text:
            c.drawCentredString(
                (x3 + x4) / 2,
                y_row + (altura_linha_dia / 2) - 3,
                hs_text
            )
        if saida_texto:
            fonte = "Helvetica-Bold"
            tamanho = 7 if feriados.get(dia) else 9
            draw_wrapped_centered(
                saida_texto,
                (x4 + x5) / 2,
                y_row,
                largura_col_saida,
                fonte,
                tamanho,
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

    # ------------------------------------------------------------
    # RODAPÉ COM ENDEREÇO / CONTATOS / ASSINATURAS
    # ------------------------------------------------------------
    altura_footer = 5 * mm

    # linha 1: endereço (largura total)
    y_footer1 = y_ultima_linha - altura_footer
    c.rect(x, y_footer1, largura_tabela, altura_footer, fill=0)
    c.drawString(
        x + pad,
        y_footer1 + (altura_footer / 2) - 3,
        f"ENDEREÇO: {endereco}"
    )

    # linha 2: CEP | TELEFONE | DATA
    y_footer2 = y_footer1 - altura_footer
    c.rect(x, y_footer2, largura_tabela, altura_footer, fill=0)
    col1 = largura_tabela * 0.35
    col2 = largura_tabela * 0.30
    x_col1 = x + col1
    x_col2 = x_col1 + col2
    c.line(x_col1, y_footer2, x_col1, y_footer2 + altura_footer)
    c.line(x_col2, y_footer2, x_col2, y_footer2 + altura_footer)
    c.drawString(x + pad, y_footer2 + (altura_footer / 2) - 3, f"CEP: {cep}")
    c.drawString(x_col1 + pad, y_footer2 + (altura_footer / 2) - 3, f"TELEFONE: {telefone}")
    c.drawString(x_col2 + pad, y_footer2 + (altura_footer / 2) - 3, f"DATA: {data_preenchimento}")

    # linha 3: assinaturas
    y_footer3 = y_footer2 - altura_footer
    c.rect(x, y_footer3, largura_tabela, altura_footer, fill=0)
    x_meio = x + (largura_tabela / 2)
    c.line(x_meio, y_footer3, x_meio, y_footer3 + altura_footer)
    c.drawCentredString(
        x + (largura_tabela / 4),
        y_footer3 + (altura_footer / 2) - 3,
        "ASSINATURA DO REEDUCANDO"
    )
    c.drawCentredString(
        x + (3 * largura_tabela / 4),
        y_footer3 + (altura_footer / 2) - 3,
        "VISTO DO CHEFE"
    )

    # linha extra para o campo de assinatura de ambos
    altura_campo_assinatura = 8 * mm
    y_footer4 = y_footer3 - altura_campo_assinatura
    c.rect(x, y_footer4, largura_tabela, altura_campo_assinatura, fill=0)
    c.line(x_meio, y_footer4, x_meio, y_footer4 + altura_campo_assinatura)

    y_ultima_linha = y_footer4

    return y_ultima_linha
