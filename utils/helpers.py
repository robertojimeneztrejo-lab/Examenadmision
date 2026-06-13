# utils/helpers.py
import random
from datetime import datetime, timezone


DIAS_SEMANA_ES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def seleccionar_aleatorias(preguntas: list, n: int = 10):
    """Selecciona hasta n preguntas aleatorias de una lista."""
    if len(preguntas) <= n:
        return preguntas
    return random.sample(preguntas, n)


def calcular_aciertos(respuestas_usuario: dict, preguntas: list):
    """respuestas_usuario: {pregunta_id: 'A'/'B'/'C'/'D'}
    preguntas: lista de dicts con 'id' y 'respuesta_correcta'
    Devuelve (aciertos, lista_errores)
    """
    aciertos = 0
    errores = []
    for p in preguntas:
        resp = respuestas_usuario.get(p["id"])
        if resp == p["respuesta_correcta"]:
            aciertos += 1
        else:
            errores.append({
                "pregunta": p["pregunta"],
                "opcion_a": p["opcion_a"],
                "opcion_b": p["opcion_b"],
                "opcion_c": p["opcion_c"],
                "opcion_d": p["opcion_d"],
                "respuesta_correcta": p["respuesta_correcta"],
                "respuesta_usuario": resp or "(sin respuesta)",
            })
    return aciertos, errores


def procesar_actividad(actividad_raw: list):
    """Convierte registros de sesiones en una matriz día_semana x hora
    para graficar un heatmap de actividad.
    actividad_raw: lista de dicts con hora_inicio, hora_fin (ISO strings)
    Devuelve DataFrame-ready: lista de dicts {dia, hora, minutos}
    """
    resultado = []
    for s in actividad_raw:
        inicio = datetime.fromisoformat(s["hora_inicio"].replace("Z", "+00:00"))
        fin = datetime.fromisoformat(s["hora_fin"].replace("Z", "+00:00"))
        dia = DIAS_SEMANA_ES[inicio.weekday()]
        hora = inicio.hour
        minutos = (fin - inicio).total_seconds() / 60
        resultado.append({"dia": dia, "hora": hora, "minutos": minutos})
    return resultado

