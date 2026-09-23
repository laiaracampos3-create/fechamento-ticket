import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import base64
from PIL import Image

# ==========================================
# FAVICON E TÍTULO
# ==========================================
icone_separador = "💳"
possiveis_nomes = ["LOGO.PNG", "logo.png", "LOGO.png", "logo.PNG", "LOGO.jpeg", "logo.jpg"]

for nome in possiveis_nomes:
    if os.path.exists(nome):
        try:
            icone_separador = Image.open(nome)
            break
        except Exception:
            pass

st.set_page_config(
    page_title="Turin | Portal de Gestão de Benefícios",
    page_icon=icone_separador,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOGO BASE64
# ==========================================
def carregar_logo():
    for nome in possiveis_nomes:
        if os.path.exists(nome):
            with open(nome, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None

logo_b64 = carregar_logo()

# ==========================================
# CSS PROFISSIONAL - DESIGN TURIN
# ==========================================
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }}

        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 1.5rem !important;
        }}

        .stApp {{
            background-color: #f8fafc;
        }}

        .header-container {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 18px 26px;
            border-radius: 12px;
            margin-top: 0px !important;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 6px solid #22c55e;
        }}
        .header-title {{
            color: #ffffff !important;
            font-size: 24px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        .header-subtitle {{
            color: #cbd5e1 !important;
            font-size: 13px;
            margin: 4px 0 0 0;
        }}
        .header-badge {{
            background-color: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }}

        section[data-testid="stSidebar"] {{
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }}
        .sidebar-logo-box {{
            text-align: center;
            padding: 10px 0 20px 0;
            border-bottom: 1px solid #f1f5f9;
            margin-bottom: 15px;
        }}

        /* Cards de Métricas Estilizados */
        div[data-testid="stMetric"] {{
            background-color: #ffffff;
            padding: 16px 20px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        div[data-testid="stMetricLabel"] {{
            color: #64748b;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        div[data-testid="stMetricValue"] {{
            color: #16a34a !important;
            font-size: 24px;
            font-weight: 700;
        }}

        .stButton>button, .stDownloadButton>button {{
            background-color: #22c55e !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(34, 197, 94, 0.2);
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{
            background-color: #16a34a !important;
            box-shadow: 0 4px 6px rgba(34, 197, 94, 0.3);
            transform: translateY(-1px);
        }}

        div[data-testid="stFileUploader"] {{
            background-color: #ffffff;
            padding: 14px;
            border-radius: 10px;
            border: 1px dashed #cbd5e1;
        }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL
# ==========================================
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<div class="sidebar-logo-box"><img src="{logo_b64}" style="max-width: 170px; height: auto;"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="sidebar-logo-box"><h2 style="color: #22c55e; margin:0; letter-spacing: 2px;">TURIN</h2></div>',
            unsafe_allow_html=True
        )

    st.subheader("⚙️ Parâmetros do Fechamento")
    competencia = st.text_input("Competência de Pagamento", value="01/10/2026")
    
    col_par1, col_par2 = st.columns(2)
    with col_par1:
        dias_base_mes = st.number_input("Dias Base", min_value=1, max_value=31, value=30)
    with col_par2:
        valor_diario = st.number_input("Diária (R$)", min_value=0.0, value=25.00, step=0.50)
        
    valor_mensal_cheio = dias_base_mes * valor_diario
    st.metric("Total Mensal", f"R$ {valor_mensal_cheio:,.2f}")
    
    data_corte = st.date_input(
        "Corte de Admissão",
        value=datetime(2026, 9, 23),
        format="DD/MM/YYYY"
    )

    st.markdown("---")
    st.subheader("🧪 Ambiente de Testes")
    
    # Modelo já com coluna de Unidade/CNPJ simulada
    df_modelo_teste = pd.DataFrame({
        'Matricula': ['1001', '1002', '1003', '1004', '1005'],
        'Nome': [
            'Carlos Alberto Silva',
            'Mariana Souza Costa',
            'Roberto Ferreira Lima',
            'Lucas Henrique Mendes',
            'Fernanda Oliveira Dias'
        ],
        'CPF': [
            '111.222.333-44',
            '222.333.444-55',
            '333.444.555-66',
            '444.555.666-77',
            '555.666.777-88'
        ],
        'Data_Admissao': [
            '2023-03-15',
            '2024-08-10',
            '2026-09-12',
            '2026-09-25',
            '2026-08-28'
        ],
        'Unidade': ['Unidade 1 - Matriz', 'Unidade 2 - Filial', 'Unidade 1 - Matriz', 'Unidade 2 - Filial', 'Unidade 1 - Matriz'],
        'Saldo_Retroativo_Dias': [0, 0, 0, 0, 3]
    })
    
    buf_modelo = io.BytesIO()
    with pd.ExcelWriter(buf_modelo, engine='openpyxl') as writer:
        df_modelo_teste.to_excel(writer, index=False)
        
    st.download_button(
        "📥 Baixar Modelo com 2 Unidades",
        data=buf_modelo.getvalue(),
        file_name="ativos_teste_unidades.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.markdown("""
    <div class="header-container">
        <div>
            <h1 class="header-title">Portal de Fechamento de Benefícios</h1>
            <p class="header-subtitle">Módulo de Validação e Exportação de Crédito do Vale Alimentação</p>
        </div>
        <div class="header-badge">
            TURIN RH / DP
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# ENTRADA DE FICHEIROS
# ==========================================
col_up1, col_up2 = st.columns(2)
with col_up1:
    file_ativos = st.file_uploader("1️⃣ Base de Colaboradores Ativos (.xlsx)", type=["xlsx"], help="Deve conter: Matricula, Nome, CPF, Data_Admissao e (opcionalmente) Unidade/CNPJ")
with col_up2:
    file_afastados = st.file_uploader("2️⃣ Relatório de Afastados / INSS (.xlsx - Opcional)", type=["xlsx"], help="Lista de matrículas a suspender no mês")

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
            
            # Identifica coluna de unidade/filial se existir
            col_unidade = [c for c in df_ativos.columns if c.lower() in ['unidade', 'filial', 'cnpj', 'empresa']]
            nome_col_unidade = col_unidade[0] if col_unidade else None
            
            if 'Saldo_Retroativo_Dias' not in df_ativos.columns:
                df_ativos['Saldo_Retroativo_Dias'] = 0
            df_ativos['Saldo_Retroativo_Dias'] = df_ativos['Saldo_Retroativo_Dias'].fillna(0)

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
                        st.success("✅ Faltas integradas com sucesso!")
                    else:
                        st.error("O ficheiro precisa conter a coluna 'Matricula' e uma com 'Faltas'.")
                        df_ativos['Faltas'] = 0
                else:
                    df_ativos['Faltas'] = 0
            else:
                if 'Faltas' not in df_ativos.columns:
                    df_ativos['Faltas'] = 0
                st.info("💡 Altere as faltas diretamente na coluna 'Faltas' abaixo:")
                df_ativos = st.data_editor(
                    df_ativos,
                    column_config={
                        "Faltas": st.column_config.NumberColumn("Faltas a Descontar", min_value=0, max_value=30, step=1)
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
                        'Status': 'Afastado (Suspenso)',
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
                dias_calculados = max(0, dias_base_mes + saldo_retro - faltas)
                return pd.Series({
                    'Status': 'Elegível',
                    'Entra_Carga': True,
                    'Dias_Pagar': dias_calculados,
                    'Valor_Final': dias_calculados * valor_diario,
                    'Saldo_Proximo_Mes': 0
                })

            res = df_ativos.apply(processar_regras, axis=1)
            df_final = pd.concat([df_ativos, res], axis=1)

            cols_export = ['Matricula', 'CPF', 'Nome', 'Valor_Final']
            if nome_col_unidade:
                cols_export.insert(3, nome_col_unidade)
                
            df_envio = df_final[df_final['Entra_Carga'] == True][cols_export].rename(columns={'Valor_Final': 'Valor_Beneficio'})
            df_retidos = df_final[df_final['Entra_Carga'] == False]

            # ==========================================
            # PAINEL DE CARDS COM VALORES POR UNIDADE
            # ==========================================
            st.markdown("---")
            st.subheader("📊 Somatório de Cartões e Valores")
            
            valor_total_geral = df_envio['Valor_Beneficio'].sum()
            total_cartoes_geral = len(df_envio)

            if nome_col_unidade and df_envio[nome_col_unidade].nunique() > 1:
                unidades = df_envio[nome_col_unidade].unique()
                cols_cards = st.columns(1 + len(unidades))
                
                # Card 1: Total Geral
                cols_cards[0].metric(
                    "TOTAL GERAL (LOTE)",
                    f"R$ {valor_total_geral:,.2f}",
                    help=f"{total_cartoes_geral} cartões a carregar"
                )
                
                # Cards das Unidades Individuais
                for i, u in enumerate(unidades):
                    df_u = df_envio[df_envio[nome_col_unidade] == u]
                    val_u = df_u['Valor_Beneficio'].sum()
                    qtd_u = len(df_u)
                    cols_cards[i + 1].metric(
                        f"{str(u).upper()}",
                        f"R$ {val_u:,.2f}",
                        help=f"{qtd_u} colaboradores nesta unidade"
                    )
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Cartões a Carregar", total_cartoes_geral)
                c2.metric("Valor Total do Lote", f"R$ {valor_total_geral:,.2f}")
                c3.metric("Suspensos / Retidos", len(df_retidos))

            # ==========================================
            # TABS DE VISUALIZAÇÃO E DOWNLOADS
            # ==========================================
            tab1, tab2, tab3 = st.tabs(["✅ Arquivos para Ticket", "🚫 Suspensos / Retidos", "📋 Base Completa de Fechamento"])

            with tab1:
                st.dataframe(df_envio, use_container_width=True)
                
                st.markdown("##### 📥 Opções de Download")
                # Botão do Lote Geral
                buf_ticket = io.BytesIO()
                with pd.ExcelWriter(buf_ticket, engine='openpyxl') as writer:
                    df_envio.to_excel(writer, index=False)
                st.download_button(
                    "⬇️ Baixar Lote Geral Consolidado (.xlsx)",
                    buf_ticket.getvalue(),
                    file_name=f"lote_ticket_geral_{competencia.replace('/', '_')}.xlsx"
                )

                # Se houver mais de uma unidade, permite baixar arquivos individuais por CNPJ
                if nome_col_unidade and df_envio[nome_col_unidade].nunique() > 1:
                    st.write("---")
                    st.caption("Arquivos individuais por Unidade / CNPJ:")
                    cols_dl = st.columns(len(df_envio[nome_col_unidade].unique()))
                    for idx, un in enumerate(df_envio[nome_col_unidade].unique()):
                        df_sub = df_envio[df_envio[nome_col_unidade] == un]
                        buf_sub = io.BytesIO()
                        with pd.ExcelWriter(buf_sub, engine='openpyxl') as writer:
                            df_sub.to_excel(writer, index=False)
                        cols_dl[idx].download_button(
                            f"⬇️ Baixar {un} ({len(df_sub)} cartões)",
                            buf_sub.getvalue(),
                            file_name=f"ticket_{str(un).lower().replace(' ', '_')}_{competencia.replace('/', '_')}.xlsx"
                        )

            with tab2:
                cols_ret = ['Matricula', 'Nome', 'Status', 'Saldo_Proximo_Mes']
                if nome_col_unidade:
                    cols_ret.insert(2, nome_col_unidade)
                st.dataframe(df_retidos[cols_ret], use_container_width=True)

            with tab3:
                st.dataframe(df_final, use_container_width=True)
                buf_completo = io.BytesIO()
                with pd.ExcelWriter(buf_completo, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button(
                    "⬇️ Baixar Relatório Completo de Fechamento (.xlsx)",
                    buf_completo.getvalue(),
                    file_name=f"fechamento_completo_{competencia.replace('/', '_')}.xlsx"
                )

    except Exception as e:
        st.error(f"Erro no processamento dos dados: {e}")
