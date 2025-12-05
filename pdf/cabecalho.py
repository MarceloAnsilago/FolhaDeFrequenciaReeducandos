from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from pathlib import Path

LOGO_PATH = Path("assets/logo_ro_horizontal.jpg")

def desenhar_cabecalho(c, margem_topo=5*mm, margem_lateral=15*mm):
    largura_pagina, altura_pagina = A4

    # ---------- LOGO ----------
    if not LOGO_PATH.exists():
        raise FileNotFoundError(f"Logo não encontrado: {LOGO_PATH}")

    logo = ImageReader(str(LOGO_PATH))
    w_px, h_px = logo.getSize()

    largura_mm = 32  # levemente menor
    w_pt = largura_mm * mm
    proporcao = w_pt / w_px
    h_pt = h_px * proporcao

    # Logo MUITO mais alto
    x_logo = (largura_pagina - w_pt) / 2
    y_logo = altura_pagina - margem_topo - h_pt

    c.drawImage(
        logo,
        x_logo,
        y_logo,
        w_pt,
        h_pt,
        preserveAspectRatio=True,
        mask="auto"
    )

    # ---------- TEXTOS ----------
    # menos espaço entre logo e texto
    y_texto = y_logo - 3*mm  
    x_centro = largura_pagina / 2

    linha1 = "GOVERNO DO ESTADO DE RONDÔNIA"
    linha2 = "SECRETARIA DE ESTADO DA JUSTIÇA"
    linha3 = "FUNDO PENITENCIÁRIO"

    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_centro, y_texto, linha1)
    c.drawCentredString(x_centro, y_texto - 10, linha2)
    c.drawCentredString(x_centro, y_texto - 20, linha3)

   