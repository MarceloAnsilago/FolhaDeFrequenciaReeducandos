from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from pathlib import Path

LOGO_ESQ_PATH = Path("assets/logo_inferior_esq.JPG")
LOGO_DIR_PATH = Path("assets/logo_inferior_dir.JPG")


def desenhar_rodape(
    c,
    margem_inferior=8 * mm,
    margem_lateral=15 * mm,
):
    """
    Desenha rodapé com linha superior, logos esquerdo/direito (se existirem)
    e bloco de texto central com endereço e contato da ULSAV.
    Retorna a coordenada y logo acima do rodapé.
    """
    largura_pagina, _ = A4
    altura_rodape = 22 * mm
    y_base = margem_inferior + altura_rodape
    x_esq = margem_lateral
    x_dir = largura_pagina - margem_lateral

    # linha superior do rodapé
    c.setLineWidth(1)
    c.line(x_esq, y_base, x_dir, y_base)

    # logos (se existirem)
    logo_h = 14 * mm
    logo_w = 38 * mm
    y_logo = margem_inferior + 4 * mm

    if LOGO_ESQ_PATH.exists():
        img_esq = ImageReader(str(LOGO_ESQ_PATH))
        c.drawImage(
            img_esq,
            x_esq,
            y_logo,
            logo_w,
            logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    if LOGO_DIR_PATH.exists():
        img_dir = ImageReader(str(LOGO_DIR_PATH))
        c.drawImage(
            img_dir,
            x_dir - logo_w,
            y_logo,
            logo_w,
            logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # bloco de texto central
    texto = [
        "ULSAV - UNIDADE LOCAL DE SANIDADE ANIMAL E VEGETAL",
        "Av. São Paulo, 436 – Bairro Centro",
        "Fone/Fax: (69) 3642-1026/8479-9229",
        "CEP 76.932-000 – São Miguel do Guaporé/RO",
        "saomiguel@idaron.ro.gov.br",
    ]
    c.setFont("Helvetica-Bold", 9)
    x_centro = largura_pagina / 2
    y_texto = y_logo + logo_h - 1 * mm

    for i, linha in enumerate(texto):
        # primeira linha em negrito, demais regulares
        if i == 0:
            c.setFont("Helvetica-Bold", 9)
        else:
            c.setFont("Helvetica", 9)
        c.drawCentredString(x_centro, y_texto - i * 10, linha)

    return y_base + 2 * mm
