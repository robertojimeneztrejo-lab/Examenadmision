-- =========================================================
-- ESQUEMA SUPABASE - EXANI PREP APP
-- =========================================================

-- Extensión para hashing de contraseñas (pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Usuarios (con login simple usuario/contraseña)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    area TEXT NOT NULL CHECK (area IN ('1','2','3','4')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Banco de preguntas
CREATE TABLE preguntas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    materia TEXT NOT NULL,
    subtema TEXT NOT NULL,
    area_aplicable TEXT[] NOT NULL DEFAULT ARRAY['1','2','3','4'],
    pregunta TEXT NOT NULL,
    opcion_a TEXT NOT NULL,
    opcion_b TEXT NOT NULL,
    opcion_c TEXT NOT NULL,
    opcion_d TEXT NOT NULL,
    respuesta_correcta CHAR(1) NOT NULL CHECK (respuesta_correcta IN ('A','B','C','D')),
    explicacion TEXT,
    dificultad SMALLINT DEFAULT 1 CHECK (dificultad BETWEEN 1 AND 3),
    fuente TEXT DEFAULT 'banco',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Sesiones de estudio
CREATE TABLE sesiones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    materia TEXT NOT NULL,
    subtema TEXT,
    hora_inicio TIMESTAMPTZ DEFAULT now(),
    hora_fin TIMESTAMPTZ,
    num_preguntas SMALLINT DEFAULT 10,
    aciertos SMALLINT DEFAULT 0
);

-- Respuestas individuales
CREATE TABLE respuestas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID REFERENCES sesiones(id) ON DELETE CASCADE,
    pregunta_id UUID REFERENCES preguntas(id),
    respuesta_usuario CHAR(1),
    es_correcta BOOLEAN,
    tiempo_respuesta_seg NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Dominio acumulado por subtema
CREATE TABLE dominio_temas (
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    materia TEXT NOT NULL,
    subtema TEXT NOT NULL,
    total_respondidas INT DEFAULT 0,
    total_correctas INT DEFAULT 0,
    porcentaje_dominio NUMERIC GENERATED ALWAYS AS (
        CASE WHEN total_respondidas = 0 THEN 0
        ELSE ROUND((total_correctas::NUMERIC / total_respondidas) * 100, 1)
        END
    ) STORED,
    ultima_actualizacion TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (usuario_id, materia, subtema)
);

-- Vista para barra de actividad (días/horas de uso)
CREATE VIEW actividad_usuario AS
SELECT
    usuario_id,
    DATE(hora_inicio) AS dia,
    TO_CHAR(hora_inicio, 'Day') AS dia_semana,
    EXTRACT(DOW FROM hora_inicio) AS dia_semana_num,
    EXTRACT(HOUR FROM hora_inicio) AS hora,
    COUNT(*) AS sesiones_realizadas,
    SUM(EXTRACT(EPOCH FROM (hora_fin - hora_inicio))/60) AS minutos_totales
FROM sesiones
WHERE hora_fin IS NOT NULL
GROUP BY usuario_id, DATE(hora_inicio), TO_CHAR(hora_inicio, 'Day'), EXTRACT(DOW FROM hora_inicio), EXTRACT(HOUR FROM hora_inicio);

-- Índices
CREATE INDEX idx_preguntas_materia_subtema ON preguntas(materia, subtema);
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);
CREATE INDEX idx_respuestas_sesion ON respuestas(sesion_id);
CREATE INDEX idx_dominio_usuario ON dominio_temas(usuario_id);

-- =========================================================
-- Función helper para crear usuarios con password hasheado
-- Uso: SELECT crear_usuario('Roberto', 'roberto', 'miPassword123', '1');
-- =========================================================
CREATE OR REPLACE FUNCTION crear_usuario(
    p_nombre TEXT,
    p_username TEXT,
    p_password TEXT,
    p_area TEXT
) RETURNS UUID AS $$
DECLARE
    nuevo_id UUID;
BEGIN
    INSERT INTO usuarios (nombre, username, password_hash, area)
    VALUES (p_nombre, p_username, crypt(p_password, gen_salt('bf')), p_area)
    RETURNING id INTO nuevo_id;
    RETURN nuevo_id;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- Función para validar login
-- Uso: SELECT * FROM validar_login('roberto', 'miPassword123');
-- =========================================================
CREATE OR REPLACE FUNCTION validar_login(
    p_username TEXT,
    p_password TEXT
) RETURNS TABLE(id UUID, nombre TEXT, area TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.nombre, u.area
    FROM usuarios u
    WHERE u.username = p_username
      AND u.password_hash = crypt(p_password, u.password_hash);
END;
$$ LANGUAGE plpgsql;
