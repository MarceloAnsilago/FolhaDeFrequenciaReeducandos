from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader


LOGO_PATH = Path("assets/logo_ro_horizontal.jpg")
LOGO_PATH_ALT = Path("assets/logo_ro_horizontal.JPG")


def desenhar_cabecalho(
    c,
    margem_topo: float = 14 * mm,
    margem_lateral: float = 15 * mm,
    deslocar_logo_para_cima: float = 8 * mm,
) -> float:
    """
    Desenha o cabeçalho oficial com o brasão e devolve a coordenada Y logo abaixo dele.
    Mantém o início do conteúdo mais alto, para afastar rodapé e ganhar espaço na página.
    """
    largura_pagina, altura_pagina = A4

    # ---------- LOGO ----------
    logo_path = LOGO_PATH if LOGO_PATH.exists() else LOGO_PATH_ALT
    y_logo = altura_pagina - margem_topo

    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        w_px, h_px = logo.getSize()
        largura_mm = 24
        w_pt = largura_mm * mm
        proporcao = w_pt / w_px
        h_pt = h_px * proporcao
        x_logo = (largura_pagina - w_pt) / 2
        y_logo = altura_pagina - margem_topo - h_pt - deslocar_logo_para_cima
        c.drawImage(
            logo,
            x_logo,
            y_logo,
            w_pt,
            h_pt,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ---------- TEXTOS ----------
    y_texto = y_logo - 0.5 * mm
    x_centro = largura_pagina / 2

    linha1 = "GOVERNO DO ESTADO DE RONDÔNIA"
    linha2 = "SECRETARIA DE ESTADO DA JUSTIÇA"
    linha3 = "FUNDO PENITENCIÁRIO"

    espacamento = 10
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_centro, y_texto, linha1)
    c.drawCentredString(x_centro, y_texto - espacamento, linha2)
    c.drawCentredString(x_centro, y_texto - 2 * espacamento, linha3)

    # devolve posição logo abaixo do cabeçalho (mais alto, sem subtrair deslocamento)
    y_base_cabecalho = y_texto - 2 * espacamento
    return y_base_cabecalho - 2 * mm
