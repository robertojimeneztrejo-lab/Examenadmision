# app.py
import streamlit as st
from utils.supabase_client import validar_login
from data.temario import AREAS

st.set_page_config(page_title="EXANI-II Prep", page_icon="📚", layout="wide")


def login_screen():
    st.title("📚 EXANI-II Prep")
    st.subheader("Inicia sesión para continuar")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")

    if submitted:
        if not username or not password:
            st.warning("Por favor ingresa usuario y contraseña.")
            return

        usuario = validar_login(username, password)
        if usuario:
            st.session_state["usuario_id"] = usuario["id"]
            st.session_state["nombre"] = usuario["nombre"]
            st.session_state["area"] = "TODAS"  # por defecto, el usuario elige luego en el sidebar
            st.success(f"¡Bienvenido, {usuario['nombre']}!")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.divider()
    st.caption(
        "¿No tienes cuenta? Pide al administrador que la cree desde Supabase "
        "usando la función `crear_usuario('Nombre', 'usuario', 'contraseña', 'área')`."
    )


def main_app():
    st.sidebar.title("📚 EXANI-II Prep")
    st.sidebar.markdown(f"**Usuario:** {st.session_state['nombre']}")

    # Selector de área (puede cambiarse libremente durante la sesión)
    opciones_area = list(AREAS.keys())
    area_actual = st.session_state.get("area", "TODAS")
    if area_actual not in opciones_area:
        area_actual = "TODAS"

    nueva_area = st.sidebar.selectbox(
        "Área a estudiar",
        options=opciones_area,
        index=opciones_area.index(area_actual),
        format_func=lambda a: AREAS.get(a, a),
        help="Puedes cambiar el área en cualquier momento. Elige 'Todas las áreas' "
             "si tu examen incluye preguntas de varias áreas.",
    )
    st.session_state["area"] = nueva_area

    if st.sidebar.button("Cerrar sesión"):
        for key in ["usuario_id", "nombre", "area"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.title(f"¡Hola, {st.session_state['nombre']}! 👋")
    st.markdown(
        """
        Usa el menú de la izquierda para navegar:

        - **Dashboard**: revisa tu progreso, dominio por tema y tu actividad de estudio.
        - **Práctica**: selecciona una materia y subtema para responder un bloque de 10 preguntas.

        ¡Mucho éxito en tu preparación! 🚀
        """
    )


# ---------------------------------------------------------
# Control de flujo principal
# ---------------------------------------------------------
if "usuario_id" not in st.session_state:
    login_screen()
else:
    main_app()
