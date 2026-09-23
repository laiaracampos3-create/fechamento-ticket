import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# Configuração da página institucional
st.set_page_config(
    page_title="Turin - Gestão de Benefícios",
    page_icon="💳",
    layout="wide"
)

# Estilização visual inspirada na identidade visual da Turin
st.markdown("""
    <style>
        /* Cor de destaque principal */
        :root {
            --primary-color: #2eb85c;
        }
        /* Personalização dos botões principais */
        .stButton>button, .stDownloadButton>button {
            background-color: #2eb85c !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold !important;
            padding: 0.5rem 1.2rem !important;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #238a45 !important;
            color: white !important;
        }
        /* Cartões de métricas */
        div[data-testid="stMetricValue"] {
            color: #2eb85c !important;
            font-weight: 700 !important;
        }
        /* Título e cabeçalhos */
        h1, h2, h3 {
            color: #1f2937;
        }
        .turin-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 25px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL COM IDENTIDADE VISUAL
# ==========================================
with st.sidebar:
    if os.path.exists("LOGO.PNG"):
        st.image("LOGO.PNG", use_container_width=True)
    else:
        st.title("TURIN")
        
    st.markdown("---")
    st.subheader("⚙️ Parâmetros do Fechamento")
    competencia = st.text_input("Competência de Pagamento", value="01/10/2026")
    valor_diario = st.number_input("Valor Diário do Vale (R$)", min_value=0.0, value=30.00, step=1.0)
    dias_uteis = st.number_input("Dias Úteis do Mês", min_value=1, max_value=31, value=22)
    data_corte = st.date_input("Data de Corte de Admissão", value=datetime(2026, 9, 23))

    st.markdown("---")
    st.caption(
        "**Regras do Fechamento:**\n"
        "• Demitidos: Retirados (apuração em TRCT)\n"
        "• Afastados: Benefício suspenso\n"
        "• Admissões pós-corte: Saldo retido p/ próximo mês\n"
        "• Faltas: Descontadas da competência anterior (16 a 15)"
    )

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.markdown("""
    <div class="turin-header">
        <div>
            <h1 style="margin: 0; font-size: 2rem;">Sistema de Fechamento de Benefícios</h1>
            <p style="margin: 0; color: #6b7280; font-size: 1rem;">Módulo de Cálculo e Exportação do Vale Alimentação</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# UPLOAD DAS BASES DE DADOS
# ==========================================
col_up1, col_up2 = st.columns(2)
with col_up1:
    file_ativos = st.file_uploader("1️⃣ Base de Colaboradores Ativos (.xlsx)", type=["xlsx"], help="Deve conter: Matricula, Nome, CPF, Data_Admissao")
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
            # APURAÇÃO DE FALTAS
            # ==========================================
            st.markdown("---")
            st.subheader("⏱️ Apuração de Faltas (Período 16 a 15)")
            
            opcao_faltas = st.radio(
                "Origem das faltas:",
                ["Importar Relatório de Ponto (.xlsx)", "Preencher / Ajustar Manualmente"],
                horizontal=True
            )

            if opcao_faltas == "Importar Relatório de Ponto (.xlsx)":
                file_faltas = st.file_uploader("Selecione o ficheiro de faltas", type=["xlsx"])
                if file_faltas is not None:
                    df_faltas = pd.read_excel(file_faltas)
                    df_faltas.columns = [c.strip() for c in df_faltas.columns]
                    col_faltas = [c for c in df_faltas.columns if 'falta' in c.lower()]
                    
                    if col_faltas and 'Matricula' in df_faltas.columns:
                        col_nome = col_faltas[0]
                        df_faltas['Matricula'] = df_faltas['Matricula'].astype(str).str.strip()
                        df_faltas = df_faltas[['Matricula', col_nome]].rename(columns={col_nome: 'Faltas'})
                        df_ativos = pd.merge(df_ativos, df_faltas, on='Matricula', how='left')
                        df_ativos['Faltas'] = df_ativos['Faltas'].fillna(0)
                        st.success("Faltas apuradas e integradas com sucesso.")
                    else:
                        st.error("O ficheiro precisa ter a coluna 'Matricula' e uma com 'Faltas'.")
                        df_ativos['Faltas'] = 0
                else:
                    df_ativos['Faltas'] = 0
            else:
                if 'Faltas' not in df_ativos.columns:
                    df_ativos['Faltas'] = 0
                st.info("Altere as faltas diretamente na coluna 'Faltas' abaixo:")
                df_ativos = st.data_editor(
                    df_ativos,
                    column_config={
                        "Faltas": st.column_config.NumberColumn("Faltas a Descontar", min_value=0, max_value=31, step=1)
                    },
                    disabled=[c for c in df_ativos.columns if c != 'Faltas'],
                    use_container_width=True
                )

            # ==========================================
            # MOTOR DE CÁLCULO
            # ==========================================
            def processar_regras(row):
                mat = row['Matricula']
                admissao = row['Data_Admissao'].date() if pd.notnull(row['Data_Admissao']) else None
                faltas = row.get('Faltas', 0)
                saldo_retro = row.get('Saldo_Retroativo_Dias', 0)

                # 1. Afastado
                if mat in mats_afastadas:
                    return pd.Series({
                        'Status': 'Afastado - Benefício Suspenso',
                        'Entra_Carga': False,
                        'Dias_Pagar': 0,
                        'Valor_Final': 0.0,
                        'Saldo_Proximo_Mes': 0
                    })

                # 2. Admitido pós-corte
                if admissao and admissao > data_corte:
                    dias_acumular = max(0, 30 - admissao.day + 1)
                    return pd.Series({
                        'Status': f'Admitido pós-corte ({admissao.strftime("%d/%m")})',
                        'Entra_Carga': False,
                        'Dias_Pagar': 0,
                        'Valor_Final': 0.0,
                        'Saldo_Proximo_Mes': saldo_retro + dias_acumular
                    })

                # 3. Regular
                dias_calculados = max(0, dias_uteis + saldo_retro - faltas)
                return pd.Series({
                    'Status': 'Elegível',
                    'Entra_Carga': True,
                    'Dias_Pagar': dias_calculados,
                    'Valor_Final': dias_calculados * valor_diario,
                    'Saldo_Proximo_Mes': 0
                })

            res = df_ativos.apply(processar_regras, axis=1)
            df_final = pd.concat([df_ativos, res], axis=1)

            df_envio = df_final[df_final['Entra_Carga'] == True][['Matricula', 'CPF', 'Nome', 'Valor_Final']].rename(columns={'Valor_Final': 'Valor_Beneficio'})
            df_retidos = df_final[df_final['Entra_Carga'] == False]

            # ==========================================
            # RESULTADOS E DOWNLOADS
            # ==========================================
            st.markdown("---")
            st.subheader("📊 Resumo do Pedido")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Colaboradores Ativos", len(df_ativos))
            c2.metric("Créditos no Arquivo", len(df_envio))
            c3.metric("Valor Total do Pedido", f"R$ {df_envio['Valor_Beneficio'].sum():,.2f}")
            c4.metric("Bloqueados / Pós-Corte", len(df_retidos))

            tab1, tab2, tab3 = st.tabs(["✅ Arquivo de Carga (Ticket)", "🚫 Retidos / Suspensos", "📋 Base Geral de Controle"])

            with tab1:
                st.dataframe(df_envio, use_container_width=True)
                buf_ticket = io.BytesIO()
                with pd.ExcelWriter(buf_ticket, engine='openpyxl') as writer:
                    df_envio.to_excel(writer, index=False)
                st.download_button(
                    "⬇️ Descarregar Arquivo de Carga (.xlsx)",
                    buf_ticket.getvalue(),
                    file_name=f"carga_ticket_{competencia.replace('/', '_')}.xlsx"
                )

            with tab2:
                st.dataframe(df_retidos[['Matricula', 'Nome', 'Status', 'Saldo_Proximo_Mes']], use_container_width=True)

            with tab3:
                st.dataframe(df_final, use_container_width=True)
                buf_completo = io.BytesIO()
                with pd.ExcelWriter(buf_completo, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button(
                    "⬇️ Descarregar Relatório Completo (.xlsx)",
                    buf_completo.getvalue(),
                    file_name=f"controle_geral_{competencia.replace('/', '_')}.xlsx"
                )

    except Exception as e:
        st.error(f"Erro no processamento dos dados: {e}")
