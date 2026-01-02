import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Transparencia Presupuestaria – Santa Cruz", layout="wide")

@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]

    money_cols = [
        "Crédito Inicial","Crédito Vigente","Compromiso Consumido",
        "Devengado Consumido","Pagado","Disponible Gastar"
    ]
    for c in money_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    return df

st.sidebar.title("Filtros")

uploaded = st.sidebar.file_uploader("Cargar Excel actualizado (.xlsx)", type=["xlsx"])
default_path = "cr_30_12_25_1_12.xlsx"

if uploaded:
    df = load_data(uploaded)
    fuente = "Archivo cargado manualmente"
else:
    df = load_data(default_path)
    fuente = f"Archivo por defecto: {default_path}"

st.sidebar.caption(f"Fuente: {fuente}")

metric_col = "Devengado Consumido"

levels = [
    "Jurisdicción Desc.",
    "Entidad Desc.",
    "Servicio Administrativo Financiero Desc.",
    "Programa Desc.",
    "Inciso Desc."
]

max_level = st.sidebar.slider("Nivel de detalle", 1, len(levels), 3)
path = levels[:max_level]

st.title("Transparencia Presupuestaria – Provincia de Santa Cruz")
st.caption("Ejecución acumulada – métrica por defecto: Devengado")

total = df[metric_col].sum()
credito = df["Crédito Vigente"].sum()

c1, c2 = st.columns(2)
c1.metric("Devengado acumulado", f"${total:,.0f}")
c2.metric("Crédito vigente", f"${credito:,.0f}")

st.divider()

agg = df.groupby(path, dropna=False)[metric_col].sum().reset_index()
for c in path:
    agg[c] = agg[c].fillna("Sin dato")

fig = px.treemap(
    agg,
    path=path,
    values=metric_col,
    hover_data={metric_col:":,.0f"}
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Ranking por SAF")
rank = (
    df.groupby("Servicio Administrativo Financiero Desc.")[metric_col]
    .sum()
    .reset_index()
    .sort_values(metric_col, ascending=False)
    .head(30)
)

rank.columns = ["SAF", "Devengado"]
rank["Devengado"] = rank["Devengado"].map(lambda x: f"${x:,.0f}")
st.dataframe(rank, use_container_width=True, hide_index=True)

st.download_button(
    "Descargar ranking (CSV)",
    data=rank.to_csv(index=False).encode("utf-8-sig"),
    file_name="ranking_saf_devengado.csv",
    mime="text/csv"
)

st.divider()

st.subheader("Detalle filtrado")
cols = [
    "Jurisdicción Desc.","Entidad Desc.",
    "Servicio Administrativo Financiero Desc.",
    "Programa Desc.","Inciso Desc.",
    "Crédito Vigente","Devengado Consumido","Pagado"
]
cols = [c for c in cols if c in df.columns]

detalle = df[cols]
st.dataframe(detalle, use_container_width=True)

st.download_button(
    "Descargar detalle (CSV)",
    data=detalle.to_csv(index=False).encode("utf-8-sig"),
    file_name="detalle_ejecucion.csv",
    mime="text/csv"
)
