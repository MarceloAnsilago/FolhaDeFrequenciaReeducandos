from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader


LOGO_IDARON = Path("assets/logo_idaron1548x1787px-1.png")


def _draw_header(
    c,
    regional,
    unidade,
    atividade,
    atividade_palestra,
    atividade_reuniao,
    atividade_curso,
    atividade_encontro,
    outro_qual,
    tema,
    data,
    horario_inicio,
    horario_fim,
    local,
    municipio,
    tipo_publico,
    tipo_publico_outra,
    qual,
):
    largura_pagina, altura_pagina = A4
    x = 15 * mm
    largura_tabela = largura_pagina - 2 * x

    # logo e título em topo
    y_top = altura_pagina - 14 * mm
    h_topo = 8 * mm
    h_titulo = h_topo
    h_regional = h_topo
    h_atividade = h_topo
    logo_h = h_titulo + h_regional + h_atividade
    area_campos_x = x + 42 * mm
    area_campos_w = largura_tabela - 42 * mm
    bloco_top_y = y_top - 18 * mm
    logo_box_x = x
    logo_box_y = bloco_top_y - logo_h
    logo_box_w = area_campos_x - logo_box_x
    logo_base_y = logo_box_y + 2 * mm
    if LOGO_IDARON.exists():
        logo = ImageReader(str(LOGO_IDARON))
        w_px, h_px = logo.getSize()
        scale = logo_h / h_px
        logo_w = w_px * scale
        c.rect(logo_box_x, logo_box_y, logo_box_w, logo_h, fill=0)
        c.drawImage(
            logo,
            x + 4 * mm,
            logo_base_y,
            logo_w,
            logo_h,
            preserveAspectRatio=True,
            mask='auto',
        )
    c.rect(area_campos_x, bloco_top_y - h_titulo, area_campos_w, h_titulo, fill=0)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(
        area_campos_x + area_campos_w / 2,
        bloco_top_y - h_titulo + 2.6 * mm,
        'LISTA DE PRESENÇA',
    )
    y = bloco_top_y - h_titulo
    c.setLineWidth(0.8)

    # REGIONAL
    h = h_regional
    divisor_campo_x = area_campos_x + 23 * mm
    c.rect(area_campos_x, y - h, area_campos_w, h, fill=0)
    c.line(divisor_campo_x, y - h, divisor_campo_x, y)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(area_campos_x + 2 * mm, y - h + 2 * mm, 'REGIONAL:')
    c.setFont('Helvetica', 9)
    c.drawString(divisor_campo_x + 2 * mm, y - h + 2 * mm, str(regional))

    y -= h
    # UNIDADE
    h = h_atividade
    c.rect(area_campos_x, y - h, area_campos_w, h, fill=0)
    c.line(divisor_campo_x, y - h, divisor_campo_x, y)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(area_campos_x + 2 * mm, y - h + 2 * mm, 'UNIDADE:')
    c.setFont('Helvetica', 9)
    c.drawString(divisor_campo_x + 2 * mm, y - h + 2 * mm, str(unidade))

    y -= h
    # ATIVIDADE / OUTRO-QUAL?
    h = 8 * mm
    altura_bloco_atividade = h * 2
    c.rect(x, y - altura_bloco_atividade, logo_box_w, altura_bloco_atividade, fill=0)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(x + 2 * mm, y - h - 2 * mm, 'ATIVIDADE:')

    c.rect(area_campos_x, y - h, area_campos_w, h, fill=0)
    col1 = area_campos_x + area_campos_w / 4
    col2 = area_campos_x + area_campos_w / 2
    col3 = area_campos_x + (area_campos_w * 3 / 4)
    c.line(col1, y - h, col1, y)
    c.line(col2, y - h, col2, y)
    c.line(col3, y - h, col3, y)

    c.setFont('Helvetica', 7)
    checkbox_size = 2.6 * mm
    checkbox_y = y - h + 2.5 * mm
    campos_atividade = [
        (area_campos_x, col1, 'PALESTRA', atividade_palestra),
        (col1, col2, 'REUNIÃO', atividade_reuniao),
        (col2, col3, 'CURSO/ TREINAMENTO', atividade_curso),
        (col3, area_campos_x + area_campos_w, 'ENCONTRO', atividade_encontro),
    ]
    for x0, x1, label, marcado in campos_atividade:
        checkbox_x = x0 + 2 * mm
        c.rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size, fill=0)
        if str(marcado).strip():
            c.setFont('Helvetica-Bold', 7)
            c.drawCentredString(
                checkbox_x + checkbox_size / 2,
                checkbox_y + 0.15 * mm,
                'X',
            )
            c.setFont('Helvetica', 7)
        c.drawRightString(x1 - 1.5 * mm, y - h + 2.5 * mm, label)

    y -= h
    c.rect(area_campos_x, y - h, area_campos_w, h, fill=0)
    c.line(col1, y - h, col1, y)
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(col1 - 2 * mm, y - h + 2 * mm, 'OUTRO-QUAL?')
    c.setFont('Helvetica', 9)
    c.drawString(col1 + 2 * mm, y - h + 2 * mm, str(outro_qual))

    y -= h + 1 * mm
    # TEMA
    h = 8 * mm
    c.rect(x, y - h, largura_tabela, h, fill=0)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(x + 2 * mm, y - h + 2 * mm, 'TEMA:')
    c.setFont('Helvetica', 9)
    c.drawString(x + 20 * mm, y - h + 2 * mm, str(tema))

    y -= h + 1 * mm
    # DATA/HORÁRIO INÍCIO/HORÁRIO FIM
    h = 8 * mm
    c.rect(x, y - h, largura_tabela, h, fill=0)
    c.line(x + 42 * mm, y - h, x + 42 * mm, y)
    c.line(x + 109 * mm, y - h, x + 109 * mm, y)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(x + 2 * mm, y - h + 2 * mm, 'DATA:')
    c.setFont('Helvetica', 9)
    c.drawString(x + 44 * mm, y - h + 2 * mm, 'HORÁRIO INÍCIO')
    c.drawString(x + 111 * mm, y - h + 2 * mm, 'HORÁRIO FIM')
    c.drawString(x + 2 * mm, y - h - 4 * mm, str(data))
    c.drawString(x + 44 * mm, y - h - 4 * mm, str(horario_inicio))
    c.drawString(x + 111 * mm, y - h - 4 * mm, str(horario_fim))

    y -= h + 1 * mm
    # LOCAL / MUNICÍPIO
    h = 8 * mm
    c.rect(x, y - h, largura_tabela, h, fill=0)
    municipio_x = x + 92 * mm
    municipio_label_end_x = x + 109 * mm
    c.line(municipio_x, y - h, municipio_x, y)
    c.line(municipio_label_end_x, y - h, municipio_label_end_x, y)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(x + 2 * mm, y - h + 2 * mm, 'LOCAL:')
    c.setFont('Helvetica-Bold', 8)
    c.drawString(municipio_x + 0.8 * mm, y - h + 2.2 * mm, 'MUNICÍPIO:')
    c.setFont('Helvetica', 9)
    c.drawString(x + 2 * mm, y - h - 4 * mm, str(local))
    c.drawString(municipio_label_end_x + 2 * mm, y - h - 4 * mm, str(municipio))

    y -= h + 1 * mm
    # TIPO DE PÚBLICO
    h = 12 * mm
    c.rect(x, y - h, largura_tabela, h, fill=0)
    row1_y = y - 4 * mm
    row2_y = y - 8 * mm
    c.setFont('Helvetica', 8)
    c.drawString(x + 2 * mm, y - h + 2 * mm, 'TIPO DE PÚBLICO:')

    # colunas para público
    col0 = x + 34 * mm
    col1 = x + 70 * mm
    col2 = x + 112 * mm
    col3 = x + 149 * mm
    c.line(col0, y - h, col0, y)
    c.line(col1, y - h, col1, y)
    c.line(col2, y - h, col2, y)
    c.line(col3, y - h, col3, y)

    c.drawString(col0 + 2 * mm, row1_y, 'PRODUTOR')
    c.drawString(col1 + 2 * mm, row1_y, 'LIDERANÇAS')
    c.drawString(col2 + 2 * mm, row1_y, 'ESCOLARES')
    c.drawString(col3 + 2 * mm, row1_y, 'COMERCIANTES')
    c.drawString(col0 + 2 * mm, row2_y, 'PROFESSORES')
    c.drawString(col1 + 2 * mm, row2_y, 'AUTORIDADES')
    c.drawString(col2 + 2 * mm, row2_y, 'SERVIDORES IDARON')
    c.drawString(col3 + 2 * mm, row2_y, 'OUTRO')

    y -= h + 1 * mm
    # QUAL
    h = 8 * mm
    c.rect(x, y - h, largura_tabela, h, fill=0)
    c.drawString(x + 2 * mm, y - h + 2 * mm, 'QUAL?')
    c.drawString(x + 14 * mm, y - h + 2 * mm, str(qual))

    return y - h - 4 * mm


