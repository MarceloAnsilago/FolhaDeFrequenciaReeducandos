import streamlit as st
from streamlit.errors import StreamlitAPIException

from services.constants import ANOS_OPCOES, MESES
from services.parsers import _ler_upload, _parse_campos_sugesp, _safe_index, parse_feriados_text
from pdf.sugesp import gerar_pdf_sugesp

def render_folha_ponto_sugesp():
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.title("Gerador de Folha de Ponto - SUGESP")

        with st.expander("Importar dados (PDF ou DOCX)", expanded=False):
            arquivo = st.file_uploader("Selecione o PDF ou DOCX da ultima folha", type=["pdf", "docx"], key="sugesp_upload")
            if arquivo:
                if st.session_state.get("_sugesp_ultimo_upload") != arquivo.name:
                    st.session_state["_sugesp_upload_aplicado"] = False
                    st.session_state["_sugesp_ultimo_upload"] = arquivo.name

                if not st.session_state.get("_sugesp_upload_aplicado", False):
                    texto = _ler_upload(arquivo)
                    if not texto:
                        st.warning("Nao consegui ler o arquivo enviado.")
                    else:
                        campos = _parse_campos_sugesp(texto)
                        st.session_state.update({k: v for k, v in campos.items() if v})
                        st.session_state["_sugesp_upload_aplicado"] = True
                        st.success("Campos preenchidos a partir do arquivo.")

        with st.expander("Dados do servidor (SUGESP)", expanded=True):
            unidade = st.text_input("Unidade", key="sugesp_unidade")
            sub_unidade = st.text_input("Sub unidade", key="sugesp_sub_unidade")
            setor_lotacao = st.text_input("Setor de lotacao", key="sugesp_setor_lotacao")
            servidor = st.text_input("Servidor", key="sugesp_servidor")
            matricula = st.text_input("Matricula", key="sugesp_matricula")
            sigla = st.text_input("Sigla/Local", key="sugesp_sigla")
            cargo = st.text_input("Cargo", key="sugesp_cargo")

        with st.expander("Contato", expanded=True):
            endereco = st.text_input("Endereco", key="sugesp_endereco")
            cep = st.text_input("CEP", key="sugesp_cep")
            telefone = st.text_input("Telefone", key="sugesp_telefone")
            email = st.text_input("Email", key="sugesp_email")
            cpf = st.text_input("CPF", key="sugesp_cpf")
            data_preenchimento = st.text_input("Data", key="sugesp_data_preenchimento")

        with st.expander("Mes, ano e feriados", expanded=True):
            mes_opcoes = list(MESES.keys())
            if st.session_state.get("sugesp_mes_label") not in MESES:
                st.session_state["sugesp_mes_label"] = mes_opcoes[0]
            anos_opcoes = ANOS_OPCOES
            ano_atual_ss = st.session_state.get("sugesp_ano", anos_opcoes[0])
            if not isinstance(ano_atual_ss, int):
                try:
                    ano_atual_ss = int(ano_atual_ss)
                except Exception:
                    ano_atual_ss = anos_opcoes[0]
            if ano_atual_ss not in anos_opcoes:
                ano_atual_ss = anos_opcoes[0]
            st.session_state["sugesp_ano"] = ano_atual_ss

            col_mes, col_ano = st.columns(2)
            with col_mes:
                mes_label = st.selectbox("Mes", mes_opcoes, key="sugesp_mes_label")
            with col_ano:
                ano = st.selectbox("Ano", anos_opcoes, key="sugesp_ano")

            opcoes_he = [
                f"{h:02d}:{m:02d}"
                for h in range(5, 10)
                for m in (0, 30)
                if (h < 9 or (h == 9 and m == 0))
            ]
            opcoes_hs = [
                f"{h:02d}:{m:02d}"
                for h in range(10, 18)
                for m in (0, 30)
                if not (h == 10 and m == 0)
            ]

            col_he, col_hs = st.columns(2)
            with col_he:
                he_default = st.session_state.get("sugesp_he", "")
                he_index = _safe_index(opcoes_he, he_default, 0)
                he = st.selectbox("Horario de entrada", opcoes_he, index=he_index, key="sugesp_he")
            with col_hs:
                hs_default = st.session_state.get("sugesp_hs", "")
                hs_index = _safe_index(opcoes_hs, hs_default, 0)
                hs = st.selectbox("Horario de saida", opcoes_hs, index=hs_index, key="sugesp_hs")

            feriados_texto = st.text_area(
                "Feriados (formato: dia-descricao, separados por virgulas)",
                value=st.session_state.get("sugesp_feriados_texto", ""),
                placeholder="1-Feriado, 2-Feriado2",
            )

            if st.button("Gerar Folha SUGESP"):
                feriados_dict, erros = parse_feriados_text(feriados_texto)
                if erros:
                    st.error("Revise os feriados informados: " + "; ".join(erros))
                else:
                    st.session_state["sugesp_feriados_texto"] = feriados_texto
                    data = {
                        "ano": ano,
                        "mes": MESES[mes_label],
                        "mes_label": mes_label,
                        "unidade": unidade,
                        "sub_unidade": sub_unidade,
                        "setor_lotacao": setor_lotacao,
                        "servidor": servidor,
                        "matricula": matricula,
                        "sigla": sigla,
                        "cargo": cargo,
                        "he": he,
                        "hs": hs,
                        "feriados": feriados_dict,
                        "endereco": endereco,
                        "cep": cep,
                        "telefone": telefone,
                        "email": email,
                        "cpf": cpf,
                        "data_preenchimento": data_preenchimento,
                    }
                    st.session_state["sugesp_pdf"] = gerar_pdf_sugesp(data)
                    st.success("Folha SUGESP gerada com sucesso!")

        if "sugesp_pdf" in st.session_state:
            st.markdown("### Pagina de impressao")
            pdf_bytes = st.session_state["sugesp_pdf"]
            try:
                st.pdf(pdf_bytes)
            except StreamlitAPIException:
                st.info(
                    "Pre-visualizacao de PDF indisponivel neste ambiente. "
                    "Para habilitar, instale: pip install streamlit[pdf]"
                )
            st.download_button(
                "Baixar Folha SUGESP",
                data=pdf_bytes,
                file_name="folha_sugesp.pdf",
                mime="application/pdf",
            )
