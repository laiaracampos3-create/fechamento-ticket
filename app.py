import streamlit as st
import pandas as pd
from datetime import datetime, date
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
            white-space: nowrap;
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

        /* Estilização Executiva dos Cards da Sidebar */
        .param-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            margin: 14px 0 18px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
            border-left: 4px solid #16a34a;
        }}
        .param-item {{
            margin-bottom: 12px;
        }}
        .param-item:last-child {{
            margin-bottom: 0px;
        }}
        .param-label {{
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 4px;
        }}
        .param-value {{
            font-size: 13px;
            font-weight: 600;
            color: #0f172a;
            background: #f8fafc;
            padding: 6px 10px;
            border-radius: 6px;
            display: inline-block;
            border: 1px solid #f1f5f9;
        }}

        .total-box {{
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 14px 16px;
            text-align: center;
            margin-top: 15px;
        }}
        .total-label {{
            font-size: 11px;
            font-weight: 700;
            color: #15803d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .total-value {{
            font-size: 24px;
            font-weight: 800;
            color: #166534;
            margin-top: 2px;
        }}

        /* Métricas e Botões */
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
# COMPETÊNCIAS PRÉ-DEFINIDAS (D-1 PARA FALTAS)
# ==========================================
hoje = date.today()
ANO_VIGENTE = hoje.year

# Mapeamento atualizado para D-1 (Apenas 1 mês anterior para o período do ponto)
CONFIG_COMPETENCIAS = {
    f"01/01/{ANO_VIGENTE}": f"16/11/{ANO_VIGENTE-1} a 15/12/{ANO_VIGENTE-1}",
    f"01/02/{ANO_VIGENTE}": f"16/12/{ANO_VIGENTE-1} a 15/01/{ANO_VIGENTE}",
    f"01/03/{ANO_VIGENTE}": f"16/01/{ANO_VIGENTE} a 15/02/{ANO_VIGENTE}",
    f"01/04/{ANO_VIGENTE}": f"16/02/{ANO_VIGENTE} a 15/03/{ANO_VIGENTE}",
    f"01/05/{ANO_VIGENTE}": f"16/03/{ANO_VIGENTE} a 15/04/{ANO_VIGENTE}",
    f"01/06/{ANO_VIGENTE}": f"16/04/{ANO_VIGENTE} a 15/05/{ANO_VIGENTE}",
    f"01/07/{ANO_VIGENTE}": f"16/05/{ANO_VIGENTE} a 15/0
