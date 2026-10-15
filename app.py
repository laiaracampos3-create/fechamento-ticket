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
            border: 1
