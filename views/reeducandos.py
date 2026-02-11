import streamlit as st

from services.constants import (
    ANOS_OPCOES,
    MESES,
)
from services.parsers import (
    _ler_upload,
    _parse_campos,
    _safe_index,
    parse_feriados_text,
)
from services.pdf_builders import (
    gerar_pdf,
    gerar_relatorio_pdf,
)

def render_folha_ponto():
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.title("📄 Gerador de Folha de Ponto de Reeducandos")

        with st.expander("Importar dados (PDF ou DOCX)", expanded=False):
            arquivo = st.file_uploader("Selecione o PDF ou DOCX da ?ltima folha", type=["pdf", "docx"])
            if arquivo:
                # aplica os campos apenas uma vez por arquivo para permitir edicoes depois
                if st.session_state.get("_ultimo_upload") != arquivo.name:
                    st.session_state["_upload_aplicado"] = False
                    st.session_state["_ultimo_upload"] = arquivo.name

                if not st.session_state.get("_upload_aplicado", False):
                    texto = _ler_upload(arquivo)
                    if not texto:
                        st.warning("N?o consegui ler o arquivo enviado.")
                    else:
                        campos = _parse_campos(texto)
                        st.session_state.update({k: v for k, v in campos.items() if v})
                        st.session_state["_upload_aplicado"] = True
                        st.success("Campos preenchidos a partir do arquivo.")

        with st.expander("Dados do Reeducando", expanded=True):
            secretaria_input = st.text_input("Secretaria", key="secretaria")
            reeducando_input = st.text_input("Reeducando", key="reeducando")
            funcao_input = st.text_input("Função", key="funcao")
            data_inclusao_input = st.text_input("Data da inclusão", key="data_inclusao")
            municipio_input = st.text_input("Município", key="municipio")

            col_doc = st.columns(3)
            with col_doc[0]:
                cpf_input = st.text_input("CPF", key="cpf")
            with col_doc[1]:
                banco_input = st.text_input("Banco (BCO)", key="banco")
            with col_doc[2]:
                agencia_input = st.text_input("Agência (AG)", key="agencia")
            conta_input = st.text_input("Conta", key="conta")
            tipo_opcoes = ["Corrente", "Salário", "Poupança", "Outro"]
            tipo_atual = st.session_state.get("tipo_conta", "")
            if tipo_atual not in tipo_opcoes or tipo_atual == "":
                tipo_radio = "Outro"
                tipo_outro_val = tipo_atual
            else:
                tipo_radio = tipo_atual
                tipo_outro_val = ""
            col_tipo = st.columns([1, 1])
            with col_tipo[0]:
                tipo_radio_sel = st.radio("Tipo de conta", tipo_opcoes, index=tipo_opcoes.index(tipo_radio))
            with col_tipo[1]:
                tipo_outro_val = st.text_input("Outro (se aplicável)", value=tipo_outro_val, key="tipo_conta_outro")
            # valor final do tipo de conta
            if tipo_radio_sel == "Outro":
                tipo_conta_input = tipo_outro_val
            else:
                tipo_conta_input = tipo_radio_sel

            endereco_input = st.text_input("Endereço", key="endereco")
            col_contato = st.columns(3)
            with col_contato[0]:
                cep_input = st.text_input("CEP", key="cep")
            with col_contato[1]:
                telefone_input = st.text_input("Telefone", key="telefone")
            with col_contato[2]:
                data_input = st.text_input("Data", key="data_preenchimento")

        with st.expander("Rodapé (ULSAV/IDARON)", expanded=True):
            rodape_titulo_input = st.text_input("Título do rodapé", key="rodape_titulo")
            rodape_endereco_input = st.text_input("Endereço (rodapé)", key="rodape_endereco")
            rodape_fone_input = st.text_input("Fone/Fax (rodapé)", key="rodape_fone")
            rodape_cep_input = st.text_input("CEP / Cidade (rodapé)", key="rodape_cep")
            rodape_email_input = st.text_input("Email (rodapé)", key="rodape_email")

        with st.expander("Preencher dados da folha", expanded=True):
            # saneia valores de mês/ano antes de criar os widgets
            if st.session_state.get("mes_label") not in MESES:
                st.session_state["mes_label"] = list(MESES.keys())[0]
            anos_opcoes = ANOS_OPCOES
            ano_atual_ss = st.session_state.get("ano", anos_opcoes[0])
            if not isinstance(ano_atual_ss, int):
                try:
                    ano_atual_ss = int(ano_atual_ss)
                except Exception:
                    ano_atual_ss = anos_opcoes[0]
            if ano_atual_ss not in anos_opcoes:
                ano_atual_ss = anos_opcoes[0]
            st.session_state["ano"] = ano_atual_ss

            col_mes, col_ano = st.columns(2)
            with col_mes:
                mes_opcoes = list(MESES.keys())
                mes_label = st.selectbox("Mês", mes_opcoes, key="mes_label")
            with col_ano:
                ano = st.selectbox("Ano", anos_opcoes, key="ano")

            # opções de horário
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
                if not (h == 10 and m == 0)  # começa em 10:30
            ]

            col_he, col_hs = st.columns(2)
            with col_he:
                he_default = st.session_state.get("he", opcoes_he[0])
                he_index = _safe_index(opcoes_he, he_default, 0)
                he = st.selectbox("Horário de entrada (HE)", opcoes_he, index=he_index, key="he")
            with col_hs:
                hs_default = st.session_state.get("hs", opcoes_hs[0])
                hs_index = _safe_index(opcoes_hs, hs_default, 0)
                hs = st.selectbox("Horário de saída (HS)", opcoes_hs, index=hs_index, key="hs")

            feriados_texto = st.text_area(
                "Feriados (formato: dia-descrição, separados por vírgulas)",
                value=st.session_state.get("feriados_texto", ""),
                placeholder="1-Feriado, 2-Feriado2, 3-Feriado3",
                help=(
                    "Use dia-descrição separados por vírgulas. Ex.: 1-Confraternização Universal, "
                    "15-Feriado inventado, 21-Dia tal (dia entre 1 e 31). "
                    "Exemplo para colar: 1-Feriado, 2-Feriado2, 3-Feriado3."
                ),
            )

            st.write(
                """
            Selecione o mês e o ano, gere o PDF com o cabeçalho oficial e depois baixe o arquivo.
            """
            )

            col_btn = st.columns(2)
            with col_btn[0]:
                if st.button("Gerar Folha de Ponto"):

                    feriados_dict, erros = parse_feriados_text(feriados_texto)
                    if erros:
                        st.error("Revise os feriados informados: " + "; ".join(erros))
                    else:
                        st.session_state["feriados_texto"] = feriados_texto
                        st.session_state["pdf"] = gerar_pdf(
                            ano=ano,
                            mes=MESES[mes_label],
                            he=he,
                            hs=hs,
                            endereco=endereco_input,
                            cep=cep_input,
                            telefone=telefone_input,
                            data_preenchimento=data_input,
                            secretaria=secretaria_input,
                            reeducando=reeducando_input,
                            funcao=funcao_input,
                            data_inclusao=data_inclusao_input,
                            municipio=municipio_input,
                            cpf=cpf_input,
                            banco=banco_input,
                            agencia=agencia_input,
                            conta=conta_input,
                            tipo_conta=tipo_conta_input,
                            feriados=feriados_dict,
                        )
                        st.success("Folha de ponto gerada com sucesso!")
            with col_btn[1]:
                if st.button("Gerar Relatório de Atividades"):
                    feriados_dict, erros = parse_feriados_text(feriados_texto)
                    if erros:
                        st.error("Revise os feriados informados: " + "; ".join(erros))
                    else:
                        st.session_state["feriados_texto"] = feriados_texto
                        st.session_state["relatorio_pdf"] = gerar_relatorio_pdf(
                            ano=ano,
                            mes=MESES[mes_label],
                            secretaria=secretaria_input,
                            reeducando=reeducando_input,
                            funcao=funcao_input,
                            municipio=municipio_input,
                            endereco=endereco_input,
                            cep=cep_input,
                            telefone=telefone_input,
                            data_preenchimento=data_input,
                            feriados=feriados_dict,
                            rodape_titulo=rodape_titulo_input,
                            rodape_endereco=rodape_endereco_input,
                            rodape_fone=rodape_fone_input,
                            rodape_cep=rodape_cep_input,
                            rodape_email=rodape_email_input,
                        )
                        st.success("Relatório de atividades gerado com sucesso!")

        # Botões de download
        if "pdf" in st.session_state:
            st.download_button(
                "📄 Baixar Folha de Ponto",
                data=st.session_state["pdf"],
                file_name="folha.pdf",
                mime="application/pdf",
            )
        if "relatorio_pdf" in st.session_state:
            st.download_button(
                "📄 Baixar Relatório de Atividades",
                data=st.session_state["relatorio_pdf"],
                file_name="relatorio_atividades.pdf",
                mime="application/pdf",
            )
