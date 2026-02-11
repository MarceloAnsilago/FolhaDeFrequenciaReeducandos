import streamlit as st
from streamlit_option_menu import option_menu

from services.constants import DEFAULTS
from pages.declaracao_nada_consta import render_declaracao_nada_consta
from pages.parcelamento import render_parcelamento
from pages.reeducandos import render_folha_ponto
from pages.restituicao import render_restituicao
from pages.sugesp import render_folha_ponto_sugesp
from pages.veiculos import render_veiculos


st.set_page_config(page_title="Folha de Ponto de Reeducandos", page_icon="\U0001F4C4", layout="wide")

for chave, valor in DEFAULTS.items():
    st.session_state.setdefault(chave, valor)
# flags de controle do upload (para nao sobrescrever apos a primeira aplicacao)
st.session_state.setdefault("_upload_aplicado", False)
st.session_state.setdefault("_ultimo_upload", "")
st.session_state.setdefault("_sugesp_upload_aplicado", False)
st.session_state.setdefault("_sugesp_ultimo_upload", "")


col_esq, col_meio, col_dir = st.columns([1, 2, 1])
with col_meio:
    st.markdown(
        """
        <style>
        /* Forca texto em minusculas no option menu */
        .nav-link, .nav-link span, .nav-link p {
            text-transform: lowercase !important;
            font-variant: normal !important;
            letter-spacing: normal !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            line-height: 1.2 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    destino = option_menu(
        None,
        [
            "Folha Reeducandos",
            "Folha SUGESP",
            "Controle de Veiculos",
            "Parcelar Auto de Infracao",
            "Requerimento de restituicao de valor recolhido indevidamente",
            "Declaracao de nada consta",
        ],
        icons=["file-earmark-text", "file-earmark-ruled", "truck", "receipt", "cash-coin", "file-text"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "nav-link": {"text-transform": "none"},
            "nav-link-selected": {"text-transform": "none"},
        },
    )

if destino == "Folha Reeducandos":
    render_folha_ponto()
elif destino == "Folha SUGESP":
    render_folha_ponto_sugesp()
elif destino == "Controle de Veiculos":
    render_veiculos()
elif destino == "Parcelar Auto de Infracao":
    render_parcelamento()
elif destino == "Declaracao de nada consta":
    render_declaracao_nada_consta()
else:
    render_restituicao()
