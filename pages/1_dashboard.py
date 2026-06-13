# pages/1_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.supabase_client import obtener_dominio, obtener_dominio_general, obtener_actividad
from utils.helpers import procesar_actividad, DIAS_SEMANA_ES

st.set_page_config(page_title="Dashboard - EXANI-II Prep", page_icon="📊", layout="wide")
st.sidebar.image("assets/logo.jpg", width=100)

if "usuario_id" not in st.session_state:
    st.warning("Inicia sesión desde la página principal.")
    st.stop()

st.title("📊 Mi Dashboard")

usuario_id = st.session_state["usuario_id"]

# ---------------------------------------------------------
# Dominio general
# ---------------------------------------------------------
dominio_general = obtener_dominio_general(usuario_id)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Dominio general", f"{dominio_general}%")
    st.progress(min(int(dominio_general), 100) / 100)

# ---------------------------------------------------------
# Dominio por materia / subtema
# ---------------------------------------------------------
st.subheader("Dominio por tema")

dominio_data = obtener_dominio(usuario_id)

if not dominio_data:
    st.info("Aún no tienes datos de práctica. ¡Resuelve tu primer bloque de preguntas!")
else:
    df = pd.DataFrame(dominio_data)
    df = df.sort_values(["materia", "porcentaje_dominio"])

    fig = px.bar(
        df,
        x="porcentaje_dominio",
        y="subtema",
        color="materia",
        orientation="h",
        text="porcentaje_dominio",
        labels={"porcentaje_dominio": "Dominio (%)", "subtema": "Subtema", "materia": "Materia"},
        height=max(400, len(df) * 28),
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(xaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabla de detalle"):
        st.dataframe(
            df[["materia", "subtema", "total_respondidas", "total_correctas", "porcentaje_dominio"]],
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------
# Actividad de estudio (días y horas)
# ---------------------------------------------------------
st.subheader("Actividad de estudio")

actividad_raw = obtener_actividad(usuario_id)

if not actividad_raw:
    st.info("Aún no tienes sesiones completadas.")
else:
    procesada = procesar_actividad(actividad_raw)
    df_act = pd.DataFrame(procesada)

    # Heatmap día de la semana x hora
    pivot = (
        df_act.groupby(["dia", "hora"])["minutos"]
        .sum()
        .reset_index()
    )

    orden_dias = list(DIAS_SEMANA_ES.values())
    pivot["dia"] = pd.Categorical(pivot["dia"], categories=orden_dias, ordered=True)

    fig2 = px.density_heatmap(
        pivot,
        x="hora",
        y="dia",
        z="minutos",
        category_orders={"dia": orden_dias},
        labels={"hora": "Hora del día", "dia": "Día de la semana", "minutos": "Minutos de estudio"},
        color_continuous_scale="Blues",
        height=400,
    )
    fig2.update_xaxes(dtick=1, range=[0, 23])
    st.plotly_chart(fig2, use_container_width=True)

    # Resumen por día (barras)
    resumen_dia = df_act.groupby("dia")["minutos"].sum().reindex(orden_dias, fill_value=0).reset_index()
    fig3 = px.bar(
        resumen_dia,
        x="dia",
        y="minutos",
        labels={"dia": "Día de la semana", "minutos": "Minutos totales"},
        text_auto=".0f",
    )
    st.plotly_chart(fig3, use_container_width=True)
