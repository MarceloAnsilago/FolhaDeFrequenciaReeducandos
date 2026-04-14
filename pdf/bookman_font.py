from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def ensure_bookman_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD

    if getattr(ensure_bookman_fonts, "_loaded", False):
        return

    regular_path = Path(r"C:\Windows\Fonts\BOOKOS.TTF")
    bold_path = Path(r"C:\Windows\Fonts\BOOKOSB.TTF")
    if regular_path.exists() and bold_path.exists():
        pdfmetrics.registerFont(TTFont("BookmanOldStyle", str(regular_path)))
        pdfmetrics.registerFont(TTFont("BookmanOldStyle-Bold", str(bold_path)))
        FONT_REGULAR = "BookmanOldStyle"
        FONT_BOLD = "BookmanOldStyle-Bold"

    ensure_bookman_fonts._loaded = True
