from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from pdf.cabecalho import desenhar_cabecalho


def gerar_relatorio_cabecalho(
    c,
    secretaria,
    ano,
    reeducando,
    funcao,
    municipio,
    endereco,
    cep,
    telefone,
    data_preenchimento,
):
    """
    Apenas desenha o cabeçalho oficial (logo e textos institucionais) e retorna a base
    para continuar o conteúdo do relatório.
    """
    # usa o mesmo cabeçalho oficial da folha de ponto
    y_base = desenhar_cabecalho(c)
    return y_base
