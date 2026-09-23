import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Fechamento Ticket Alimentação", layout="wide")

st.title("💳 Fechamento de Ticket Alimentação")
st.markdown("Automação com controle de ativos, suspensão de afastados, corte de admissão e apuração de faltas (D-2).")

# ==========================================
# 1. PARÂMETROS
# ==========================================
with st.sidebar:
    st.header("⚙️ Parâmetros do Fechamento")
    competencia = st.text_input("Competência de Pagamento", value="01/10/2026")
    valor_diario = st.number_input("Valor Diário do Benefício (R$)", min_value=0.0, value=30.00, step=1.0)
    dias_uteis = st.number_input("Dias Úteis do Mês", min_value=1, max_value=31, value=22)
    data_corte = st.date_input("Data de Corte de Admissão", value=datetime(2026, 9, 23))

    st.markdown("---")
    st.caption(
        "Regras Ativas:\n"
        "- Base principal: Ativos do mês\n"
        "- Afastados: Benefício suspenso\n"
        "- Admitidos pós-corte: Saldo retido para o mês seguinte\n"
        "- Faltas: Apuradas no ciclo 16 a 15 (D-2)"
    )

# ==========================================
# 2. UPLOAD DOS ARQUIVOS BASE
# ==========================================
col_up1, col_up2 = st.columns(2)
with col_up1:
    file_ativos = st.file_uploader("1️⃣ Base de Ativos do Mês (.xlsx)", type=["xlsx"], help="Deve conter: Matricula, Nome, CPF, Data_Admissao")
with col_up2:
    file_afastados = st.file_uploader("2️⃣ Relatório de Afastados / INSS (.xlsx - Opcional)", type=["xlsx"], help="Deve conter a coluna Matricula")

