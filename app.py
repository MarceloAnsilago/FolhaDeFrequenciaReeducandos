import streamlit as st
from streamlit_option_menu import option_menu

from services.constants import DEFAULTS
from views.cadastro_emissao_gta import render_cadastro_emissao_gta
from views.declaracao_residencia import render_declaracao_residencia
from views.declaracao_nada_consta import render_declaracao_nada_consta
from views.parcelamento import render_parcelamento
from views.reeducandos import render_folha_ponto
from views.restituicao import render_restituicao
from views.sugesp import render_folha_ponto_sugesp
from views.veiculos import render_veiculos


st.set_page_config(page_title="Folha de Ponto de Reeducandos", page_icon="\U0001F4C4", layout="wide")

for chave, valor in DEFAULTS.items():
    st.session_state.setdefault(chave, valor)
# flags de controle do upload (para nao sobrescrever apos a primeira aplicacao)
st.session_state.setdefault("_upload_aplicado", False)
st.session_state.setdefault("_ultimo_upload", "")
st.session_state.setdefault("_sugesp_upload_aplicado", False)
st.session_state.setdefault("_sugesp_ultimo_upload", "")


with st.sidebar:
    st.markdown("### Menu")
    destino = option_menu(
        "Navegacao",
        [
            "Folha Reeducandos",
            "Folha SUGESP",
            "Controle de Veiculos",
            "Cadastro de Emissao de GTA",
            "Parcelar Auto de Infracao",
            "Requerimento de restituicao de valor recolhido indevidamente",
            "Declaracao de nada consta",
            "Declaracao de residencia",
        ],
        icons=[
            "file-earmark-text",
            "file-earmark-ruled",
            "truck",
            "person-vcard",
            "receipt",
            "cash-coin",
            "file-text",
            "house",
        ],
        menu_icon="cast",
        default_index=0,
    )

if destino == "Folha Reeducandos":
    render_folha_ponto()
elif destino == "Folha SUGESP":
    render_folha_ponto_sugesp()
elif destino == "Controle de Veiculos":
    render_veiculos()
elif destino == "Cadastro de Emissao de GTA":
    render_cadastro_emissao_gta()
elif destino == "Parcelar Auto de Infracao":
    render_parcelamento()
elif destino == "Declaracao de nada consta":
    render_declaracao_nada_consta()
elif destino == "Declaracao de residencia":
    render_declaracao_residencia()
else:
    render_restituicao()
