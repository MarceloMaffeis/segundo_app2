import streamlit as st
import pandas as pd

# Configuração da página da aplicação
st.set_page_config(
    page_title="Simulador de Custos e Orçamento",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# 1. BASE DE DADOS INTERNA (Mock Corporativo)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados() -> pd.DataFrame:
    dados = [
        {"Item": "Aço e Chapas Estruturais", "Categoria": "Matéria-Prima", "Valor (R$)": 8500.0, "Prioridade": "Alta"},
        {"Item": "Componentes de Fixação", "Categoria": "Matéria-Prima", "Valor (R$)": 1400.0, "Prioridade": "Média"},
        {"Item": "Operação de Linha (Horas-Homem)", "Categoria": "Mão de Obra", "Valor (R$)": 6200.0, "Prioridade": "Alta"},
        {"Item": "Supervisão Técnica", "Categoria": "Mão de Obra", "Valor (R$)": 3100.0, "Prioridade": "Média"},
        {"Item": "Frete Interestadual de Cargas", "Categoria": "Logística", "Valor (R$)": 2900.0, "Prioridade": "Alta"},
        {"Item": "Armazenamento Terceirizado", "Categoria": "Logística", "Valor (R$)": 1200.0, "Prioridade": "Baixa"},
        {"Item": "Consumo Elétrico Maquinário", "Categoria": "Energia", "Valor (R$)": 2400.0, "Prioridade": "Alta"},
        {"Item": "Gerador de Backup (Óleo)", "Categoria": "Energia", "Valor (R$)": 800.0, "Prioridade": "Baixa"},
        {"Item": "Insertos e Ferramental de Corte", "Categoria": "Ferramentas", "Valor (R$)": 1950.0, "Prioridade": "Média"},
        {"Item": "Instrumentos de Metrologia", "Categoria": "Ferramentas", "Valor (R$)": 1150.0, "Prioridade": "Alta"},
    ]
    return pd.DataFrame(dados)

df_original = carregar_dados()

# ---------------------------------------------------------
# 2. BARRA LATERAL (Sidebar - Filtros e Entradas)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parâmetros de Simulação")

# Controle do Orçamento Disponível
orcamento_disponivel = st.sidebar.slider(
    label="Orçamento Total Disponível (R$)",
    min_value=5000,
    max_value=50000,
    value=20000,
    step=500,
    format="R$ %d"
)

# Seleção de Categorias
categorias_disponiveis = df_original["Categoria"].unique().tolist()
categorias_selecionadas = st.sidebar.multiselect(
    label="Filtrar por Categoria:",
    options=categorias_disponiveis,
    default=categorias_disponiveis
)

# ---------------------------------------------------------
# 3. FILTRAGEM E CÁLCULOS DINÂMICOS
# ---------------------------------------------------------
if categorias_selecionadas:
    df_filtrado = df_original[df_original["Categoria"].isin(categorias_selecionadas)]
else:
    df_filtrado = pd.DataFrame(columns=df_original.columns)

total_gasto = df_filtrado["Valor (R$)"].sum()
saldo_restante = orcamento_disponivel - total_gasto

# ---------------------------------------------------------
# 4. ÁREA PRINCIPAL
# ---------------------------------------------------------
st.title("📊 Simulador de Custos e Orçamento")
st.caption("Ferramenta gerencial para acompanhamento orçamentário dinâmico e tomada de decisão.")

# Métricas de topo (KPIs)
col1, col2, col3 = st.columns(3)

col1.metric(
    label="Orçamento Definido",
    value=f"R$ {orcamento_disponivel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

col2.metric(
    label="Gasto Filtrado",
    value=f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

col3.metric(
    label="Saldo Restante",
    value=f"R$ {saldo_restante:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    delta=f"R$ {saldo_restante:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Alerta condicional de meta orçamentária
if total_gasto <= orcamento_disponivel:
    st.success(
        f"✅ **Projeto dentro da meta orçamentária!** Você ainda possui "
        f"**R$ {saldo_restante:,.2f}** disponíveis para alocação."
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )
else:
    excedente = abs(saldo_restante)
    st.error(
        f"🚨 **Atenção: Limite orçamentário ultrapassado!** Os custos excederam o limite em "
        f"**R$ {excedente:,.2f}**. Revise os itens ou renegocie o aporte."
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )

st.markdown("---")

# Visualização de dados: Gráfico e Tabela
col_grafico, col_tabela = st.columns([1, 1])

with col_grafico:
    st.subheader("Custos por Categoria")
    if not df_filtrado.empty:
        # Agrupamento para gráfico horizontal nativo do Streamlit (sem dependências extras)
        df_categoria = (
            df_filtrado.groupby("Categoria")["Valor (R$)"]
            .sum()
            .reset_index()
            .set_index("Categoria")
        )
        st.bar_chart(df_categoria, horizontal=True)
    else:
        st.info("Nenhuma categoria selecionada para exibir o gráfico.")

with col_tabela:
    st.subheader("Detalhamento dos Itens")
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valor (R$)": st.column_config.NumberColumn(
                    "Valor (R$)",
                    format="R$ %.2f"
                )
            }
        )
    else:
        st.warning("Selecione pelo menos uma categoria no menu lateral para visualizar as despesas.")