def desenhar_lista_presenca(
    c,
    mes,
    ano,
    regional="",
    unidade="",
    atividade="",
    atividade_palestra="",
    atividade_reuniao="",
    atividade_curso="",
    atividade_encontro="",
    outro_qual="",
    tema="",
    data="",
    horario_inicio="",
    horario_fim="",
    local="",
    municipio="",
    tipo_publico="",
    tipo_publico_outra="",
    qual="",
    total_linhas=31,
):
    largura_pagina, altura_pagina = A4

    y = _draw_header(
        c,
        regional=regional,
        unidade=unidade,
        atividade=atividade,
        atividade_palestra=atividade_palestra,
        atividade_reuniao=atividade_reuniao,
        atividade_curso=atividade_curso,
        atividade_encontro=atividade_encontro,
        outro_qual=outro_qual,
        tema=tema,
        data=data,
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        local=local,
        municipio=municipio,
        tipo_publico=tipo_publico,
        tipo_publico_outra=tipo_publico_outra,
        qual=qual,
    )

    # tabela
    largura_tabela = 180 * mm
    x = (largura_pagina - largura_tabela) / 2
    y_inicio = y

    # colunas: Nº, NOME, MATRÍCULA, CARGO, DIA, ASSINATURA
    num_cols = 6
    largura_igual = largura_tabela / num_cols
    col_x = [x]
    for _ in range(num_cols):
        col_x.append(col_x[-1] + largura_igual)

    altura_header = 7 * mm
    altura_linha = 6 * mm

    c.setLineWidth(0.7)
    c.setFont("Helvetica-Bold", 8)
    c.rect(x, y_inicio - altura_header, largura_tabela, altura_header, fill=0)
    for x_line in col_x[1:]:
        c.line(x_line, y_inicio - altura_header, x_line, y_inicio)

    labels = ["Nº", "Nome", "Matrícula", "Cargo", "Dia", "Assinatura"]
    for i, label in enumerate(labels):
        x_centro = (col_x[i] + col_x[i + 1]) / 2
        c.drawCentredString(x_centro, y_inicio - altura_header / 2 - 2, label)

    y_linha = y_inicio - altura_header
    c.setFont("Helvetica", 8)
    for i in range(1, total_linhas + 1):
        y_linha -= altura_linha
        c.rect(x, y_linha, largura_tabela, altura_linha, fill=0)
        for x_line in col_x[1:]:
            c.line(x_line, y_linha, x_line, y_linha + altura_linha)
        c.drawCentredString((col_x[0] + col_x[1]) / 2, y_linha + 1.8 * mm, str(i))

    # assinaturas de fechamento
    y_final = y_linha - 15 * mm
    if y_final > 15 * mm:
        c.line(x, y_final + 8 * mm, x + largura_tabela, y_final + 8 * mm)
        c.drawString(x + 2 * mm, y_final + 2 * mm, "Assinatura do responsável:")
        c.drawString(x + largura_tabela - 70 * mm, y_final + 2 * mm, "Carimbo / Assinatura")

    return y_final


def gerar_pdf_lista_presenca(
    mes,
    ano,
    regional,
    unidade,
    atividade,
    atividade_palestra,
    atividade_reuniao,
    atividade_curso,
    atividade_encontro,
    outro_qual,
    tema,
    data,
    horario_inicio,
    horario_fim,
    local,
    municipio,
    tipo_publico,
    tipo_publico_outra,
    qual,
):
    from io import BytesIO
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle("Lista de Presenca")

    desenhar_lista_presenca(
        c,
        mes=mes,
        ano=ano,
        regional=regional,
        unidade=unidade,
        atividade=atividade,
        atividade_palestra=atividade_palestra,
        atividade_reuniao=atividade_reuniao,
        atividade_curso=atividade_curso,
        atividade_encontro=atividade_encontro,
        outro_qual=outro_qual,
        tema=tema,
        data=data,
        horario_inicio=horario_inicio,
        horario_fim=horario_fim,
        local=local,
        municipio=municipio,
        tipo_publico=tipo_publico,
        tipo_publico_outra=tipo_publico_outra,
        qual=qual,
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
