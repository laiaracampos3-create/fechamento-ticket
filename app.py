import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io
import os
import base64
from PIL import Image

# ==========================================
# FAVICON E CONFIGURAÇÃO DA PÁGINA
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
# CARREGAMENTO DA LOGO (BASE64)
# ==========================================
def carregar_logo():
    for nome in possiveis_nomes:
        if os.path.exists(nome):
            with open(nome, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None

logo_b64 = carregar_logo()

# Função para normalizar CPF (remove pontos, traços e espaços)
def normalizar_cpf(serie):
    return serie.astype(str).str.replace(r'\D', '', regex=True).str.zfill(11)

# ==========================================
# CSS CLEAN & EXECUTIVO - DESIGN TURIN
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 1.5rem !important;
        }

        .stApp {
            background-color: #f8fafc;
        }

        /* BANNER PRINCIPAL CLEAN */
        .header-container {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 20px 28px;
            border-radius: 12px;
            margin-top: 0px !important;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-left: 6px solid #22c55e;
        }
        .header-title {
            color: #ffffff !important;
            font-size: 24px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header-subtitle {
            color: #94a3b8 !important;
            font-size: 13px;
            margin: 6px 0 0 0;
            font-weight: 400;
        }
        .header-subtitle b {
            color: #e2e8f0 !important;
        }
        .header-badge {
            background-color: rgba(34, 197, 94, 0.12);
            color: #4ade80;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(34, 197, 94, 0.25);
            white-space: nowrap;
        }

        /* SIDEBAR CLEAN */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        .sidebar-logo-box {
            text-align: center;
            padding: 10px 0 16px 0;
            border-bottom: 1px solid #f1f5f9;
            margin-bottom: 15px;
        }

        /* CARDS DA BARRA LATERAL */
        .param-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px;
            margin: 14px 0 16px 0;
        }
        .param-item {
            margin-bottom: 10px;
        }
        .param-item:last-child {
            margin-bottom: 0px;
        }
        .param-label {
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }
        .param-value {
            font-size: 13px;
            font-weight: 600;
            color: #0f172a;
        }

        .total-box {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 12px 14px;
            text-align: center;
            margin-top: 14px;
        }
        .total-label {
            font-size: 11px;
            font-weight: 700;
            color: #166534;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .total-value {
            font-size: 22px;
            font-weight: 800;
            color: #15803d;
            margin-top: 2px;
        }

        /* METRICAS E BOTOES */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 16px 20px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        div[data-testid="stMetricLabel"] {
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }
        div[data-testid="stMetricValue"] {
            color: #16a34a !important;
            font-size: 24px;
            font-weight: 700;
        }

        .stButton>button, .stDownloadButton>button {
            background-color: #22c55e !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 8px 18px !important;
            box-shadow: 0 2px 4px rgba(34, 197, 94, 0.15);
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #16a34a !important;
            box-shadow: 0 4px 6px rgba(34, 197, 94, 0.25);
        }

        div[data-testid="stFileUploader"] {
            background-color: #ffffff;
            padding: 14px;
            border-radius: 10px;
            border: 1px dashed #cbd5e1;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CÁLCULO DINÂMICO DE COMPETÊNCIA E D-1
# ==========================================
hoje = date.today()

opcoes_datas = [hoje.replace(day=1) + relativedelta(months=i) for i in range(-5, 7)]
dict_competencias = {d.strftime("01/%m/%Y"): d for d in opcoes_datas}

# ==========================================
# BARRA LATERAL
# ==========================================
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<div class="sidebar-logo-box"><img src="{logo_b64}" style="max-width: 160px; height: auto;"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="sidebar-logo-box"><h2 style="color: #22c55e; margin:0; letter-spacing: 2px;">TURIN</h2></div>',
            unsafe_allow_html=True
        )

    st.markdown("### ⚙️ Parâmetros")
    
    comp_str_lista = list(dict_competencias.keys())
    idx_comp_atual = comp_str_lista.index(hoje.strftime("01/%m/%Y")) if hoje.strftime("01/%m/%Y") in comp_str_lista else 5
    
    competencia_str = st.selectbox(
        "Mês de Pagamento do Ticket",
        options=comp_str_lista,
        index=idx_comp_atual
    )
    
    dt_comp = dict_competencias[competencia_str]
    
    # Período de Ponto em D-1
    dt_ponto_fim = dt_comp - relativedelta(months=1)
    dt_ponto_fim_15 = dt_ponto_fim.replace(day=15)
    dt_ponto_ini_16 = (dt_ponto_fim_15 - relativedelta(months=1)).replace(day=16)
    
    periodo_faltas_ativo = f"{dt_ponto_ini_16.strftime('%d/%m/%Y')} a {dt_ponto_fim_15.strftime('%d/%m/%Y')}"

    # Corte de Admissão
    data_corte = st.date_input(
        "Corte de Admissão",
        value=hoje,
        format="DD/MM/YYYY",
        help="Admissões após esta data não entram no crédito atual e acumulam saldo para o mês seguinte."
    )

    st.markdown(f"""
        <div class="param-card">
            <div class="param-item">
                <div class="param-label">🗓️ Período de Ponto (D-1)</div>
                <div class="param-value">{periodo_faltas_ativo}</div>
            </div>
            <div class="param-item">
                <div class="param-label">✂️ Trava de Admissão</div>
                <div class="param-value">{data_corte.strftime('%d/%m/%Y')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_par1, col_par2 = st.columns(2)
    with col_par1:
        dias_base_mes = st.number_input("Dias Base", min_value=1, max_value=31, value=30)
    with col_par2:
        valor_diario = st.number_input("Diária (R$)", min_value=0.0, value=25.00, step=0.50)
        
    valor_mensal_cheio = dias_base_mes * valor_diario
    
    st.markdown(f"""
        <div class="total-box">
            <div class="total-label">Total Mês Cheio</div>
            <div class="total-value">R$ {valor_mensal_cheio:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption(
        "🔒 **LGPD:** Identificação por CPF interno (Sem CPF no lote de saída)\n"
        "• Demitidos: Excluídos (pago em TRCT)\n"
        "• Afastados: Benefício suspenso\n"
        "• Pós-Corte: Saldo retido p/ próximo mês"
    )

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.markdown(f"""
    <div class="header-container">
        <div>
            <h1 class="header-title">Portal de Fechamento de Benefícios</h1>
            <p class="header-subtitle">
                Competência: <b>{competencia_str}</b> &nbsp;|&nbsp; 
                Faltas (D-1): <b>{periodo_faltas_ativo}</b> &nbsp;|&nbsp; 
                Corte de Admissão: <b>{data_corte.strftime('%d/%m/%Y')}</b>
            </p>
        </div>
        <div class="header-badge">
            DEPARTAMENTO PESSOAL OURO BRANCO
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# NAVEGAÇÃO PRINCIPAL
# ==========================================
modulo_principal = st.radio(
    "Selecione o módulo de trabalho:",
    ["⚡ Novo Fechamento da Folha", "📂 Consultar Histórico de Meses Anteriores"],
    horizontal=True
)

# --------------------------------------------------------------------------
# MÓDULO 1: NOVO FECHAMENTO (CHAVE: CPF)
# --------------------------------------------------------------------------
if modulo_principal == "⚡ Novo Fechamento da Folha":
    col_up1, col_up2, col_up3 = st.columns(3)
    with col_up1:
        file_ativos = st.file_uploader("1️⃣ Colaboradores Ativos (.xlsx)", type=["xlsx"], help="Obrigatório: CPF, Nome, Data_Admissao e Unidade")
    with col_up2:
        file_demitidos = st.file_uploader("2️⃣ Relatório de Demitidos (.xlsx - Opcional)", type=["xlsx"], help="Deve conter a coluna CPF")
    with col_up3:
        file_afastados = st.file_uploader("3️⃣ Afastados / INSS (.xlsx - Opcional)", type=["xlsx"], help="Deve conter a coluna CPF")

    if file_ativos is not None:
        try:
            df_ativos = pd.read_excel(file_ativos)
            df_ativos.columns = [c.strip() for c in df_ativos.columns]

            colunas_necessarias = ['CPF', 'Nome', 'Data_Admissao']
            ausentes = [c for c in colunas_necessarias if c not in df_ativos.columns]

            if ausentes:
                st.error(f"⚠️ As seguintes colunas não foram encontradas na Base de Ativos: {', '.join(ausentes)}")
            else:
                df_ativos['CPF_Clean'] = normalizar_cpf(df_ativos['CPF'])
                df_ativos['Data_Admissao'] = pd.to_datetime(df_ativos['Data_Admissao'], errors='coerce')
                
                col_unidade = [c for c in df_ativos.columns if c.lower() in ['unidade', 'filial', 'cnpj', 'empresa']]
                nome_col_unidade = col_unidade[0] if col_unidade else None
                
                if 'Saldo_Retroativo_Dias' not in df_ativos.columns:
                    df_ativos['Saldo_Retroativo_Dias'] = 0
                df_ativos['Saldo_Retroativo_Dias'] = pd.to_numeric(df_ativos['Saldo_Retroativo_Dias'], errors='coerce').fillna(0).astype(int)

                # Demitidos cruzados por CPF
                cpfs_demitidos = set()
                if file_demitidos is not None:
                    df_demit = pd.read_excel(file_demitidos)
                    df_demit.columns = [c.strip() for c in df_demit.columns]
                    if 'CPF' in df_demit.columns:
                        cpfs_demitidos = set(normalizar_cpf(df_demit['CPF']).unique())

                # Afastados cruzados por CPF
                cpfs_afastados = set()
                if file_afastados is not None:
                    df_afast = pd.read_excel(file_afastados)
                    df_afast.columns = [c.strip() for c in df_afast.columns]
                    if 'CPF' in df_afast.columns:
                        cpfs_afastados = set(normalizar_cpf(df_afast['CPF']).unique())

                # ==========================================
                # APURAÇÃO DE FALTAS
                # ==========================================
                st.markdown("---")
                st.subheader(f"⏱️ Apuração de Faltas — Período: {periodo_faltas_ativo}")
                
                opcao_faltas = st.radio(
                    "Origem das faltas:",
                    ["Importar Relatório de Ponto (.xlsx)", "Preencher / Ajustar Manualmente"],
                    horizontal=True
                )

                if opcao_faltas == "Importar Relatório de Ponto (.xlsx)":
                    file_faltas = st.file_uploader(f"Selecione o arquivo de faltas ({periodo_faltas_ativo})", type=["xlsx"])
                    if file_faltas is not None:
                        df_faltas = pd.read_excel(file_faltas)
                        df_faltas.columns = [c.strip() for c in df_faltas.columns]
                        col_faltas = [c for c in df_faltas.columns if 'falta' in c.lower()]
                        
                        if col_faltas and 'CPF' in df_faltas.columns:
                            col_nome = col_faltas[0]
                            df_faltas['CPF_Clean'] = normalizar_cpf(df_faltas['CPF'])
                            df_faltas = df_faltas[['CPF_Clean', col_nome]].rename(columns={col_nome: 'Faltas'})
                            
                            if 'Faltas' in df_ativos.columns:
                                df_ativos = df_ativos.drop(columns=['Faltas'])
                                
                            df_ativos = pd.merge(df_ativos, df_faltas, on='CPF_Clean', how='left')
                            df_ativos['Faltas'] = pd.to_numeric(df_ativos['Faltas'], errors='coerce').fillna(0).astype(int)
                            st.success(f"✅ Faltas de {periodo_faltas_ativo} integradas com sucesso por CPF!")
                        else:
                            st.error("O arquivo precisa conter a coluna 'CPF' e uma coluna de 'Faltas'.")
                            df_ativos['Faltas'] = 0
                    else:
                        df_ativos['Faltas'] = 0
                else:
                    if 'Faltas' not in df_ativos.columns:
                        df_ativos['Faltas'] = 0
                    df_ativos['Faltas'] = pd.to_numeric(df_ativos['Faltas'], errors='coerce').fillna(0).astype(int)
                    st.info(f"💡 Altere as faltas apuradas em {periodo_faltas_ativo} diretamente na tabela:")
                    df_ativos = st.data_editor(
                        df_ativos,
                        column_config={
                            "Faltas": st.column_config.NumberColumn("Faltas a Descontar", min_value=0, max_value=30, step=1)
                        },
                        disabled=[c for c in df_ativos.columns if c != 'Faltas'],
                        use_container_width=True
                    )

                df_ativos['Faltas'] = pd.to_numeric(df_ativos['Faltas'], errors='coerce').fillna(0).astype(int)
                df_ativos['Saldo_Retroativo_Dias'] = pd.to_numeric(df_ativos['Saldo_Retroativo_Dias'], errors='coerce').fillna(0).astype(int)

                # ==========================================
                # MOTOR DE CÁLCULO BLINDADO
                # ==========================================
                def processar_regras(row):
                    cpf_id = str(row['CPF_Clean'])
                    admissao = row['Data_Admissao']
                    
                    data_adm = None
                    if pd.notnull(admissao):
                        if isinstance(admissao, (datetime, pd.Timestamp)):
                            data_adm = admissao.date()
                        elif isinstance(admissao, str):
                            data_adm = pd.to_datetime(admissao, errors='coerce').date()

                    faltas = int(row.get('Faltas', 0))
                    saldo_retro = int(row.get('Saldo_Retroativo_Dias', 0))

                    # 1. Demitido
                    if cpf_id in cpfs_demitidos:
                        return pd.Series({
                            'Status': 'Demitido (Pago em TRCT)',
                            'Entra_Carga': False,
                            'Dias_Pagar': 0,
                            'Valor_Final': 0.0,
                            'Saldo_Proximo_Mes': 0
                        })

                    # 2. Afastado
                    if cpf_id in cpfs_afastados:
                        return pd.Series({
                            'Status': 'Afastado (Suspenso)',
                            'Entra_Carga': False,
                            'Dias_Pagar': 0,
                            'Valor_Final': 0.0,
                            'Saldo_Proximo_Mes': 0
                        })

                    # 3. Admitido após o corte atual
                    if data_adm and data_adm > data_corte:
                        dia_admissao = int(data_adm.day)
                        dias_acumular = max(0, 30 - dia_admissao + 1)
                        return pd.Series({
                            'Status': f'Admitido pós-corte ({data_adm.strftime("%d/%m")})',
                            'Entra_Carga': False,
                            'Dias_Pagar': 0,
                            'Valor_Final': 0.0,
                            'Saldo_Proximo_Mes': saldo_retro + dias_acumular
                        })

                    # 4. Elegível
                    dias_calculados = max(0, int(dias_base_mes) + saldo_retro - faltas)
                    return pd.Series({
                        'Status': 'Elegível',
                        'Entra_Carga': True,
                        'Dias_Pagar': dias_calculados,
                        'Valor_Final': float(dias_calculados * valor_diario),
                        'Saldo_Proximo_Mes': 0
                    })

                res = df_ativos.apply(processar_regras, axis=1)
                df_final = pd.concat([df_ativos, res], axis=1)

                # EXPORTAÇÃO FINAL CONFORME LGPD (SEM EXPOR O CPF NO ARQUIVO DA TICKET)
                cols_export = ['Nome', 'Valor_Final']
                if nome_col_unidade:
                    cols_export.insert(1, nome_col_unidade)
                    
                df_envio = df_final[df_final['Entra_Carga'] == True][cols_export].rename(columns={'Valor_Final': 'Valor_Beneficio'})
                df_retidos = df_final[df_final['Entra_Carga'] == False]
                total_demitidos = len(df_final[df_final['Status'] == 'Demitido (Pago em TRCT)'])

                # ==========================================
                # PAINEL DE CARDS E MÉTRICAS
                # ==========================================
                st.markdown("---")
                st.subheader(f"📊 Somatório de Cartões e Valores — {competencia_str}")
                
                valor_total_geral = df_envio['Valor_Beneficio'].sum()
                total_cartoes_geral = len(df_envio)

                if nome_col_unidade and df_envio[nome_col_unidade].nunique() > 1:
                    unidades = df_envio[nome_col_unidade].unique()
                    cols_cards = st.columns(2 + len(unidades))
                    
                    cols_cards[0].metric(
                        "TOTAL GERAL (LOTE)",
                        f"R$ {valor_total_geral:,.2f}",
                        help=f"{total_cartoes_geral} cartões a carregar"
                    )
                    
                    for i, u in enumerate(unidades):
                        df_u = df_envio[df_envio[nome_col_unidade] == u]
                        val_u = df_u['Valor_Beneficio'].sum()
                        qtd_u = len(df_u)
                        cols_cards[i + 1].metric(
                            f"{str(u).upper()}",
                            f"R$ {val_u:,.2f}",
                            help=f"{qtd_u} colaboradores nesta unidade"
                        )

                    cols_cards[-1].metric("Demitidos Eliminados", total_demitidos)
                else:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Cartões a Carregar", total_cartoes_geral)
                    c2.metric("Valor Total do Lote", f"R$ {valor_total_geral:,.2f}")
                    c3.metric("Demitidos Eliminados", total_demitidos)
                    c4.metric("Bloqueados / Pós-Corte", len(df_retidos) - total_demitidos)

                # ==========================================
                # TABS DE EXPORTAÇÃO
                # ==========================================
                tab1, tab2, tab3 = st.tabs(["✅ Arquivos para Ticket", "🚫 Demitidos e Suspensos", "📋 Base Completa de Fechamento"])

                with tab1:
                    st.dataframe(df_envio, use_container_width=True)
                    
                    st.markdown("##### 📥 Opções de Download")
                    buf_ticket = io.BytesIO()
                    with pd.ExcelWriter(buf_ticket, engine='openpyxl') as writer:
                        df_envio.to_excel(writer, index=False)
                    st.download_button(
                        "⬇️ Baixar Lote Geral Consolidado (.xlsx)",
                        buf_ticket.getvalue(),
                        file_name=f"lote_ticket_geral_{competencia_str.replace('/', '_')}.xlsx"
                    )

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
                                file_name=f"ticket_{str(un).lower().replace(' ', '_')}_{competencia_str.replace('/', '_')}.xlsx"
                            )

                with tab2:
                    st.caption("Colaboradores que não entrarão no arquivo de carga da Ticket:")
                    cols_ret = ['Nome', 'CPF', 'Status', 'Saldo_Proximo_Mes']
                    if nome_col_unidade:
                        cols_ret.insert(1, nome_col_unidade)
                    st.dataframe(df_retidos[cols_ret], use_container_width=True)

                with tab3:
                    cols_completo = [c for c in df_final.columns if c != 'CPF_Clean']
                    st.dataframe(df_final[cols_completo], use_container_width=True)
                    buf_completo = io.BytesIO()
                    with pd.ExcelWriter(buf_completo, engine='openpyxl') as writer:
                        df_final[cols_completo].to_excel(writer, index=False)
                    st.download_button(
                        "⬇️ Baixar Relatório Completo de Fechamento (.xlsx)",
                        buf_completo.getvalue(),
                        file_name=f"fechamento_completo_{competencia_str.replace('/', '_')}.xlsx",
                        help="Guarde este arquivo! Ele servirá de base para a consulta de histórico no próximo mês."
                    )

        except Exception as e:
            st.error(f"Erro no processamento dos dados: {e}")

# --------------------------------------------------------------------------
# MÓDULO 2: CONSULTA DE HISTÓRICO
# --------------------------------------------------------------------------
else:
    st.markdown("### 📂 Consulta & Auditoria de Fechamentos Anteriores")
    st.info("Suba aqui o arquivo `fechamento_completo_XX_XXXX.xlsx` baixado no mês anterior para auditar valores pagos, faltas e saldos retidos.")
    
    file_historico = st.file_uploader("Selecione o arquivo de fechamento completo do mês anterior (.xlsx)", type=["xlsx"])
    
    if file_historico is not None:
        try:
            df_hist = pd.read_excel(file_historico)
            df_hist.columns = [c.strip() for c in df_hist.columns]
            
            col_unid_hist = [c for c in df_hist.columns if c.lower() in ['unidade', 'filial', 'cnpj', 'empresa']]
            nome_unid_hist = col_unid_hist[0] if col_unid_hist else None
            
            df_hist_pagos = df_hist[df_hist.get('Entra_Carga', True) == True]
            valor_pago_hist = df_hist_pagos['Valor_Final'].sum() if 'Valor_Final' in df_hist_pagos.columns else (df_hist_pagos['Valor_Beneficio'].sum() if 'Valor_Beneficio' in df_hist_pagos.columns else 0.0)
            
            st.markdown("#### 📈 Visão Geral do Fechamento Consultado")
            ch1, ch2, ch3, ch4 = st.columns(4)
            ch1.metric("Colaboradores Processados", len(df_hist))
            ch2.metric("Cartões Creditados", len(df_hist_pagos))
            ch3.metric("Total Financeiro Pago", f"R$ {valor_pago_hist:,.2f}")
            
            df_com_saldo = df_hist[df_hist.get('Saldo_Proximo_Mes', 0) > 0] if 'Saldo_Proximo_Mes' in df_hist.columns else pd.DataFrame()
            ch4.metric("Colaboradores com Saldo Retido", len(df_com_saldo))
            
            if nome_unid_hist and df_hist_pagos[nome_unid_hist].nunique() > 1:
                st.markdown("##### 🏢 Totais por Unidade no Histórico:")
                cols_un = st.columns(df_hist_pagos[nome_unid_hist].nunique())
                for idx, u in enumerate(df_hist_pagos[nome_unid_hist].unique()):
                    sub_u = df_hist_pagos[df_hist_pagos[nome_unid_hist] == u]
                    v_u = sub_u['Valor_Final'].sum() if 'Valor_Final' in sub_u.columns else 0.0
                    cols_un[idx].metric(f"{str(u).upper()}", f"R$ {v_u:,.2f}", help=f"{len(sub_u)} cartões")
            
            st.markdown("---")
            st.subheader("🔍 Localizar Colaborador no Histórico")
            termo_busca = st.text_input("Digite o CPF ou Nome para pesquisar:")
            
            if termo_busca:
                termo = termo_busca.strip().lower()
                resultado = df_hist[
                    df_hist['CPF'].astype(str).str.lower().str.contains(termo, na=False) |
                    df_hist['Nome'].astype(str).str.lower().str.contains(termo, na=False)
                ]
                if not resultado.empty:
                    st.success(f"Encontrado(s) {len(resultado)} registro(s):")
                    cols_show = ['CPF', 'Nome', 'Status', 'Faltas', 'Valor_Final', 'Saldo_Proximo_Mes']
                    cols_validas = [c for c in cols_show if c in resultado.columns]
                    st.dataframe(resultado[cols_validas], use_container_width=True)
                else:
                    st.warning("Nenhum colaborador encontrado com os dados informados.")

            if not df_com_saldo.empty:
                st.markdown("---")
                st.subheader("🎁 Saldo Retido Identificado (Admissões Pós-Corte)")
                st.caption("Estes colaboradores devem ter seus dias acumulados somados na base do fechamento deste mês:")
                cols_saldo = ['CPF', 'Nome', 'Data_Admissao', 'Saldo_Proximo_Mes']
                if nome_unid_hist:
                    cols_saldo.insert(2, nome_unid_hist)
                st.dataframe(df_com_saldo[cols_saldo], use_container_width=True)

        except Exception as e:
            st.error(f"Não foi possível ler o arquivo de histórico: {e}")
