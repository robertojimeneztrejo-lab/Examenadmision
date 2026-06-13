# utils/gemini_client.py
import json
import re
import streamlit as st
import google.generativeai as genai


MODEL_NAME = "gemini-2.5-flash"


@st.cache_resource
def get_gemini_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel(MODEL_NAME)


def _limpiar_json(texto: str) -> str:
    """Elimina backticks/markdown fences si Gemini los incluye."""
    texto = texto.strip()
    texto = re.sub(r"^```json\s*", "", texto)
    texto = re.sub(r"^```\s*", "", texto)
    texto = re.sub(r"```\s*$", "", texto)
    return texto.strip()


PROMPT_GENERAR_PREGUNTAS = """
Eres un experto en exámenes de admisión universitaria tipo CENEVAL (EXANI-II), México.

Genera {n} preguntas de opción múltiple sobre:
- Materia: {materia}
- Subtema: {subtema}
- Nivel de dificultad: {dificultad} (1=básico, 2=intermedio, 3=avanzado)

Requisitos:
- Cada pregunta debe tener 4 opciones (A, B, C, D), solo una correcta.
- Las opciones incorrectas deben ser distractores plausibles (errores comunes de razonamiento).
- Incluye una explicación clara y paso a paso de cómo llegar a la respuesta correcta.
- Lenguaje claro, formal, en español de México.
- Basa el contenido en el temario oficial EXANI-II.
- No repitas preguntas genéricas ni triviales.

Responde ÚNICAMENTE con un JSON válido, sin texto adicional ni backticks, con esta estructura exacta:

{{
  "preguntas": [
    {{
      "pregunta": "texto de la pregunta",
      "opcion_a": "texto",
      "opcion_b": "texto",
      "opcion_c": "texto",
      "opcion_d": "texto",
      "respuesta_correcta": "A",
      "explicacion": "explicación paso a paso"
    }}
  ]
}}
"""

PROMPT_RETROALIMENTACION = """
Eres un tutor experto preparando estudiantes mexicanos para el examen EXANI-II (CENEVAL).

El estudiante respondió incorrectamente las siguientes preguntas:

{lista_errores}

Para cada pregunta, genera una retroalimentación que incluya:
1. Por qué su respuesta es incorrecta (identifica el posible error de razonamiento).
2. El procedimiento correcto, paso a paso, para llegar a la respuesta correcta.
3. Un tip o regla mnemotécnica para no repetir el error.

Responde en español de México, tono motivador pero directo y profesional.
Usa formato Markdown con un encabezado "### Pregunta N" por cada pregunta.
"""


def generar_preguntas(materia: str, subtema: str, n: int = 10, dificultad: int = 1, area: str = "1"):
    """Genera preguntas con Gemini y devuelve una lista de dicts listos para insertar
    en la tabla `preguntas` de Supabase."""
    model = get_gemini_model()
    prompt = PROMPT_GENERAR_PREGUNTAS.format(
        n=n, materia=materia, subtema=subtema, dificultad=dificultad
    )

    response = model.generate_content(prompt)
    texto = _limpiar_json(response.text)

    try:
        data = json.loads(texto)
    except json.JSONDecodeError:
        # Intento de recuperación: buscar el primer bloque {...}
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError(f"No se pudo parsear la respuesta de Gemini:\n{texto}")

    area_aplicable = ["1", "2", "3", "4"] if area == "TODAS" else [area]

    # Mapeo flexible de posibles nombres de keys que Gemini podría usar
    ALIAS = {
        "pregunta": ["pregunta", "question", "texto", "enunciado"],
        "opcion_a": ["opcion_a", "opcion_A", "a", "A", "option_a"],
        "opcion_b": ["opcion_b", "opcion_B", "b", "B", "option_b"],
        "opcion_c": ["opcion_c", "opcion_C", "c", "C", "option_c"],
        "opcion_d": ["opcion_d", "opcion_D", "d", "D", "option_d"],
        "respuesta_correcta": ["respuesta_correcta", "respuesta", "correct_answer", "answer"],
        "explicacion": ["explicacion", "explanation", "explicación"],
    }

    def get_campo(p: dict, campo: str, default=None):
        for key in ALIAS[campo]:
            if key in p and p[key] not in (None, ""):
                return p[key]
        return default

    preguntas = []
    descartadas = 0
    for p in data.get("preguntas", []):
        if not isinstance(p, dict):
            descartadas += 1
            continue

        texto_pregunta = get_campo(p, "pregunta")
        opc_a = get_campo(p, "opcion_a")
        opc_b = get_campo(p, "opcion_b")
        opc_c = get_campo(p, "opcion_c")
        opc_d = get_campo(p, "opcion_d")
        resp_correcta = get_campo(p, "respuesta_correcta")

        # Si falta cualquier campo esencial, descartar esta pregunta
        if not all([texto_pregunta, opc_a, opc_b, opc_c, opc_d, resp_correcta]):
            descartadas += 1
            continue

        resp_correcta = str(resp_correcta).strip().upper()
        if resp_correcta not in ("A", "B", "C", "D"):
            descartadas += 1
            continue

        preguntas.append({
            "materia": materia,
            "subtema": subtema,
            "area_aplicable": area_aplicable,
            "pregunta": texto_pregunta,
            "opcion_a": opc_a,
            "opcion_b": opc_b,
            "opcion_c": opc_c,
            "opcion_d": opc_d,
            "respuesta_correcta": resp_correcta,
            "explicacion": get_campo(p, "explicacion", ""),
            "dificultad": dificultad,
            "fuente": "gemini",
        })

    if not preguntas:
        raise ValueError(
            f"Gemini no devolvió preguntas válidas para '{materia} / {subtema}'. "
            f"Respuesta cruda:\n{texto[:1500]}"
        )

    return preguntas


def generar_retroalimentacion(errores: list):
    """errores: lista de dicts con keys:
    pregunta, opcion_a..d, respuesta_correcta, respuesta_usuario
    Devuelve texto en Markdown.
    """
    if not errores:
        return "¡Excelente! No tuviste errores en este bloque. 🎉"

    model = get_gemini_model()

    bloques = []
    for i, e in enumerate(errores):
        bloques.append(
            f"Pregunta {i+1}: {e['pregunta']}\n"
            f"Opciones: A) {e['opcion_a']}  B) {e['opcion_b']}  "
            f"C) {e['opcion_c']}  D) {e['opcion_d']}\n"
            f"Respuesta correcta: {e['respuesta_correcta']}\n"
            f"Respuesta del usuario: {e['respuesta_usuario']}"
        )
    lista_errores = "\n\n".join(bloques)

    prompt = PROMPT_RETROALIMENTACION.format(lista_errores=lista_errores)
    response = model.generate_content(prompt)
    return response.text
