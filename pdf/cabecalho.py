from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from pathlib import Path

LOGO_PATH = Path("assets/logo_ro_horizontal.png")

def desenhar_cabecalho(c, margem_esq=15*mm, margem_topo=15*mm):
    largura_pagina, altura_pagina = A4

    # ---------- LOGO ----------
    if not LOGO_PATH.exists():
        raise FileNotFoundError(f"Logo não encontrado: {LOGO_PATH}")

    logo = ImageReader(str(LOGO_PATH))
    w_px, h_px = logo.getSize()

    largura_mm = 60
    w_pt = largura_mm * mm
    proporcao = w_pt / w_px
    h_pt = h_px * proporcao

    x_logo = margem_esq
    y_logo = altura_pagina - margem_topo - h_pt

    c.drawImage(logo, x_logo, y_logo, w_pt, h_pt, preserveAspectRatio=True, mask="auto")

    # ---------- TEXTO ----------
    linha1 = "AGÊNCIA DE DEFESA SANITÁRIA"
    linha2 = "AGROSILVOPASTORIL DO ESTADO DE RONDÔNIA"
    linha3 = "UNIDADE LOCAL DE SÃO MIGUEL DO GUAPORÉ"

    x_direita = largura_pagina - margem_esq
    y_base = y_logo + h_pt * 0.6

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(x_direita, y_base, linha1)

    c.setFont("Helvetica", 10)
    c.drawRightString(x_direita, y_base - 15, linha2)

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(x_direita, y_base - 30, linha3)

    # ---------- LINHA ----------
    c.setLineWidth(0.8)
    c.line(
        margem_esq,
        y_logo - 8,
        largura_pagina - margem_esq,
        y_logo - 8,
    )
