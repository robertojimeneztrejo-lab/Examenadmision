# data/temario.py
"""
Temario EXANI-II organizado por materia y subtemas.
'areas' indica en qué áreas aplica cada materia:
1 = Físico-Matemáticas e Ingenierías
2 = Ciencias Biológicas, Químicas y de la Salud
3 = Ciencias Sociales y Administrativas
4 = Humanidades y Artes

Por defecto, todas las materias "básicas" aplican a todas las áreas (['1','2','3','4']).
Las materias especiales (Cálculo, Química del Carbono, Filosofía) tienen áreas restringidas.
"""

TEMARIO = {
    "Español": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "Funciones de la lengua",
            "Formas del discurso",
            "Comprensión de lectura",
            "Gramática",
            "Redacción",
            "Vocabulario",
            "Ortografía",
        ],
    },
    "Matemáticas": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "Operaciones con números reales, complejos y expresiones algebraicas",
            "Productos notables y factorización",
            "Ecuaciones",
            "Desigualdades",
            "Sistemas de ecuaciones",
            "Funciones algebraicas",
            "Trigonometría",
            "Funciones trigonométricas",
            "Funciones exponenciales y logarítmicas",
            "Recta",
            "Circunferencia",
            "Elipse",
            "Hipérbola",
            "Ecuación general de segundo grado",
        ],
    },
    "Física": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "Cinemática",
            "Fuerzas, leyes de Newton y Ley de la Gravitación Universal",
            "Trabajo y leyes de la conservación",
            "Termodinámica",
            "Ondas",
            "Electromagnetismo",
            "Fluidos",
            "Óptica",
            "Física contemporánea",
        ],
    },
    "Química": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "Temas básicos",
            "Agua",
            "Aire",
            "Alimentos",
            "La energía y las reacciones químicas",
        ],
    },
    "Biología": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "Célula",
            "Metabolismo celular",
            "Reproducción",
            "Mecanismos de la herencia",
            "Evolución",
            "Los seres vivos y su ambiente",
        ],
    },
    "Historia Universal": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "La Historia",
            "Las revoluciones burguesas",
            "Pensamiento y movimientos sociales y políticos del siglo XIX",
            "El imperialismo",
            "La Primera Guerra Mundial",
            "El mundo entre guerras",
            "La Segunda Guerra Mundial",
            "El conflicto entre el capitalismo y el socialismo",
            "El mundo actual",
        ],
    },
    "Historia de México": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "La Nueva España (siglos XVI a XIX)",
            "El movimiento de Independencia de la Nueva España (1810-1821)",
            "México independiente (1821-1854)",
            "La Reforma liberal y la resistencia de la República (1854-1876)",
            "El Porfiriato (1876-1911)",
            "La Revolución Mexicana (1910-1920)",
            "La reconstrucción nacional (1920-1940)",
            "México contemporáneo (1940-2000)",
        ],
    },
    "Literatura": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "El texto",
            "Géneros y corrientes literarias",
            "Redacción y técnicas de investigación documental",
        ],
    },
    "Geografía": {
        "areas": ["1", "2", "3", "4"],
        "subtemas": [
            "La Tierra, base del desarrollo del hombre",
            "Geografía humana: el paisaje cultural (espacio geográfico)",
        ],
    },
    # Exclusivo de áreas 1 y 2
    "Límites, Derivadas e Integrales": {
        "areas": ["1", "2"],
        "subtemas": [
            "Límites: concepto intuitivo",
            "Límites: definición formal",
            "Límites: teoremas",
            "Límites: obtención",
            "Límites: formas indeterminadas",
            "Continuidad en un punto y en un intervalo",
            "La derivada: definición y notaciones",
            "Obtención de derivadas",
            "Regla de la cadena",
            "Derivada de funciones implícitas",
            "Derivadas sucesivas",
            "Interpretación geométrica y física de la derivada",
            "Ecuaciones de la tangente y la normal a una curva",
            "Cálculo de velocidad y aceleración de un móvil",
            "Máximos y mínimos relativos",
            "Máximos y mínimos absolutos en intervalo cerrado",
            "Puntos de inflexión y concavidad",
            "Problemas de aplicación de la derivada",
            "La integral: función integrable",
            "Teoremas de propiedades de la integral",
            "Integral inmediata",
            "Tabla de fórmulas de integración",
            "Métodos de integración",
            "Integral definida y su notación",
        ],
    },
    # Exclusivo de área 2
    "Química del Carbono": {
        "areas": ["2"],
        "subtemas": [
            "Carbono",
            "Alcanos, alquenos, alquinos y cíclicos",
            "Grupos funcionales",
            "Reacciones orgánicas",
        ],
    },
    # Exclusivo de área 4
    "Filosofía": {
        "areas": ["4"],
        "subtemas": [
            "Lógica: tipos de lenguaje (informativo, directivo, expresivo)",
            "Lógica: estructura de argumentos",
            "Ética: moral",
            "Ética: responsabilidad moral",
            "Ética: valores",
            "Estética",
            "Ontología",
            "Epistemología",
        ],
    },
}


def materias_por_area(area: str):
    """Devuelve lista de materias aplicables a un área dada."""
    return [m for m, d in TEMARIO.items() if area in d["areas"]]


def subtemas_de(materia: str):
    """Devuelve lista de subtemas de una materia."""
    return TEMARIO.get(materia, {}).get("subtemas", [])


AREAS = {
    "1": "Físico-Matemáticas e Ingenierías",
    "2": "Ciencias Biológicas, Químicas y de la Salud",
    "3": "Ciencias Sociales y Administrativas",
    "4": "Humanidades y Artes",
}
