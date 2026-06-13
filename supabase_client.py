# utils/supabase_client.py
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ---------------------------------------------------------
# Autenticación
# ---------------------------------------------------------
def validar_login(username: str, password: str):
    """Valida usuario/contraseña usando la función RPC validar_login.
    Devuelve dict con id, nombre, area si es correcto, o None si no.
    """
    sb = get_supabase_client()
    try:
        res = sb.rpc("validar_login", {"p_username": username, "p_password": password}).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al validar login: {e}")
        return None


def crear_usuario(nombre: str, username: str, password: str, area: str):
    """Crea un nuevo usuario usando la función RPC crear_usuario."""
    sb = get_supabase_client()
    try:
        res = sb.rpc(
            "crear_usuario",
            {"p_nombre": nombre, "p_username": username, "p_password": password, "p_area": area},
        ).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al crear usuario: {e}")
        return None


# ---------------------------------------------------------
# Preguntas
# ---------------------------------------------------------
def obtener_preguntas(materia: str, subtema: str, area: str, limite: int = 10):
    sb = get_supabase_client()
    query = (
        sb.table("preguntas")
        .select("*")
        .eq("materia", materia)
        .eq("subtema", subtema)
    )
    if area != "TODAS":
        query = query.contains("area_aplicable", [area])

    res = query.limit(limite * 3).execute()  # traemos más para poder randomizar localmente
    return res.data or []


def insertar_preguntas(preguntas: list):
    """Inserta una lista de preguntas (dicts) en la tabla preguntas."""
    sb = get_supabase_client()
    if not preguntas:
        return None
    res = sb.table("preguntas").insert(preguntas).execute()
    return res.data


# ---------------------------------------------------------
# Sesiones y respuestas
# ---------------------------------------------------------
def crear_sesion(usuario_id: str, materia: str, subtema: str, num_preguntas: int = 10):
    sb = get_supabase_client()
    res = (
        sb.table("sesiones")
        .insert({
            "usuario_id": usuario_id,
            "materia": materia,
            "subtema": subtema,
            "num_preguntas": num_preguntas,
        })
        .execute()
    )
    return res.data[0] if res.data else None


def finalizar_sesion(sesion_id: str, aciertos: int):
    sb = get_supabase_client()
    from datetime import datetime, timezone
    res = (
        sb.table("sesiones")
        .update({"hora_fin": datetime.now(timezone.utc).isoformat(), "aciertos": aciertos})
        .eq("id", sesion_id)
        .execute()
    )
    return res.data


def guardar_respuesta(sesion_id: str, pregunta_id: str, respuesta_usuario: str,
                       es_correcta: bool, tiempo_respuesta_seg: float = None):
    sb = get_supabase_client()
    res = (
        sb.table("respuestas")
        .insert({
            "sesion_id": sesion_id,
            "pregunta_id": pregunta_id,
            "respuesta_usuario": respuesta_usuario,
            "es_correcta": es_correcta,
            "tiempo_respuesta_seg": tiempo_respuesta_seg,
        })
        .execute()
    )
    return res.data


# ---------------------------------------------------------
# Dominio de temas
# ---------------------------------------------------------
def actualizar_dominio(usuario_id: str, materia: str, subtema: str,
                        respondidas: int, correctas: int):
    sb = get_supabase_client()
    # Buscar registro existente
    existente = (
        sb.table("dominio_temas")
        .select("*")
        .eq("usuario_id", usuario_id)
        .eq("materia", materia)
        .eq("subtema", subtema)
        .execute()
    )

    from datetime import datetime, timezone
    if existente.data:
        actual = existente.data[0]
        nuevas_respondidas = actual["total_respondidas"] + respondidas
        nuevas_correctas = actual["total_correctas"] + correctas
        sb.table("dominio_temas").update({
            "total_respondidas": nuevas_respondidas,
            "total_correctas": nuevas_correctas,
            "ultima_actualizacion": datetime.now(timezone.utc).isoformat(),
        }).eq("usuario_id", usuario_id).eq("materia", materia).eq("subtema", subtema).execute()
    else:
        sb.table("dominio_temas").insert({
            "usuario_id": usuario_id,
            "materia": materia,
            "subtema": subtema,
            "total_respondidas": respondidas,
            "total_correctas": correctas,
        }).execute()


def obtener_dominio(usuario_id: str):
    sb = get_supabase_client()
    res = (
        sb.table("dominio_temas")
        .select("*")
        .eq("usuario_id", usuario_id)
        .execute()
    )
    return res.data or []


def obtener_dominio_general(usuario_id: str):
    """Calcula el porcentaje de dominio general (promedio ponderado)."""
    datos = obtener_dominio(usuario_id)
    total_resp = sum(d["total_respondidas"] for d in datos)
    total_corr = sum(d["total_correctas"] for d in datos)
    if total_resp == 0:
        return 0.0
    return round((total_corr / total_resp) * 100, 1)


# ---------------------------------------------------------
# Actividad (días/horas de uso)
# ---------------------------------------------------------
def obtener_actividad(usuario_id: str):
    sb = get_supabase_client()
    res = (
        sb.table("sesiones")
        .select("hora_inicio, hora_fin")
        .eq("usuario_id", usuario_id)
        .not_.is_("hora_fin", "null")
        .execute()
    )
    return res.data or []
