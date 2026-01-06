
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Transparencia Presupuestaria – Santa Cruz", layout="wide")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    # Normalizar nombres
    df.columns = [c.strip() for c in df.columns]
    # Asegurar numéricos
    money_cols = [
        "Crédito Inicial","Crédito Vigente","Compromiso Consumido","Compromiso Preventivo",
        "Compromiso Res.","Devengado Consumido","Pagado","Disponible Gastar",
        "Crédito Restringido","Crédito Potencial","Devengado Res.","Pagado Financiero",
        "Disponible Devengar","Disponible Pagar","Crédito Disp.OPP"
    ]
    for c in money_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    # Campos clave (algunos pueden venir como int/float)
    key_cols = ["Jur","SJur","Ent.","Sec","SSec","Cr","SAF","Fte","UG","Pg","Sp","Py","Ac","Ob","In","Pp","Pc","SPc","Fi","Fu"]
    for c in key_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="ignore")
    return df

# --- Sidebar
st.sidebar.title("Filtros")
uploaded = st.sidebar.file_uploader("Cargar Excel actualizado (.xlsx)", type=["xlsx"])
default_path = "cr_30_12_25_1_12.xlsx"

if uploaded is not None:
    df = load_data(uploaded)
    data_label = "Archivo cargado"
else:
    df = load_data(default_path)
    data_label = f"Archivo por defecto: {default_path}"

st.sidebar.caption(f"Fuente: {data_label}")

metric_options = {
    "Devengado (por defecto)": "Devengado Consumido",
    "Pagado": "Pagado",
    "Compromiso": "Compromiso Consumido",
    "Crédito Vigente": "Crédito Vigente",
    "Crédito Inicial": "Crédito Inicial",
}
metric_name = st.sidebar.selectbox("Mostrar", list(metric_options.keys()), index=0)
metric_col = metric_options[metric_name]

# Drilldown: por defecto permitir bajar a SAF
group_levels = [
    ("Jurisdicción", "Jurisdicción Desc."),
    ("Subjurisdicción", "Subjurisdicción Desc."),
    ("Entidad", "Entidad Desc."),
    ("SAF", "Servicio Administrativo Financiero Desc."),
    ("Programa", "Programa Desc."),
    ("Inciso", "Inciso Desc."),
]
level_labels = [x[0] for x in group_levels]
level_cols = [x[1] for x in group_levels]

max_level = st.sidebar.slider("Nivel de detalle (drilldown)", 1, len(group_levels), 4)  # hasta SAF por defecto
selected_levels = level_cols[:max_level]

# Filtros por Jurisdicción / SAF (para navegación rápida)
jur_list = ["(Todas)"] + sorted(df["Jurisdicción Desc."].dropna().unique().tolist())
jur_pick = st.sidebar.selectbox("Jurisdicción", jur_list, index=0)

saf_list = ["(Todos)"] + sorted(df["Servicio Administrativo Financiero Desc."].dropna().unique().tolist())
saf_pick = st.sidebar.selectbox("SAF", saf_list, index=0)

if jur_pick != "(Todas)":
    df = df[df["Jurisdicción Desc."] == jur_pick]
if saf_pick != "(Todos)":
    df = df[df["Servicio Administrativo Financiero Desc."] == saf_pick]

# --- Header
st.title("Transparencia Presupuestaria – Provincia de Santa Cruz")
st.caption("Visualización para ciudadanía: montos y proporciones con navegación hasta SAF (y más).")

# KPIs
total = float(df[metric_col].sum())
credito_vig = float(df["Crédito Vigente"].sum()) if "Crédito Vigente" in df.columns else 0.0
pagado = float(df["Pagado"].sum()) if "Pagado" in df.columns else 0.0
col1, col2, col3 = st.columns(3)
col1.metric("Total (según métrica)", f"${total:,.0f}")
col2.metric("Crédito vigente", f"${credito_vig:,.0f}")
col3.metric("Pagado", f"${pagado:,.0f}")

st.divider()

# --- Treemap
st.subheader("Gasto en proporciones (gráfico de árbol)")
agg = df.groupby(selected_levels, dropna=False)[metric_col].sum().reset_index()
# Reemplazar NaN por "Sin dato"
for c in selected_levels:
    agg[c] = agg[c].fillna("Sin dato").astype(str)

fig = px.treemap(
    agg,
    path=selected_levels,
    values=metric_col,
    hover_data={metric_col:":,.0f"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Tabla de ranking
st.subheader("Ranking (tabla)")
top_n = st.slider("Mostrar top N", 10, 200, 30)
rank_level = st.selectbox("Agrupar por", level_labels, index=3)  # SAF por defecto
rank_col = dict(group_levels)[rank_level]
rank = (
    df.groupby(rank_col, dropna=False)[metric_col].sum()
      .reset_index()
      .rename(columns={rank_col: rank_level, metric_col: "Monto"})
      .sort_values("Monto", ascending=False)
      .head(top_n)
)
rank[rank_level] = rank[rank_level].fillna("Sin dato").astype(str)

st.dataframe(
    rank.assign(**{"Monto": rank["Monto"].map(lambda x: f"${x:,.0f}")}),
    use_container_width=True,
    hide_index=True
)

# Descarga
csv = rank.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Descargar ranking (CSV)",
    data=csv,
    file_name=f"ranking_{rank_level.lower()}_{metric_col.lower().replace(' ','_')}.csv",
    mime="text/csv"
)

st.divider()
st.subheader("Explorar detalle")
st.caption("Podés filtrar y luego ver el detalle de registros (por programa, inciso, etc.).")

# Columnas a mostrar en detalle
detail_cols = [
    "Jurisdicción Desc.","Subjurisdicción Desc.","Entidad Desc.",
    "Servicio Administrativo Financiero Desc.","Programa Desc.",
    "Inciso Desc.","Principal Desc.","Parcial Desc.",
    "Crédito Vigente","Devengado Consumido","Pagado","Disponible Gastar"
]
detail_cols = [c for c in detail_cols if c in df.columns]
detail = df[detail_cols].copy()

st.dataframe(detail, use_container_width=True)

st.download_button(
    "Descargar detalle filtrado (CSV)",
    data=detail.to_csv(index=False).encode("utf-8-sig"),
    file_name="detalle_filtrado.csv",
    mime="text/csv"
)
