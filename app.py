# ==========================================
# MOTOR DE CÁLCULO DE ADMISSÃO (CORRIGIDO)
# ==========================================
def processar_regras(row):
    cpf_id = str(row['CPF_Clean'])
    data_adm = row['Data_Admissao_Clean']

    faltas = int(row.get('Faltas', 0))
    saldo_retro = int(row.get('Saldo_Retroativo_Dias', 0))

    # 1. Demitidos e Afastados
    if cpf_id in cpfs_demitidos:
        return pd.Series({'Status': 'Demitido (Pago em TRCT)', 'Entra_Carga': False, 'Dias_Pagar': 0, 'Valor_Final': 0.0, 'Saldo_Proximo_Mes': 0})
    if cpf_id in cpfs_afastados:
        return pd.Series({'Status': 'Afastado (Suspenso)', 'Entra_Carga': False, 'Dias_Pagar': 0, 'Valor_Final': 0.0, 'Saldo_Proximo_Mes': 0})

    # 2. Pós-Corte
    if data_adm and data_adm > data_corte:
        dia_admissao = int(data_adm.day)
        dias_acumular = max(0, 30 - dia_admissao + 1)
        return pd.Series({'Status': f'Admitido pós-corte ({data_adm.strftime("%d/%m/%Y")})', 'Entra_Carga': False, 'Dias_Pagar': 0, 'Valor_Final': 0.0, 'Saldo_Proximo_Mes': saldo_retro + dias_acumular})

    # 3. Regra de Admissão Proporcional vs Mês Cheio
    dias_base_direito = int(dias_base_mes) # Padrão: 30 dias (Mês Cheio)

    if data_adm:
        # Se foi admitido no mês IMEDIATAMENTE ANTERIOR ao pagamento (ex: admitido em Outubro p/ pagamento 01/11)
        if data_adm.year == dt_mes_trabalhado.year and data_adm.month == dt_mes_trabalhado.month:
            dias_base_direito = max(0, 30 - int(data_adm.day) + 1)
            status_str = f'Admitido proporcional ({data_adm.strftime("%d/%m")})'
        # Se foi admitido em meses ANTERIORES (ex: Setembro ou antes p/ pagamento 01/11)
        else:
            status_str = 'Elegível'
    else:
        status_str = 'Elegível'

    dias_calculados = max(0, dias_base_direito + saldo_retro - faltas)
    valor_pago = float(dias_calculados * valor_diario)

    return pd.Series({
        'Status': status_str,
        'Entra_Carga': True if dias_calculados > 0 else False,
        'Dias_Pagar': dias_calculados,
        'Valor_Final': valor_pago,
        'Saldo_Proximo_Mes': 0
    })
