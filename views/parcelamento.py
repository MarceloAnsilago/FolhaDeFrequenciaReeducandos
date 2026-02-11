import locale
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

def render_parcelamento():
    # tenta usar locale BR se disponivel
    try:
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    except locale.Error:
        pass

    css = """
    <style>
        /* Remove negrito dos itens do radio */
        div[data-baseweb="radio"] label {
            font-weight: normal !important;
            font-family: inherit !important;
            font-size: 1rem !important;
        }
        header {
            visibility: hidden;
        }
        /* Mantem o fundo padrão do app */
        .stApp {
            background-color: transparent;
        }
        .stApp .main .block-container h1 {
            text-align: center;
        }
        /* Oculta o botao de imprimir ao imprimir */
        @media print {
            .no-print, .print-button {
                display: none !important;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    def k(name: str) -> str:
        return f"parc_{name}"

    st.session_state.setdefault(k("auto_info_submitted"), False)
    st.session_state.setdefault(k("data_requerimento"), datetime.today())
    st.session_state.setdefault(k("data_auto"), datetime.today())
    st.session_state.setdefault(k("N_auto"), "")
    st.session_state.setdefault(k("nome_completo"), "")
    st.session_state.setdefault(k("cpf"), "")
    st.session_state.setdefault(k("endereco"), "")
    st.session_state.setdefault(k("municipio"), "")
    st.session_state.setdefault(k("valor_upf"), "124,46")
    st.session_state.setdefault(k("qtd_upf_por_animal"), 2.5)
    st.session_state.setdefault(k("qtd_upf_por_parcela"), 3.0)
    st.session_state.setdefault(k("n_animais"), 0)
    st.session_state.setdefault(
        k("prazo_defesa"),
        "Sim (Desconto de 20% pra uma parcela)",
    )

    def formatar_moeda_br(valor):
        """Converte float para BRL formatado, ex: 1234.5 -> R$ 1.234,50"""
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return "R$ 0,00"

        texto = f"{valor:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.title("Parcelar Auto de Infração")
        tabs = st.tabs(["Preencher Requerimento", "Tabela de Descontos"])

    with tabs[0]:
        with st.expander("Dados do Auto de Infração", expanded=True):
            st.subheader("Dados do Auto de Infração")
            with st.form("form_auto_info"):
                col1, col2 = st.columns(2)
                with col1:
                    st.date_input(
                        "Data do requerimento",
                        key=k("data_requerimento"),
                    )
                with col2:
                    st.date_input(
                        "Data do Auto de Infração",
                        key=k("data_auto"),
                    )

                st.text_input(
                    "Numero do Auto de Infração:",
                    key=k("N_auto"),
                )

                continuar = st.form_submit_button("Continuar")

            if continuar:
                st.session_state[k("auto_info_submitted")] = True

        if not st.session_state[k("auto_info_submitted")]:
            st.info(
                "Preencha os dados do auto acima e pressione Enter (ou Continuar) "
                "para liberar o restante do requerimento."
            )
            st.stop()

        data_requerimento = st.session_state[k("data_requerimento")]
        data_auto = st.session_state[k("data_auto")]

        with st.expander("Dados do Autuado", expanded=True):
            st.subheader("Dados do Autuado")
            with st.form("form_requerimento"):
                nome_completo = st.text_input("Nome completo:", key=k("nome_completo"))
                cpf = st.text_input("No do CPF:", key=k("cpf"))
                endereco = st.text_input("Endereco:", key=k("endereco"))
                municipio = st.text_input("Municipio:", key=k("municipio"))

                colA, colB, colC = st.columns(3)
                with colA:
                    valor_upf = st.text_input(
                        "Valor da UPF:",
                        value=st.session_state.get(k("valor_upf"), "124,46"),
                        key=k("valor_upf"),
                    )
                with colB:
                    qtd_upf_por_animal = st.number_input(
                        "Qtd UPF por animal/Auto:",
                        min_value=0.0,
                        step=0.5,
                        format="%.2f",
                        value=float(st.session_state.get(k("qtd_upf_por_animal"), 2.5)),
                        key=k("qtd_upf_por_animal"),
                    )
                with colC:
                    qtd_upf_por_parcela = st.number_input(
                        "Qtd minima de UPF por parcela:",
                        min_value=0.0,
                        step=0.5,
                        format="%.2f",
                        value=float(st.session_state.get(k("qtd_upf_por_parcela"), 3.0)),
                        key=k("qtd_upf_por_parcela"),
                    )

                n_animais = st.number_input(
                    "Numero de Animais/Auto de Infração:",
                    min_value=0,
                    step=1,
                    key=k("n_animais"),
                )

                prazo_defesa_escolhido = st.radio(
                    "No prazo de defesa ate 30 dias?",
                    ("Sim (Desconto de 20% pra uma parcela)", "Nao (Desconto de 10% pra uma parcela)"),
                    key=k("prazo_defesa"),
                )

                submit_form = st.form_submit_button("Aplicar / Atualizar")

            if submit_form:
                try:
                    valor_upf_float = float(valor_upf.replace(",", "."))
                except ValueError:
                    st.error("Valor da UPF invalido, usando 0.")
                    valor_upf_float = 0.0

                st.session_state[k("valor_upf_float")] = valor_upf_float

        valor_upf_float = st.session_state.get(k("valor_upf_float"), 0.0)
        total_upf = (
            st.session_state.get(k("n_animais"), 0)
            * st.session_state.get(k("qtd_upf_por_animal"), 0)
            * valor_upf_float
        )

        if total_upf > 0:
            st.metric("Valor do Auto", formatar_moeda_br(total_upf))
        else:
            st.write("Valor do Auto: R$ 0,00")

        if valor_upf_float > 0:
            min_valor_parcela = st.session_state[k("qtd_upf_por_parcela")] * valor_upf_float
        else:
            min_valor_parcela = 0

        if total_upf >= min_valor_parcela and min_valor_parcela > 0:
            num_max_parcelas = int(total_upf // min_valor_parcela)
        else:
            num_max_parcelas = 0
        num_max_parcelas = min(num_max_parcelas, 30)

        if prazo_defesa_escolhido == "Sim (Desconto de 20% pra uma parcela)":
            desconto_mensagem = "**Desconto aplicado para prazo dentro dos 30 dias**"
            coluna_desconto = "Desconto Concedido (Integral)"
        else:
            desconto_mensagem = "**Desconto aplicado para prazo fora dos 30 dias**"
            coluna_desconto = "Desconto Concedido (metade)"

        st.markdown(desconto_mensagem)

        if num_max_parcelas > 0:
            st.write(
                f"Eh possivel parcelar em ate {num_max_parcelas} vezes, respeitando "
                f"o valor minimo de R$ {min_valor_parcela:.2f} por parcela."
            )
        else:
            st.write(
                f"O valor total e menor que o minimo exigido para uma parcela: R$ {min_valor_parcela:.2f}."
            )

        parcelas_selecionadas_df = pd.DataFrame(
            columns=["Parcela", "Valor da Parcela", "Data de Vencimento"]
        ).set_index("Parcela")

        if st.session_state.get(k("prazo_defesa")) == "Sim (Desconto de 20% pra uma parcela)":
            coluna_desconto = "Desconto Concedido (Integral)"
        else:
            coluna_desconto = "Desconto Concedido (metade)"

        discount_percentage = 0
        valor_com_desconto = 0
        valor_parcela_final = 0

        if num_max_parcelas > 0:
            with st.expander("Opcoes de Parcelamento", expanded=True):
                data_dict = {
                    "Quantidade de Parcelas": list(range(1, 32)),
                    "Desconto Concedido (Integral)": [
                        20, 12, 11.5, 11, 10.5, 10, 9.5, 9, 8.5, 8,
                        7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3,
                        2.5, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.25, 0, 0
                    ],
                    "Desconto Concedido (metade)": [
                        10, 6, 5.75, 5.5, 5.25, 5, 4.75, 4.5, 4.25, 4,
                        3.75, 3.5, 3.25, 3, 2.75, 2.5, 2.25, 2, 1.75, 1.5,
                        1.25, 1, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0, 0
                    ],
                }

                df_descontos = pd.DataFrame(data_dict)
                df_descontos["Desconto (%)"] = df_descontos[coluna_desconto].apply(lambda x: f"{x}%")
                df_descontos["Valor com Desconto"] = total_upf * (1 - df_descontos[coluna_desconto] / 100)
                df_descontos["Valor da Parcela"] = (
                    df_descontos["Valor com Desconto"] / df_descontos["Quantidade de Parcelas"]
                )
                df_descontos["Desconto Concedido"] = total_upf - df_descontos["Valor com Desconto"]

                df_descontos_display = df_descontos.copy()
                for c in ["Valor com Desconto", "Valor da Parcela", "Desconto Concedido"]:
                    df_descontos_display[c] = df_descontos_display[c].apply(formatar_moeda_br)

                tabela_para_exibir = df_descontos_display[
                    ["Quantidade de Parcelas", "Desconto (%)", "Desconto Concedido", "Valor com Desconto", "Valor da Parcela"]
                ]
                tabela_para_exibir = tabela_para_exibir[
                    tabela_para_exibir["Quantidade de Parcelas"] <= num_max_parcelas
                ]

                st.dataframe(tabela_para_exibir, use_container_width=True)

                if num_max_parcelas > 1:
                    num_parcelas_selecionadas = st.slider(
                        "Quantidade de parcelas desejada",
                        min_value=1,
                        max_value=num_max_parcelas,
                        value=1,
                    )
                else:
                    num_parcelas_selecionadas = 1

                st.markdown(
                    "Use o controle acima para escolher o parcelamento que melhor atende o requerimento."
                )

                discount_row = df_descontos[
                    df_descontos["Quantidade de Parcelas"] == num_parcelas_selecionadas
                ].iloc[0]
                discount_percentage = discount_row[coluna_desconto]
                valor_com_desconto = total_upf * (1 - discount_percentage / 100)
                valor_parcela_final = valor_com_desconto / num_parcelas_selecionadas

                dados_parcelas = []
                for i in range(1, num_parcelas_selecionadas + 1):
                    data_venc = data_requerimento + pd.DateOffset(months=i - 1)
                    dados_parcelas.append(
                        {
                            "Parcela": i,
                            "Valor da Parcela": formatar_moeda_br(valor_parcela_final),
                            "Data de Vencimento": data_venc.strftime("%d/%m/%Y"),
                        }
                    )

                parcelas_selecionadas_df = pd.DataFrame(dados_parcelas).set_index("Parcela")

        if not parcelas_selecionadas_df.empty:
            data_req_label = st.session_state[k("data_requerimento")].strftime("%d/%m/%Y")
            data_auto_label = st.session_state[k("data_auto")].strftime("%d/%m/%Y")
            n_auto = st.session_state.get(k("N_auto"), "")
            nome_completo = st.session_state.get(k("nome_completo"), "")
            cpf = st.session_state.get(k("cpf"), "")
            endereco = st.session_state.get(k("endereco"), "")
            municipio = st.session_state.get(k("municipio"), "")

            total_upf_float = st.session_state.get(k("valor_upf_float"), 0.0)
            total_upf = (
                st.session_state.get(k("n_animais"), 0)
                * st.session_state.get(k("qtd_upf_por_animal"), 0)
                * total_upf_float
            )

            desconto_reais = total_upf - valor_com_desconto
            if desconto_reais < 0:
                desconto_reais = 0

            texto_requerimento = (
                f"Eu, {nome_completo}, brasileiro(a), portador(a) do CPF no {cpf}, "
                f"residente no endereco {endereco}, municipio de {municipio}, "
                f"venho, por meio deste requerimento datado de {data_req_label}, solicitar o parcelamento "
                f"do Auto de Infração no {n_auto}, lavrado em {data_auto_label}, nos termos da legislacao vigente."
            )

            if total_upf > 0 and parcelas_selecionadas_df.shape[0] > 0:
                texto_parcelamento = (
                    f"O requerente solicitou o parcelamento em {parcelas_selecionadas_df.shape[0]} vezes, "
                    f"conforme a tabela de descontos, o que lhe confere o direito a um desconto de "
                    f"{discount_percentage}% (equivalente a {formatar_moeda_br(desconto_reais)}) sobre o valor inicial. "
                    f"Assim, o valor total, que originalmente era de {formatar_moeda_br(total_upf)}, "
                    f"passara a ser de {formatar_moeda_br(valor_com_desconto)}, distribuido em "
                    f"{parcelas_selecionadas_df.shape[0]} parcelas de {formatar_moeda_br(valor_parcela_final)} cada."
                )
            else:
                texto_parcelamento = (
                    "Nao e possivel parcelar, pois o valor total e inferior ao minimo exigido para uma parcela."
                )

            html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <title>Requerimento de Parcelamento</title>
                <style>
                    @page {{
                        margin: 20mm;
                        @bottom-center {{
                            content: "Pagina " counter(page) " de " counter(pages);
                            font-size: 10pt;
                        }}
                    }}
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        padding: 20px;
                    }}
                    p {{
                        text-indent: 2em;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: auto;
                        padding: 20px;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                    }}
                    h2 {{
                        text-align: center;
                    }}
                    .texto-requerimento {{
                        margin-top: 20px;
                        line-height: 1.5;
                        text-align: justify;
                    }}
                    .texto-parcelamento {{
                        margin-top: 20px;
                        font-weight: bold;
                        text-align: justify;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #f4f4f4;
                    }}
                    .signature {{
                        margin-top: 40px;
                        text-align: center;
                    }}
                    .signature p {{
                        margin: 0;
                        text-align: center;
                    }}
                    .print-button {{
                        display: block;
                        text-align: center;
                        margin-top: 20px;
                    }}
                    @media print {{
                        .no-print, .print-button {{
                            display: none !important;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Requerimento para Parcelamento de Auto de Infração - Emitido pela Agencia IDARON</h2>

                    <div class="texto-requerimento">
                        <p>{texto_requerimento}</p>
                    </div>

                    <div class="texto-parcelamento">
                        <p>{texto_parcelamento}</p>
                    </div>

                    <h3>Parcelas e Vencimentos</h3>
                    <table>
                        <tr>
                            <th>Parcela</th>
                            <th>Valor da Parcela</th>
                            <th>Data de Vencimento</th>
                        </tr>
            """
            for index, row in parcelas_selecionadas_df.iterrows():
                html += f"""
                        <tr>
                            <td>{index}</td>
                            <td>{row['Valor da Parcela']}</td>
                            <td>{row['Data de Vencimento']}</td>
                        </tr>
                """
            html += f"""
                    </table>

                    <div class="signature">
                        <p>Segue assinado</p>
                        <br><br>
                        <p>________________________________________</p>
                        <p>{nome_completo}</p>
                        <p>{cpf}</p>
                    </div>

                    <div class="print-button no-print">
                        <button onclick="window.print()">Imprimir Requerimento</button>
                    </div>
                </div>
            </body>
            </html>
            """

            components.html(html, height=800, scrolling=True)

    with tabs[1]:
        st.markdown("### Tabela de Descontos")
        dados = {
            "Quantidade de Parcelas": range(1, 31),
            "Desconto Concedido (Integral)": [
                20, 12, 11.5, 11, 10.5, 10, 9.5, 9, 8.5, 8,
                7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3,
                2.5, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.25, 0
            ],
            "Desconto Concedido (metade)": [
                10, 6, 5.75, 5.5, 5.25, 5, 4.75, 4.5, 4.25, 4,
                3.75, 3.5, 3.25, 3, 2.75, 2.5, 2.25, 2, 1.75, 1.5,
                1.25, 1, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0
            ],
        }
        df_desc = pd.DataFrame(dados)
        df_html = df_desc.to_html(index=False)
        df_html_styled = f"<style>td, th {{text-align: center;}}</style>{df_html}"
        st.markdown(df_html_styled, unsafe_allow_html=True)
