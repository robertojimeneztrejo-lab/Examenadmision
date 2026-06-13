# pages/2_practica.py
import time
import streamlit as st
from data.temario import TEMARIO, materias_por_area, subtemas_de
from utils.supabase_client import (
    obtener_preguntas,
    insertar_preguntas,
    crear_sesion,
    finalizar_sesion,
    guardar_respuesta,
    actualizar_dominio,
)
from utils.gemini_client import generar_preguntas, generar_retroalimentacion
from utils.helpers import seleccionar_aleatorias, calcular_aciertos

st.set_page_config(page_title="Práctica - EXANI-II Prep", page_icon="📝", layout="wide")

if "usuario_id" not in st.session_state:
    st.warning("Inicia sesión desde la página principal.")
    st.stop()

usuario_id = st.session_state["usuario_id"]
area = st.session_state["area"]

st.title("📝 Práctica por bloques")

# ---------------------------------------------------------
# Estado del bloque actual
# ---------------------------------------------------------
if "bloque_activo" not in st.session_state:
    st.session_state["bloque_activo"] = False
if "preguntas_bloque" not in st.session_state:
    st.session_state["preguntas_bloque"] = []
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}
if "sesion_id" not in st.session_state:
    st.session_state["sesion_id"] = None
if "bloque_terminado" not in st.session_state:
    st.session_state["bloque_terminado"] = False
if "retroalimentacion" not in st.session_state:
    st.session_state["retroalimentacion"] = None
if "tiempo_inicio_bloque" not in st.session_state:
    st.session_state["tiempo_inicio_bloque"] = None


def iniciar_bloque(materia, subtema):
    with st.spinner("Preparando tu bloque de preguntas..."):
        preguntas = obtener_preguntas(materia, subtema, area, limite=10)

        if len(preguntas) < 10:
            faltan = 10 - len(preguntas)
            nuevas = generar_preguntas(materia, subtema, n=max(faltan, 5), dificultad=1, area=area)
            insertadas = insertar_preguntas(nuevas)
            if insertadas:
                preguntas.extend(insertadas)

        seleccionadas = seleccionar_aleatorias(preguntas, 10)

        sesion = crear_sesion(usuario_id, materia, subtema, num_preguntas=len(seleccionadas))

        st.session_state["preguntas_bloque"] = seleccionadas
        st.session_state["sesion_id"] = sesion["id"] if sesion else None
        st.session_state["respuestas_usuario"] = {}
        st.session_state["bloque_activo"] = True
        st.session_state["bloque_terminado"] = False
        st.session_state["retroalimentacion"] = None
        st.session_state["materia_actual"] = materia
        st.session_state["subtema_actual"] = subtema
        st.session_state["tiempo_inicio_bloque"] = time.time()


def reiniciar_estado():
    st.session_state["bloque_activo"] = False
    st.session_state["preguntas_bloque"] = []
    st.session_state["respuestas_usuario"] = {}
    st.session_state["sesion_id"] = None
    st.session_state["bloque_terminado"] = False
    st.session_state["retroalimentacion"] = None
    st.session_state["tiempo_inicio_bloque"] = None


# ---------------------------------------------------------
# Selección de materia y subtema (solo si no hay bloque activo)
# ---------------------------------------------------------
if not st.session_state["bloque_activo"]:
    materias_disponibles = materias_por_area(area)

    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox("Materia", materias_disponibles)
    with col2:
        subtema = st.selectbox("Subtema", subtemas_de(materia))

    if st.button("Comenzar bloque de 10 preguntas", type="primary"):
        iniciar_bloque(materia, subtema)
        st.rerun()

# ---------------------------------------------------------
# Mostrar bloque activo
# ---------------------------------------------------------
elif st.session_state["bloque_activo"] and not st.session_state["bloque_terminado"]:
    preguntas = st.session_state["preguntas_bloque"]
    materia = st.session_state["materia_actual"]
    subtema = st.session_state["subtema_actual"]

    st.subheader(f"{materia} — {subtema}")
    st.caption(f"{len(preguntas)} preguntas en este bloque")

    with st.form("form_bloque"):
        for i, p in enumerate(preguntas):
            st.markdown(f"**{i+1}. {p['pregunta']}**")
            opciones = {
                "A": p["opcion_a"],
                "B": p["opcion_b"],
                "C": p["opcion_c"],
                "D": p["opcion_d"],
            }
            opciones_texto = [f"{k}) {v}" for k, v in opciones.items()]

            seleccion = st.radio(
                f"Respuesta {i+1}",
                options=list(opciones.keys()),
                format_func=lambda k, opc=opciones: f"{k}) {opc[k]}",
                key=f"pregunta_{p['id']}",
                index=None,
                label_visibility="collapsed",
            )
            st.session_state["respuestas_usuario"][p["id"]] = seleccion
            st.divider()

        enviar = st.form_submit_button("Terminar bloque y ver retroalimentación", type="primary")

    if enviar:
        sin_responder = [
            i + 1 for i, p in enumerate(preguntas)
            if st.session_state["respuestas_usuario"].get(p["id"]) is None
        ]
        if sin_responder:
            st.warning(f"Tienes preguntas sin responder: {sin_responder}. Puedes enviarlas igual o completarlas.")

        tiempo_total = time.time() - st.session_state["tiempo_inicio_bloque"]
        tiempo_promedio = tiempo_total / len(preguntas)

        aciertos, errores = calcular_aciertos(st.session_state["respuestas_usuario"], preguntas)

        # Guardar respuestas individuales
        for p in preguntas:
            resp = st.session_state["respuestas_usuario"].get(p["id"])
            es_correcta = resp == p["respuesta_correcta"]
            guardar_respuesta(
                st.session_state["sesion_id"], p["id"], resp or "", es_correcta, tiempo_promedio
            )

        # Finalizar sesión
        finalizar_sesion(st.session_state["sesion_id"], aciertos)

        # Actualizar dominio
        actualizar_dominio(usuario_id, materia, subtema, len(preguntas), aciertos)

        # Generar retroalimentación con Gemini (solo errores)
        with st.spinner("Generando retroalimentación personalizada..."):
            retro = generar_retroalimentacion(errores)

        st.session_state["aciertos_bloque"] = aciertos
        st.session_state["total_bloque"] = len(preguntas)
        st.session_state["retroalimentacion"] = retro
        st.session_state["bloque_terminado"] = True
        st.rerun()

# ---------------------------------------------------------
# Mostrar resultados y retroalimentación
# ---------------------------------------------------------
elif st.session_state["bloque_terminado"]:
    aciertos = st.session_state["aciertos_bloque"]
    total = st.session_state["total_bloque"]
    materia = st.session_state["materia_actual"]
    subtema = st.session_state["subtema_actual"]

    st.subheader("Resultados del bloque")
    st.metric("Aciertos", f"{aciertos} / {total}", f"{round(aciertos/total*100, 1)}%")

    st.markdown("### Retroalimentación")
    st.markdown(st.session_state["retroalimentacion"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Otro bloque de 10 preguntas (mismo tema)", type="primary"):
            iniciar_bloque(materia, subtema)
            st.rerun()
    with col2:
        if st.button("Finalizar y elegir otro tema"):
            reiniciar_estado()
            st.rerun()
