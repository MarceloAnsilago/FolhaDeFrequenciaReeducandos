from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from pdf.cabecalho import desenhar_cabecalho
from pdf.corpo import desenhar_tabela
from pdf.relatorio import gerar_relatorio_cabecalho
from pdf.rodape import desenhar_rodape

def gerar_pdf(
    ano,
    mes,
    he,
    hs,
    endereco,
    cep,
    telefone,
    data_preenchimento,
    secretaria,
    reeducando,
    funcao,
    data_inclusao,
    municipio,
    cpf,
    banco,
    agencia,
    conta,
    tipo_conta,
    feriados=None,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Define título interno do PDF
    c.setTitle("Folha de ponto")

    # Cabeçalho oficial
    y_top = desenhar_cabecalho(c)

    # Corpo
    desenhar_tabela(
        c,
        ano=ano,
        mes=mes,
        he=he,
        hs=hs,
        y_top=y_top,
        feriados=feriados or {},
        endereco=endereco,
        cep=cep,
        telefone=telefone,
        data_preenchimento=data_preenchimento,
        secretaria=secretaria,
        reeducando=reeducando,
        funcao=funcao,
        data_inclusao=data_inclusao,
        municipio=municipio,
        cpf=cpf,
        banco=banco,
        agencia=agencia,
        conta=conta,
        tipo_conta=tipo_conta,
    )

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()


def gerar_relatorio_pdf(
    ano,
    mes,
    secretaria,
    reeducando,
    funcao,
    municipio,
    endereco,
    cep,
    telefone,
    data_preenchimento,
    feriados=None,
    rodape_titulo=None,
    rodape_endereco=None,
    rodape_fone=None,
    rodape_cep=None,
    rodape_email=None,
):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # cabeçalho oficial com logo e título
    y_base = gerar_relatorio_cabecalho(
        c,
        secretaria=secretaria,
        mes=mes,
        ano=ano,
        reeducando=reeducando,
        funcao=funcao,
        municipio=municipio,
        endereco=endereco,
        cep=cep,
        telefone=telefone,
        data_preenchimento=data_preenchimento,
    )

    # tabela de atividades (dias do mês)
    atividade_base = (
        "Serviços de limpeza e conservação do prédio, bens materiais e utensílios da "
        "ULSAV/IDARON de {municipio}. Sob supervisão de um servidor."
    )
    from pdf.relatorio import desenhar_tabela_relatorio  # lazy import

    desenhar_tabela_relatorio(
        c,
        mes=mes,
        ano=ano,
        municipio=municipio,
        atividade_base=atividade_base,
        feriados=feriados or {},
        y_top=y_base,
    )

    # rodapé
    desenhar_rodape(
        c,
        titulo=rodape_titulo or "ULSAV - UNIDADE LOCAL DE SANIDADE ANIMAL E VEGETAL",
        linha_endereco=rodape_endereco or "Av. São Paulo, 436 – Bairro Centro",
        linha_fone=rodape_fone or "Fone/Fax: (69) 3642-1026/8479-9229",
        linha_cep=rodape_cep or "CEP 76.932-000 – São Miguel do Guaporé/RO",
        linha_email=rodape_email or "saomiguel@idaron.ro.gov.br",
    )

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
