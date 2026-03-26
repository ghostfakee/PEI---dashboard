import warnings
warnings.filterwarnings('ignore')

import openpyxl
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(page_title="Agro Inteligente — SLCE3", layout="wide")

@st.cache_data
def load_data():
    wb = openpyxl.load_workbook('dados.xlsx', read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data').reset_index(drop=True)
    num_cols = [
        'preco_abertura','preco_maximo','preco_minimo','preco_fechamento',
        'volume','retorno_diario','media_movel_7d','temperatura_media',
        'temperatura_maxima','temperatura_minima','precipitacao_mm',
        'velocidade_vento','chuva_acumulada_7d','precipitacao_lag_7d'
    ]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    df['drawdown'] = ((df['preco_fechamento'] - df['preco_fechamento'].cummax()) / df['preco_fechamento'].cummax() * 100).round(4)
    df['volatilidade_7d'] = df['retorno_diario'].rolling(7).std() * 100
    df['nome_mes'] = df['mes'].map({1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun'})
    return df

df = load_data()

VARS_CLIMA = {
    'temperatura_media':   'Temperatura Média (°C)',
    'temperatura_maxima':  'Temperatura Máxima (°C)',
    'temperatura_minima':  'Temperatura Mínima (°C)',
    'precipitacao_mm':     'Precipitação Diária (mm)',
    'chuva_acumulada_7d':  'Chuva Acumulada 7d (mm)',
    'precipitacao_lag_7d': 'Precipitação Lag 7d (mm)',
    'velocidade_vento':    'Velocidade do Vento (km/h)',
}

MESES = {0:'Todos', 1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun'}

with st.sidebar:
    st.markdown("**Agro Inteligente — SLCE3**")
    st.caption("SLC Agrícola S.A. · Sorriso, MT · UniVag")
    st.divider()
    pagina = st.radio("Página", ["Visão Geral", "Análise Climática", "Correlações", "Dados Brutos"])
    st.divider()
    st.markdown("**Filtro por mês**")
    mes_sel = st.selectbox("Mês", list(MESES.keys()), format_func=lambda x: MESES[x])
    st.divider()
    st.caption("UniVag · 6º Sem. EN. Software · 2023/2")
    st.caption("Lucas Lellis · Gabriel Pires · Hannah Pompeu")

df_v = df if mes_sel == 0 else df[df['mes'] == mes_sel].copy()

if len(df_v) < 2:
    st.warning("Sem dados para o mês selecionado.")
    st.stop()

mensal = df.groupby('mes').agg(
    nome_mes=('nome_mes','first'),
    preco_medio=('preco_fechamento','mean'),
    volume_total=('volume','sum'),
    precip_total=('precipitacao_mm','sum'),
    temp_media=('temperatura_media','mean'),
    drawdown_medio=('drawdown','mean')
).reset_index()

H = 320

# ── VISÃO GERAL ───────────────────────────────────────────
if pagina == "Visão Geral":
    st.title("Visão Geral — SLCE3")
    periodo = MESES[mes_sel] if mes_sel != 0 else "Jan–Jun 2025"
    st.caption(f"{periodo} · {len(df_v)} pregões")

    variacao = ((df_v.iloc[-1]['preco_fechamento'] / df_v.iloc[0]['preco_fechamento']) - 1) * 100
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Preço Final",  f"R$ {df_v.iloc[-1]['preco_fechamento']:.2f}")
    c2.metric("Variação",     f"{variacao:+.2f}%", delta=f"{variacao:+.2f}%")
    c3.metric("Max Drawdown", f"{df_v['drawdown'].min():.2f}%")
    c4.metric("Volatilidade", f"{df_v['retorno_diario'].std()*100:.2f}%")
    c5.metric("Melhor Dia",   f"{df_v['retorno_diario'].max()*100:+.2f}%")
    c6.metric("Pior Dia",     f"{df_v['retorno_diario'].min()*100:+.2f}%")

    # Preço + MM7
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
        name='Fechamento', line=dict(width=2, color='#1f77b4')))
    fig1.add_trace(go.Scatter(x=df_v['data'], y=df_v['media_movel_7d'],
        name='MM 7d', line=dict(dash='dash', width=1.5, color='#2ca02c')))
    fig1.update_layout(title='Preço de Fechamento e Média Móvel 7d',
        hovermode='x unified', height=H, xaxis_title='', yaxis_title='R$')
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        cores = ['#2ca02c' if v >= 0 else '#d62728' for v in df_v['retorno_diario'].fillna(0)]
        fig2 = go.Figure(go.Bar(x=df_v['data'], y=df_v['retorno_diario']*100, marker_color=cores))
        fig2.update_layout(title='Retorno Diário (%)', height=H, xaxis_title='', yaxis_title='%')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = go.Figure(go.Scatter(x=df_v['data'], y=df_v['drawdown'],
            fill='tozeroy', line=dict(color='#d62728', width=2),
            fillcolor='rgba(214,39,40,0.1)', name='Drawdown'))
        fig3.update_layout(title='Drawdown Acumulado (%)', height=H, xaxis_title='', yaxis_title='%')
        st.plotly_chart(fig3, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig4 = px.bar(mensal, x='nome_mes', y='volume_total',
            title='Volume Total por Mês',
            labels={'nome_mes':'Mês','volume_total':'Volume'})
        fig4.update_layout(height=H)
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        fig5 = px.bar(mensal, x='nome_mes', y='preco_medio',
            title='Preço Médio de Fechamento por Mês',
            labels={'nome_mes':'Mês','preco_medio':'R$'})
        fig5.update_layout(height=H)
        st.plotly_chart(fig5, use_container_width=True)

# ── ANÁLISE CLIMÁTICA ─────────────────────────────────────
elif pagina == "Análise Climática":
    st.title("Análise Climática")
    periodo = MESES[mes_sel] if mes_sel != 0 else "Jan–Jun 2025"
    st.caption(f"{periodo} · Sorriso, MT")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Temp. Média",        f"{df_v['temperatura_media'].mean():.1f}°C")
    c2.metric("Temp. Máxima",       f"{df_v['temperatura_maxima'].max():.1f}°C")
    c3.metric("Precipitação Total", f"{df_v['precipitacao_mm'].sum():.0f} mm")
    c4.metric("Precip. Média/Dia",  f"{df_v['precipitacao_mm'].mean():.1f} mm")

    # Seletor de variável climática
    var_sel = st.selectbox("Variável climática para comparar com o preço",
        list(VARS_CLIMA.keys()), format_func=lambda x: VARS_CLIMA[x])

    fig6 = make_subplots(specs=[[{'secondary_y': True}]])
    fig6.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
        name='Preço', line=dict(width=2, color='#1f77b4')), secondary_y=False)
    fig6.add_trace(go.Scatter(x=df_v['data'], y=df_v[var_sel],
        name=VARS_CLIMA[var_sel], line=dict(width=1.5, color='#ff7f0e')), secondary_y=True)
    fig6.update_layout(title=f'{VARS_CLIMA[var_sel]} vs Preço de Fechamento',
        hovermode='x unified', height=H)
    fig6.update_yaxes(title_text='Preço (R$)', secondary_y=False)
    fig6.update_yaxes(title_text=VARS_CLIMA[var_sel], secondary_y=True)
    st.plotly_chart(fig6, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # Precipitação + Chuva Acumulada vs Preço
        fig7 = make_subplots(specs=[[{'secondary_y': True}]])
        fig7.add_trace(go.Scatter(x=df_v['data'], y=df_v['preco_fechamento'],
            name='Preço', line=dict(width=2, color='#1f77b4')), secondary_y=False)
        fig7.add_trace(go.Bar(x=df_v['data'], y=df_v['precipitacao_mm'],
            name='Precipitação (mm)', marker_color='rgba(31,119,180,0.3)'), secondary_y=True)
        fig7.add_trace(go.Scatter(x=df_v['data'], y=df_v['chuva_acumulada_7d'],
            name='Chuva Acum. 7d', line=dict(dash='dot', color='#2ca02c', width=1.5)), secondary_y=True)
        fig7.update_layout(title='Precipitação vs Preço', hovermode='x unified', height=H)
        fig7.update_yaxes(title_text='Preço (R$)', secondary_y=False)
        fig7.update_yaxes(title_text='mm', secondary_y=True)
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        # Dispersão com tendência
        sub = df_v[[var_sel,'preco_fechamento']].dropna()
        if len(sub) > 2:
            x, y = sub[var_sel].values, sub['preco_fechamento'].values
            m, b = np.polyfit(x, y, 1)
            xl = np.linspace(x.min(), x.max(), 100)
            fig8 = px.scatter(sub, x=var_sel, y='preco_fechamento',
                labels={var_sel: VARS_CLIMA[var_sel], 'preco_fechamento':'Preço (R$)'},
                title=f'Dispersão: {VARS_CLIMA[var_sel].split("(")[0].strip()} × Preço')
            fig8.add_trace(go.Scatter(x=xl, y=m*xl+b, mode='lines', name='Tendência',
                line=dict(color='black', dash='dash', width=1.5)))
            fig8.update_layout(height=H)
            st.plotly_chart(fig8, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig9 = px.bar(mensal, x='nome_mes', y='temp_media',
            title='Temperatura Média por Mês (°C)',
            labels={'nome_mes':'Mês','temp_media':'°C'})
        fig9.update_layout(height=H)
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        fig10 = px.bar(mensal, x='nome_mes', y='precip_total',
            title='Precipitação Total por Mês (mm)',
            labels={'nome_mes':'Mês','precip_total':'mm'})
        fig10.update_layout(height=H)
        st.plotly_chart(fig10, use_container_width=True)

    # Volatilidade vs Chuva
    fig11 = make_subplots(specs=[[{'secondary_y': True}]])
    fig11.add_trace(go.Scatter(x=df_v['data'], y=df_v['volatilidade_7d'],
        name='Volatilidade 7d (%)', line=dict(color='#ff7f0e', width=2)), secondary_y=False)
    fig11.add_trace(go.Scatter(x=df_v['data'], y=df_v['chuva_acumulada_7d'],
        name='Chuva Acum. 7d (mm)', line=dict(color='#1f77b4', dash='dot', width=1.5)), secondary_y=True)
    fig11.update_layout(title='Volatilidade 7d vs Chuva Acumulada — Clima × Risco',
        hovermode='x unified', height=H)
    fig11.update_yaxes(title_text='Volatilidade (%)', secondary_y=False)
    fig11.update_yaxes(title_text='Chuva (mm)', secondary_y=True)
    st.plotly_chart(fig11, use_container_width=True)

# ── CORRELAÇÕES ───────────────────────────────────────────
elif pagina == "Correlações":
    st.title("Correlações de Pearson — Clima × Mercado")
    st.caption("Quantificação estatística do impacto climático no SLCE3")

    corr_rows = []
    for col, label in VARS_CLIMA.items():
        sub = df_v[[col,'preco_fechamento','retorno_diario']].dropna()
        if len(sub) < 5:
            continue
        r_p, p_p = stats.pearsonr(sub[col], sub['preco_fechamento'])
        r_r, _   = stats.pearsonr(sub[col], sub['retorno_diario'])
        abs_r = abs(r_p)
        forca = 'Desprezível' if abs_r<0.1 else 'Fraca' if abs_r<0.3 else 'Moderada' if abs_r<0.5 else 'Forte'
        corr_rows.append({
            'Variável': label.split('(')[0].strip(),
            'r (vs preço)': round(r_p,4),
            'r (vs retorno)': round(r_r,4),
            'p-valor': round(p_p,4),
            'Força': forca,
            'Direção': 'Positiva' if r_p>0 else 'Negativa'
        })

    df_corr = pd.DataFrame(corr_rows).sort_values('r (vs preço)', key=abs, ascending=False)
    top = df_corr.iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Maior correlação", top['Variável'])
    c2.metric("Coeficiente r",    f"{top['r (vs preço)']:+.4f}")
    c3.metric("Força",            top['Força'])
    c4.metric("p-valor",          f"{top['p-valor']:.4f}")

    df_ord = df_corr.sort_values('r (vs preço)')
    cores_bar = ['#d62728' if v < 0 else '#2ca02c' for v in df_ord['r (vs preço)']]

    col1, col2 = st.columns([3,2])
    with col1:
        fig12 = go.Figure(go.Bar(
            x=df_ord['r (vs preço)'], y=df_ord['Variável'], orientation='h',
            marker_color=cores_bar,
            text=df_ord['r (vs preço)'].apply(lambda v: f'{v:+.4f}'),
            textposition='outside'
        ))
        fig12.update_layout(title='Pearson r — Variáveis Climáticas vs Preço de Fechamento',
            xaxis=dict(range=[-0.6,0.6]), height=H)
        st.plotly_chart(fig12, use_container_width=True)

    with col2:
        st.markdown("**Tabela de correlações**")
        st.dataframe(df_corr.set_index('Variável'), use_container_width=True, height=H)

    st.markdown("---")
    st.markdown("### Respostas às Perguntas de Negócio")

    r_chuva = df_corr[df_corr['Variável'].str.contains('Precipitação Diária')]['r (vs preço)'].values
    r_lag   = df_corr[df_corr['Variável'].str.contains('Lag')]['r (vs preço)'].values
    dd_jun  = mensal[mensal['mes']==6]['drawdown_medio'].values

    itens = {
        "Variável com maior correlação": f"{top['Variável']} (r={top['r (vs preço)']}) — {top['Força']} {top['Direção']}",
        "Chuva impacta o preço?":        f"r={r_chuva[0]:+.4f} — Fraca Negativa" if len(r_chuva) else "—",
        "Efeito imediato ou com lag?":   f"r lag 7d={r_lag[0]:+.4f} — Desprezível, impacto é imediato" if len(r_lag) else "—",
        "Seca prolongada e drawdown":    f"Drawdown médio em Jun={dd_jun[0]:.1f}% (pior do semestre)" if len(dd_jun) else "—",
        "Variação total do ativo":       f"{((df_v.iloc[-1]['preco_fechamento']/df_v.iloc[0]['preco_fechamento'])-1)*100:+.2f}%",
        "Drawdown máximo":               f"{df_v['drawdown'].min():.2f}%",
        "Volatilidade diária":           f"{df_v['retorno_diario'].std()*100:.2f}%",
    }

    for k, v in itens.items():
        c1, c2 = st.columns([2,3])
        c1.markdown(f"**{k}**")
        c2.write(v)

# ── DADOS BRUTOS ──────────────────────────────────────────
elif pagina == "Dados Brutos":
    st.title("Dados Brutos")
    periodo = MESES[mes_sel] if mes_sel != 0 else "Jan–Jun 2025"
    st.caption(f"{periodo} · {len(df_v)} registros")

    col1, col2 = st.columns(2)
    with col1:
        busca = st.text_input("Buscar", placeholder="ex: Mar, Sorriso, MT")
    with col2:
        col_sel = st.multiselect("Colunas visíveis", list(df_v.columns),
            default=['data','nome_mes','preco_fechamento','retorno_diario',
                     'volume','temperatura_media','precipitacao_mm','drawdown'])

    df_tab = df_v.copy()
    if busca:
        mask = df_tab.astype(str).apply(
            lambda c: c.str.contains(busca, case=False, na=False)
        ).any(axis=1)
        df_tab = df_tab[mask]

    cols_show = [c for c in col_sel if c in df_tab.columns]
    if cols_show:
        df_tab = df_tab[cols_show]

    st.caption(f"{len(df_tab)} registros filtrados")
    st.dataframe(df_tab.reset_index(drop=True), use_container_width=True, height=480)

    csv = df_tab.to_csv(index=False).encode('utf-8')
    st.download_button("Exportar CSV", csv, "slce3_filtrado.csv", "text/csv")