if file_ativos is not None:
    try:
        df_ativos = pd.read_excel(file_ativos)
        df_ativos.columns = [c.strip() for c in df_ativos.columns]

        colunas_necessarias = ['Matricula', 'Nome', 'CPF', 'Data_Admissao']
        ausentes = [c for c in colunas_necessarias if c not in df_ativos.columns]

        if ausentes:
            st.error(f"⚠️ As seguintes colunas não foram encontradas na Base de Ativos: {', '.join(ausentes)}")
        else:
            df_ativos['Matricula'] = df_ativos['Matricula'].astype(str).str.strip()
            df_ativos['Data_Admissao'] = pd.to_datetime(df_ativos['Data_Admissao'], errors='coerce')
            
            # Tratar saldo pré-existente
            if 'Saldo_Retroativo_Dias' not in df_ativos.columns:
                df_ativos['Saldo_Retroativo_Dias'] = 0
            df_ativos['Saldo_Retroativo_Dias'] = df_ativos['Saldo_Retroativo_Dias'].fillna(0)

            # Identificar afastados
            mats_afastadas = set()
            if file_afastados is not None:
                df_afast = pd.read_excel(file_afastados)
                df_afast.columns = [c.strip() for c in df_afast.columns]
                if 'Matricula' in df_afast.columns:
                    mats_afastadas = set(df_afast['Matricula'].astype(str).str.strip().unique())

            # ==========================================
            # 3. CONTROLE DE FALTAS (ARQUIVO OU MANUAL)
            # ==========================================
            st.markdown("---")
            st.subheader("⏱️ Lançamento de Faltas (Período 16 a 15)")
            
            opcao_faltas = st.radio(
                "Como deseja apurar as faltas deste mês?",
                ["Subir Relatório do Ponto (.xlsx)", "Digitar / Ajustar na Tabela Manualmente"],
                horizontal=True
            )

            if opcao_faltas == "Subir Relatório do Ponto (.xlsx)":
                file_faltas = st.file_uploader("Suba o espelho/relatório de faltas do ponto", type=["xlsx"])
                if file_faltas is not None:
                    df_faltas = pd.read_excel(file_faltas)
                    df_faltas.columns = [c.strip() for c in df_faltas.columns]
                    col_faltas = [c for c in df_faltas.columns if 'falta' in c.lower()]
                    
                    if col_faltas and 'Matricula' in df_faltas.columns:
                        col_nome_falta = col_faltas[0]
                        df_faltas['Matricula'] = df_faltas['Matricula'].astype(str).str.strip()
                        df_faltas = df_faltas[['Matricula', col_nome_falta]].rename(columns={col_nome_falta: 'Faltas'})
                        df_ativos = pd.merge(df_ativos, df_faltas, on='Matricula', how='left')
                        df_ativos['Faltas'] = df_ativos['Faltas'].fillna(0)
                        st.success("Faltas cruzadas com sucesso a partir do relatório!")
                    else:
                        st.error("O arquivo de faltas precisa conter a coluna 'Matricula' e uma coluna com 'Faltas'.")
                        df_ativos['Faltas'] = 0
                else:
                    df_ativos['Faltas'] = 0
            else:
                if 'Faltas' not in df_ativos.columns:
                    df_ativos['Faltas'] = 0
                st.info("💡 Edite as faltas diretamente na coluna 'Faltas' abaixo (as demais colunas estão bloqueadas):")
                df_ativos = st.data_editor(
                    df_ativos,
                    column_config={
                        "Faltas": st.column_config.NumberColumn("Faltas a Descontar", min_value=0, max_value=31, step=1)
                    },
                    disabled=[c for c in df_ativos.columns if c != 'Faltas'],
                    use_container_width=True
                )

            # ==========================================
            # 4. PROCESSAMENTO DAS REGRAS DE NEGÓCIO
            # ==========================================
            def aplicar_calculos(row):
                mat = row['Matricula']
                admissao = row['Data_Admissao'].date() if pd.notnull(row['Data_Admissao']) else None
                faltas = row.get('Faltas', 0)
                saldo_retro = row.get('Saldo_Retroativo_Dias', 0)

                # Regra 1: Afastado
                if mat in mats_afastadas:
                    return pd.Series({
                        'Status': 'Afastado - Benefício Suspenso',
                        'Entra_Carga': False,
                        'Dias_Pagar': 0,
                        'Valor_Final': 0.0,
                        'Saldo_Proximo_Mes': 0
                    })

                # Regra 2: Admitido após o corte (dia 23)
                if admissao and admissao > data_corte:
                    dias_acumular = max(0, 30 - admissao.day + 1)
                    return pd.Series({
                        'Status': f'Admitido pós-corte ({admissao.strftime("%d/%m")})',
                        'Entra_Carga': False,
                        'Dias_Pagar': 0,
                        'Valor_Final': 0.0,
                        'Saldo_Proximo_Mes': saldo_retro + dias_acumular
                    })

                # Regra 3: Apto normal (recebe mês + saldo anterior - faltas)
                dias_calculados = max(0, dias_uteis + saldo_retro - faltas)
                return pd.Series({
                    'Status': 'Apto para Crédito',
                    'Entra_Carga': True,
                    'Dias_Pagar': dias_calculados,
                    'Valor_Final': dias_calculados * valor_diario,
                    'Saldo_Proximo_Mes': 0
                })

            res = df_ativos.apply(aplicar_calculos, axis=1)
            df_final = pd.concat([df_ativos, res], axis=1)

            df_envio = df_final[df_final['Entra_Carga'] == True][['Matricula', 'CPF', 'Nome', 'Valor_Final']].rename(columns={'Valor_Final': 'Valor_Beneficio'})
            df_retidos = df_final[df_final['Entra_Carga'] == False]

            # ==========================================
            # 5. DASHBOARD & DOWNLOADS
            # ==========================================
            st.markdown("---")
            st.subheader("📊 Resumo do Pedido")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Ativos", len(df_ativos))
            c2.metric("Créditos no Pedido", len(df_envio))
            c3.metric("Valor Total (R$)", f"R$ {df_envio['Valor_Beneficio'].sum():,.2f}")
            c4.metric("Afastados / Pós-corte", len(df_retidos))

            tab1, tab2, tab3 = st.tabs(["✅ Arquivo para Ticket", "🚫 Retidos / Afastados", "📋 Controle Completo"])

            with tab1:
                st.dataframe(df_envio, use_container_width=True)
                buf_ticket = io.BytesIO()
                with pd.ExcelWriter(buf_ticket, engine='openpyxl') as writer:
                    df_envio.to_excel(writer, index=False)
                st.download_button("⬇️ Baixar Pedido Ticket (.xlsx)", buf_ticket.getvalue(), file_name=f"pedido_ticket_{competencia.replace('/', '_')}.xlsx")

            with tab2:
                st.dataframe(df_retidos[['Matricula', 'Nome', 'Status', 'Saldo_Proximo_Mes']], use_container_width=True)

            with tab3:
                st.dataframe(df_final, use_container_width=True)
                buf_completo = io.BytesIO()
                with pd.ExcelWriter(buf_completo, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button("⬇️ Baixar Relatório Geral com Saldo (.xlsx)", buf_completo.getvalue(), file_name=f"controle_geral_{competencia.replace('/', '_')}.xlsx")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
