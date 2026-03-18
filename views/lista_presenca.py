import streamlit as st
from streamlit.errors import StreamlitAPIException

from services.pdf_builders import gerar_lista_presenca_pdf
from services.constants import MESES, ANOS_OPCOES


def render_lista_presenca():
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.title("🗒️ Lista de Presença")

        with st.expander("Identificação", expanded=True):
            regional = st.text_input("Regional")
            unidade = st.text_input("Unidade")
            atividade = st.text_input("Atividade")

        with st.expander("Atividade (marque as opções)", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                atividade_palestra = st.checkbox("Palestra")
            with col2:
                atividade_reuniao = st.checkbox("Reunião")
            with col3:
                atividade_curso = st.checkbox("Curso/Treinamento")
            with col4:
                atividade_encontro = st.checkbox("Encontro")
            outro_qual = st.text_input("Outro - Qual?")

        with st.expander("Tema, Data e Local", expanded=True):
            tema = st.text_input("Tema")
            col_data, col_hora1, col_hora2 = st.columns([1, 1, 1])
            with col_data:
                data = st.text_input("Data")
            with col_hora1:
                horario_inicio = st.text_input("Horário Início")
            with col_hora2:
                horario_fim = st.text_input("Horário Fim")

            col_local, col_municipio = st.columns(2)
            with col_local:
                local = st.text_input("Local")
            with col_municipio:
                municipio = st.text_input("Município")

        with st.expander("Tipo de Público", expanded=True):
            tipo1, tipo2, tipo3, tipo4 = st.columns(4)
            with tipo1:
                tipo_produtor = st.checkbox("Produtor")
            with tipo2:
                tipo_liderancas = st.checkbox("Lideranças")
            with tipo3:
                tipo_escolares = st.checkbox("Escolares")
            with tipo4:
                tipo_comerciantes = st.checkbox("Comerciantes")

            tipo5, tipo6, tipo7, tipo8 = st.columns(4)
            with tipo5:
                tipo_professores = st.checkbox("Professores")
            with tipo6:
                tipo_autoridades = st.checkbox("Autoridades")
            with tipo7:
                tipo_servidores = st.checkbox("Servidores IDARON")
            with tipo8:
                tipo_outro = st.checkbox("Outro")

            tipo_publico_outra = st.text_input("Outro (se aplicável)")
            qual = st.text_input("Qual?")

        with st.expander("Competência", expanded=True):
            col_mes, col_ano = st.columns(2)
            with col_mes:
                mes_label = st.selectbox("Mês", list(MESES.keys()))
            with col_ano:
                ano = st.selectbox("Ano", ANOS_OPCOES)

        if st.button("Gerar Lista de Presença"):
            pdf_bytes = gerar_lista_presenca_pdf(
                mes=MESES[mes_label],
                ano=ano,
                regional=regional,
                unidade=unidade,
                atividade=atividade,
                atividade_palestra='X' if atividade_palestra else '',
                atividade_reuniao='X' if atividade_reuniao else '',
                atividade_curso='X' if atividade_curso else '',
                atividade_encontro='X' if atividade_encontro else '',
                outro_qual=outro_qual,
                tema=tema,
                data=data,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                local=local,
                municipio=municipio,
                tipo_publico=', '.join(
                    [
                        v
                        for v, checked in [
                            ('Produtor', tipo_produtor),
                            ('Lideranças', tipo_liderancas),
                            ('Escolares', tipo_escolares),
                            ('Comerciantes', tipo_comerciantes),
                            ('Professores', tipo_professores),
                            ('Autoridades', tipo_autoridades),
                            ('Servidores IDARON', tipo_servidores),
                            ('Outro', tipo_outro),
                        ]
                        if checked
                    ]
                ),
                tipo_publico_outra=tipo_publico_outra,
                qual=qual,
            )
            st.success("Lista de presença gerada.")
            try:
                st.pdf(pdf_bytes)
            except StreamlitAPIException:
                st.info("Pre-visualização indisponível. Instale streamlit[pdf].")
            st.download_button(
                "Baixar Lista de Presença",
                data=pdf_bytes,
                file_name="lista_presenca.pdf",
                mime="application/pdf",
            )
