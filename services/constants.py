from datetime import datetime

MESES = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARÇO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}

ANO_INICIO = 2025
ANOS_OPCOES = list(range(ANO_INICIO, ANO_INICIO + 11))
ANO_ATUAL = datetime.now().year

# session state defaults
DEFAULTS = {
    "secretaria": "",
    "reeducando": "",
    "funcao": "",
    "data_inclusao": "",
    "municipio": "",
    "cpf": "",
    "banco": "",
    "agencia": "",
    "conta": "",
    "tipo_conta": "",
    "endereco": "",
    "cep": "",
    "telefone": "",
    "data_preenchimento": "__/__/____",
    "rodape_titulo": "ULSAV - UNIDADE LOCAL DE SANIDADE ANIMAL E VEGETAL",
    "rodape_endereco": "Av. São Paulo, 436 – Bairro Centro",
    "rodape_fone": "Fone/Fax: (69) 3642-1026/8479-9229",
    "rodape_cep": "CEP 76.932-000 – São Miguel do Guaporé/RO",
    "rodape_email": "saomiguel@idaron.ro.gov.br",
    "mes_label": list(MESES.keys())[0],
    "ano": ANO_ATUAL if ANO_ATUAL in ANOS_OPCOES else ANOS_OPCOES[0],
    "he": "07:30",
    "hs": "13:30",
    "feriados_texto": "",
}
