# EXANI-II Prep 📚

Webapp en Streamlit para practicar de cara al examen de admisión EXANI-II, con preguntas
de opción múltiple generadas/complementadas por Gemini, seguimiento de dominio por tema
y registro de actividad de estudio.

## Estructura

```
exani-prep/
├── app.py                  # Login y entrada principal
├── pages/
│   ├── 1_dashboard.py      # Dominio general/por tema + actividad (día/hora)
│   └── 2_practica.py       # Bloques de 10 preguntas + retroalimentación
├── utils/
│   ├── supabase_client.py
│   ├── gemini_client.py
│   └── helpers.py
├── data/
│   └── temario.py
├── supabase_schema.sql     # Ejecutar en el SQL editor de Supabase
├── requirements.txt
└── .streamlit/
    └── secrets.toml        # NO subir con valores reales
```

## 1. Configurar Supabase

1. Crea un proyecto en [supabase.com](https://supabase.com).
2. Ve a **SQL Editor** y ejecuta el contenido de `supabase_schema.sql`.
3. Crea tu primer usuario ejecutando en el SQL Editor:

```sql
SELECT crear_usuario('Tu Nombre', 'tu_usuario', 'tu_contraseña', '1');
```

   El último parámetro es el área: `'1'`, `'2'`, `'3'` o `'4'`.

4. Copia la **URL** y la **anon key** del proyecto (Settings → API).

## 2. Configurar secrets

Edita `.streamlit/secrets.toml` (local) o configura los **Secrets** en Streamlit Cloud:

```toml
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU_SUPABASE_ANON_KEY"
GEMINI_API_KEY = "TU_GEMINI_API_KEY"
```

> Importante: usa el modelo `gemini-2.5-flash` (ya configurado en `utils/gemini_client.py`).

## 3. Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Desplegar en Streamlit Cloud

1. Sube este repositorio a GitHub.
2. En [share.streamlit.io](https://share.streamlit.io), crea una nueva app apuntando a `app.py`.
3. Configura los Secrets desde el dashboard (mismo contenido que `secrets.toml`).

## Flujo de uso

1. El usuario inicia sesión con usuario/contraseña.
2. En **Práctica**, elige materia y subtema → se genera un bloque de 10 preguntas
   (del banco o complementadas con Gemini si faltan).
3. Al terminar el bloque, se calculan aciertos, se actualiza el dominio por tema
   y Gemini genera retroalimentación detallada de los errores.
4. El usuario puede iniciar otro bloque del mismo tema o volver a elegir tema.
5. En **Dashboard** se visualiza el dominio general, dominio por subtema y
   un mapa de calor de actividad de estudio por día/hora.
