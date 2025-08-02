"""
Módulo de consultas SQL CORREGIDAS para Fragmentación
Este módulo contiene consultas basadas en la estructura REAL de las tablas del proyecto.

ESTRUCTURA REAL DE TABLAS:

CENTRAL:
- planilla: id_planilla, id_profesor, salario, mes
- pagare: id_pagare, id_estudiante, monto, vencimiento
- profesor: id_profesor, nombre, email, id_sede
- sede: id_sede, nombre, direccion
- carrera: id_carrera, nombre, id_sede

SAN CARLOS & HEREDIA:
- estudiante: id_estudiante, nombre, email, id_sede 
- curso: id_curso, nombre, id_carrera
- matricula: id_matricula, id_estudiante, id_curso
- nota: id_nota, id_matricula, nota
- asistencia: id_asistencia, id_matricula, fecha, presente
- (Tablas replicadas: sede, carrera, profesor)
"""

# Consultas CORREGIDAS para fragmentación horizontal por sede
FRAGMENTACION_HORIZONTAL_QUERIES_REAL = {
    'central': {
        'descripcion': 'Sede Central - Datos Administrativos + Maestros',
        'puerto': 3306,
        'schema': 'cenfotec_central',
        'consultas': {
            'planillas_profesor': {
                'nombre': 'Planillas por Profesor',
                'descripcion': 'Muestra los salarios registrados por profesor en la planilla',
                'sql': """
                    SELECT 
                        p.nombre as profesor,
                        pl.salario,
                        pl.mes,
                        pl.fecha_creacion
                    FROM planilla pl
                    JOIN profesor p ON pl.id_profesor = p.id_profesor
                    ORDER BY pl.fecha_creacion DESC
                    LIMIT 15;
                """,
                'campos_esperados': ['profesor', 'salario', 'mes', 'fecha_creacion']
            },
            'pagares_vencimiento': {
                'nombre': 'Pagarés por Vencimiento',
                'descripcion': 'Lista de pagarés ordenados por fecha de vencimiento',
                'sql': """
                    SELECT 
                        pg.id_pagare,
                        pg.monto,
                        pg.vencimiento,
                        pg.fecha_creacion,
                        DATEDIFF(pg.vencimiento, CURDATE()) as dias_vencimiento
                    FROM pagare pg
                    ORDER BY pg.vencimiento ASC
                    LIMIT 15;
                """,
                'campos_esperados': ['id_pagare', 'monto', 'vencimiento', 'fecha_creacion', 'dias_vencimiento']
            },
            'profesores_sede': {
                'nombre': 'Profesores por Sede',
                'descripcion': 'Distribución de profesores por cada sede del sistema',
                'sql': """
                    SELECT 
                        s.nombre as sede,
                        COUNT(p.id_profesor) as total_profesores
                    FROM profesor p
                    JOIN sede s ON p.id_sede = s.id_sede
                    GROUP BY s.id_sede, s.nombre
                    ORDER BY total_profesores DESC;
                """,
                'campos_esperados': ['sede', 'total_profesores']
            },
            'resumen_administrativo': {
                'nombre': 'Resumen de Datos Administrativos',
                'descripcion': 'Vista consolidada de todas las tablas administrativas',
                'sql': """
                    SELECT 
                        'Planillas' as categoria,
                        COUNT(*) as total_registros,
                        'Registros de salarios' as descripcion
                    FROM planilla
                    UNION ALL
                    SELECT 
                        'Pagarés' as categoria,
                        COUNT(*) as total_registros,
                        'Compromisos de pago' as descripcion
                    FROM pagare
                    UNION ALL
                    SELECT 
                        'Profesores' as categoria,
                        COUNT(*) as total_registros,
                        'Docentes registrados' as descripcion
                    FROM profesor;
                """,
                'campos_esperados': ['categoria', 'total_registros', 'descripcion']
            }
        }
    },
    'sancarlos': {
        'descripcion': 'Sede San Carlos - Datos Académicos (id_sede = 2)',
        'puerto': 3307,
        'schema': 'cenfotec_sancarlos',
        'consultas': {
            'estudiantes_sancarlos': {
                'nombre': 'Estudiantes de San Carlos',
                'descripcion': 'Lista de estudiantes matriculados en la sede San Carlos',
                'sql': """
                    SELECT 
                        e.nombre,
                        e.email,
                        e.fecha_creacion,
                        COUNT(m.id_matricula) as cursos_matriculados
                    FROM estudiante e
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    WHERE e.id_sede = 2
                    GROUP BY e.id_estudiante, e.nombre, e.email, e.fecha_creacion
                    ORDER BY cursos_matriculados DESC, e.nombre ASC
                    LIMIT 15;
                """,
                'campos_esperados': ['nombre', 'email', 'fecha_creacion', 'cursos_matriculados']
            },
            'matriculas_curso': {
                'nombre': 'Matrículas por Curso',
                'descripcion': 'Cantidad de estudiantes matriculados en cada curso',
                'sql': """
                    SELECT 
                        c.nombre as curso,
                        COUNT(m.id_matricula) as estudiantes_matriculados,
                        c.fecha_creacion
                    FROM curso c
                    LEFT JOIN matricula m ON c.id_curso = m.id_curso
                    GROUP BY c.id_curso, c.nombre, c.fecha_creacion
                    ORDER BY estudiantes_matriculados DESC
                    LIMIT 15;
                """,
                'campos_esperados': ['curso', 'estudiantes_matriculados', 'fecha_creacion']
            },
            'estadisticas_notas': {
                'nombre': 'Estadísticas de Notas',
                'descripcion': 'Análisis de rendimiento académico en San Carlos',
                'sql': """
                    SELECT 
                        COUNT(n.id_nota) as total_notas,
                        AVG(n.nota) as promedio_general,
                        MIN(n.nota) as nota_minima,
                        MAX(n.nota) as nota_maxima,
                        COUNT(CASE WHEN n.nota >= 70 THEN 1 END) as notas_aprobadas,
                        COUNT(CASE WHEN n.nota < 70 THEN 1 END) as notas_reprobadas
                    FROM nota n;
                """,
                'campos_esperados': ['total_notas', 'promedio_general', 'nota_minima', 'nota_maxima', 'notas_aprobadas', 'notas_reprobadas']
            },
            'resumen_asistencia': {
                'nombre': 'Resumen de Asistencia',
                'descripcion': 'Análisis de asistencia por fecha reciente',
                'sql': """
                    SELECT 
                        a.fecha,
                        COUNT(*) as total_registros,
                        SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) as presentes,
                        SUM(CASE WHEN a.presente = 0 THEN 1 ELSE 0 END) as ausentes,
                        ROUND((SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as porcentaje_asistencia
                    FROM asistencia a
                    GROUP BY a.fecha
                    ORDER BY a.fecha DESC
                    LIMIT 10;
                """,
                'campos_esperados': ['fecha', 'total_registros', 'presentes', 'ausentes', 'porcentaje_asistencia']
            }
        }
    },
    'heredia': {
        'descripcion': 'Sede Heredia - Datos Académicos (id_sede = 3)',
        'puerto': 3308,
        'schema': 'cenfotec_heredia',
        'consultas': {
            'estudiantes_heredia': {
                'nombre': 'Estudiantes de Heredia',
                'descripcion': 'Lista de estudiantes matriculados en la sede Heredia',
                'sql': """
                    SELECT 
                        e.nombre,
                        e.email,
                        e.fecha_creacion,
                        COUNT(m.id_matricula) as cursos_matriculados
                    FROM estudiante e
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    WHERE e.id_sede = 3
                    GROUP BY e.id_estudiante, e.nombre, e.email, e.fecha_creacion
                    ORDER BY cursos_matriculados DESC, e.nombre ASC
                    LIMIT 15;
                """,
                'campos_esperados': ['nombre', 'email', 'fecha_creacion', 'cursos_matriculados']
            },
            'matriculas_curso': {
                'nombre': 'Matrículas por Curso',
                'descripcion': 'Cantidad de estudiantes matriculados en cada curso',
                'sql': """
                    SELECT 
                        c.nombre as curso,
                        COUNT(m.id_matricula) as estudiantes_matriculados,
                        c.fecha_creacion
                    FROM curso c
                    LEFT JOIN matricula m ON c.id_curso = m.id_curso
                    GROUP BY c.id_curso, c.nombre, c.fecha_creacion
                    ORDER BY estudiantes_matriculados DESC
                    LIMIT 15;
                """,
                'campos_esperados': ['curso', 'estudiantes_matriculados', 'fecha_creacion']
            },
            'estadisticas_notas': {
                'nombre': 'Estadísticas de Notas',
                'descripcion': 'Análisis de rendimiento académico en Heredia',
                'sql': """
                    SELECT 
                        COUNT(n.id_nota) as total_notas,
                        AVG(n.nota) as promedio_general,
                        MIN(n.nota) as nota_minima,
                        MAX(n.nota) as nota_maxima,
                        COUNT(CASE WHEN n.nota >= 70 THEN 1 END) as notas_aprobadas,
                        COUNT(CASE WHEN n.nota < 70 THEN 1 END) as notas_reprobadas
                    FROM nota n;
                """,
                'campos_esperados': ['total_notas', 'promedio_general', 'nota_minima', 'nota_maxima', 'notas_aprobadas', 'notas_reprobadas']
            },
            'resumen_asistencia': {
                'nombre': 'Resumen de Asistencia',
                'descripcion': 'Análisis de asistencia por fecha reciente',
                'sql': """
                    SELECT 
                        a.fecha,
                        COUNT(*) as total_registros,
                        SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) as presentes,
                        SUM(CASE WHEN a.presente = 0 THEN 1 ELSE 0 END) as ausentes,
                        ROUND((SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as porcentaje_asistencia
                    FROM asistencia a
                    GROUP BY a.fecha
                    ORDER BY a.fecha DESC
                    LIMIT 10;
                """,
                'campos_esperados': ['fecha', 'total_registros', 'presentes', 'ausentes', 'porcentaje_asistencia']
            }
        }
    }
}

# Consultas CORREGIDAS para comparación entre sedes
CONSULTAS_COMPARACION_SEDES_REAL = {
    'estudiantes_por_sede': {
        'nombre': 'Comparación de Estudiantes por Sede',
        'descripcion': 'Compara el número de estudiantes entre las sedes académicas',
        'consulta_sancarlos': """
            SELECT 
                'San Carlos' as sede,
                COUNT(*) as total_estudiantes,
                2 as id_sede
            FROM estudiante 
            WHERE id_sede = 2;
        """,
        'consulta_heredia': """
            SELECT 
                'Heredia' as sede,
                COUNT(*) as total_estudiantes,
                3 as id_sede
            FROM estudiante 
            WHERE id_sede = 3;
        """
    },
    'matriculas_por_sede': {
        'nombre': 'Comparación de Matrículas por Sede',
        'descripcion': 'Compara el volumen de matrículas entre sedes',
        'consulta_sancarlos': """
            SELECT 
                'San Carlos' as sede,
                COUNT(m.id_matricula) as total_matriculas,
                COUNT(DISTINCT m.id_estudiante) as estudiantes_unicos,
                COUNT(DISTINCT m.id_curso) as cursos_diferentes
            FROM matricula m;
        """,
        'consulta_heredia': """
            SELECT 
                'Heredia' as sede,
                COUNT(m.id_matricula) as total_matriculas,
                COUNT(DISTINCT m.id_estudiante) as estudiantes_unicos,
                COUNT(DISTINCT m.id_curso) as cursos_diferentes
            FROM matricula m;
        """
    },
    'rendimiento_por_sede': {
        'nombre': 'Comparación de Rendimiento Académico',
        'descripcion': 'Compara el rendimiento académico promedio entre sedes',
        'consulta_sancarlos': """
            SELECT 
                'San Carlos' as sede,
                COUNT(n.id_nota) as total_notas,
                AVG(n.nota) as promedio_general,
                COUNT(CASE WHEN n.nota >= 70 THEN 1 END) as aprobados,
                COUNT(CASE WHEN n.nota < 70 THEN 1 END) as reprobados,
                ROUND((COUNT(CASE WHEN n.nota >= 70 THEN 1 END) * 100.0 / COUNT(n.id_nota)), 2) as porcentaje_aprobacion
            FROM nota n;
        """,
        'consulta_heredia': """
            SELECT 
                'Heredia' as sede,
                COUNT(n.id_nota) as total_notas,
                AVG(n.nota) as promedio_general,
                COUNT(CASE WHEN n.nota >= 70 THEN 1 END) as aprobados,
                COUNT(CASE WHEN n.nota < 70 THEN 1 END) as reprobados,
                ROUND((COUNT(CASE WHEN n.nota >= 70 THEN 1 END) * 100.0 / COUNT(n.id_nota)), 2) as porcentaje_aprobacion
            FROM nota n;
        """
    }
}

# Consultas CORREGIDAS para fragmentación vertical
CONSULTAS_FRAGMENTACION_VERTICAL_REAL = {
    'datos_administrativos_central': """
        SELECT 
            'Datos Administrativos' as categoria,
            tabla,
            registros,
            'Central' as ubicacion
        FROM (
            SELECT 'Planillas' as tabla, COUNT(*) as registros FROM planilla
            UNION ALL
            SELECT 'Pagarés' as tabla, COUNT(*) as registros FROM pagare
            UNION ALL
            SELECT 'Profesores' as tabla, COUNT(*) as registros FROM profesor
            UNION ALL
            SELECT 'Sedes' as tabla, COUNT(*) as registros FROM sede
            UNION ALL
            SELECT 'Carreras' as tabla, COUNT(*) as registros FROM carrera
        ) as datos_admin;
    """,
    'datos_academicos_sancarlos': """
        SELECT 
            'Datos Académicos' as categoria,
            tabla,
            registros,
            'San Carlos' as ubicacion
        FROM (
            SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante
            UNION ALL
            SELECT 'Cursos' as tabla, COUNT(*) as registros FROM curso
            UNION ALL
            SELECT 'Matrículas' as tabla, COUNT(*) as registros FROM matricula
            UNION ALL
            SELECT 'Notas' as tabla, COUNT(*) as registros FROM nota
            UNION ALL
            SELECT 'Asistencias' as tabla, COUNT(*) as registros FROM asistencia
        ) as datos_acad;
    """,
    'datos_academicos_heredia': """
        SELECT 
            'Datos Académicos' as categoria,
            tabla,
            registros,
            'Heredia' as ubicacion
        FROM (
            SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante
            UNION ALL
            SELECT 'Cursos' as tabla, COUNT(*) as registros FROM curso
            UNION ALL
            SELECT 'Matrículas' as tabla, COUNT(*) as registros FROM matricula
            UNION ALL
            SELECT 'Notas' as tabla, COUNT(*) as registros FROM nota
            UNION ALL
            SELECT 'Asistencias' as tabla, COUNT(*) as registros FROM asistencia
        ) as datos_acad;
    """
}

# Consultas para fragmentación mixta REAL
CONSULTAS_FRAGMENTACION_MIXTA_REAL = {
    'estudiantes_fragmentacion': {
        'nombre': 'Fragmentación de Estudiantes',
        'descripcion': 'Muestra cómo los estudiantes están fragmentados por sede',
        'central': """
            SELECT 
                e.id_sede,
                s.nombre as sede,
                COUNT(e.id_estudiante) as total_estudiantes
            FROM estudiante e
            JOIN sede s ON e.id_sede = s.id_sede
            GROUP BY e.id_sede, s.nombre
            ORDER BY e.id_sede;
        """,
        'sancarlos': """
            SELECT 
                2 as id_sede,
                'San Carlos' as sede,
                COUNT(*) as total_estudiantes
            FROM estudiante
            WHERE id_sede = 2;
        """,
        'heredia': """
            SELECT 
                3 as id_sede,
                'Heredia' as sede,
                COUNT(*) as total_estudiantes
            FROM estudiante
            WHERE id_sede = 3;
        """
    }
}

# Funciones de utilidad CORREGIDAS
def generar_consulta_fragmentacion_real(sede_id, tabla='estudiante', limit=10):
    """
    Genera una consulta de fragmentación horizontal usando campos REALES
    """
    if tabla == 'estudiante':
        return f"""
            SELECT nombre, email, fecha_creacion
            FROM estudiante 
            WHERE id_sede = {sede_id} 
            ORDER BY nombre 
            LIMIT {limit};
        """
    elif tabla == 'profesor':
        return f"""
            SELECT nombre, email, fecha_creacion
            FROM profesor 
            WHERE id_sede = {sede_id} 
            ORDER BY nombre 
            LIMIT {limit};
        """
    else:
        return f"SELECT * FROM {tabla} LIMIT {limit};"

def generar_consulta_comparacion_real(tabla, campo_agrupacion='id_sede'):
    """
    Genera una consulta para comparar datos entre sedes usando estructura REAL
    """
    if tabla == 'estudiante':
        return """
            SELECT 
                s.nombre as sede,
                COUNT(e.id_estudiante) as total_registros
            FROM estudiante e
            JOIN sede s ON e.id_sede = s.id_sede
            GROUP BY s.nombre, s.id_sede
            ORDER BY total_registros DESC;
        """
    elif tabla == 'profesor':
        return """
            SELECT 
                s.nombre as sede,
                COUNT(p.id_profesor) as total_registros
            FROM profesor p
            JOIN sede s ON p.id_sede = s.id_sede
            GROUP BY s.nombre, s.id_sede
            ORDER BY total_registros DESC;
        """
    else:
        return f"SELECT COUNT(*) as total FROM {tabla};"

def obtener_estadisticas_sede_real(sede_id):
    """
    Retorna consultas estadísticas REALES para una sede específica
    """
    queries = {
        'estudiantes': f"SELECT COUNT(*) as total FROM estudiante WHERE id_sede = {sede_id}",
        'matriculas': f"""
            SELECT COUNT(m.id_matricula) as total 
            FROM matricula m 
            JOIN estudiante e ON m.id_estudiante = e.id_estudiante 
            WHERE e.id_sede = {sede_id}
        """,
        'promedio_notas': f"""
            SELECT AVG(n.nota) as promedio 
            FROM nota n 
            JOIN matricula m ON n.id_matricula = m.id_matricula
            JOIN estudiante e ON m.id_estudiante = e.id_estudiante 
            WHERE e.id_sede = {sede_id}
        """,
        'asistencia_promedio': f"""
            SELECT 
                COUNT(*) as total_asistencias,
                SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) as presentes,
                ROUND((SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as porcentaje
            FROM asistencia a
            JOIN matricula m ON a.id_matricula = m.id_matricula
            JOIN estudiante e ON m.id_estudiante = e.id_estudiante 
            WHERE e.id_sede = {sede_id}
        """
    }
    return queries

# Metadatos REALES para la interfaz
SEDE_METADATA_REAL = {
    'central': {
        'nombre_completo': 'Sede Central - San José',
        'color': '#1f77b4',
        'icono': '🏛️',
        'id_sede': 1,
        'descripcion': 'Centro administrativo y master de replicación',
        'responsabilidades': ['Planillas', 'Pagarés', 'Datos Maestros'],
        'tablas_exclusivas': ['planilla', 'pagare'],
        'tablas_compartidas': ['sede', 'carrera', 'profesor'],
        'puerto': 3306
    },
    'sancarlos': {
        'nombre_completo': 'Sede Regional - San Carlos',
        'color': '#ff7f0e', 
        'icono': '🏢',
        'id_sede': 2,
        'descripcion': 'Operaciones académicas regionales',
        'responsabilidades': ['Estudiantes (id_sede=2)', 'Matrículas', 'Notas', 'Asistencia'],
        'tablas_exclusivas': ['estudiante', 'matricula', 'nota', 'asistencia'],
        'tablas_replicadas': ['sede', 'carrera', 'profesor'],
        'puerto': 3307
    },
    'heredia': {
        'nombre_completo': 'Sede Regional - Heredia',
        'color': '#2ca02c',
        'icono': '🏫', 
        'id_sede': 3,
        'descripcion': 'Operaciones académicas regionales',
        'responsabilidades': ['Estudiantes (id_sede=3)', 'Matrículas', 'Notas', 'Asistencia'],
        'tablas_exclusivas': ['estudiante', 'matricula', 'nota', 'asistencia'],
        'tablas_replicadas': ['sede', 'carrera', 'profesor'],
        'puerto': 3308
    }
}

# Consultas para validación de estructura (debugging)
CONSULTAS_VALIDACION = {
    'mostrar_tablas': "SHOW TABLES;",
    'estructura_estudiante': "DESCRIBE estudiante;",
    'estructura_planilla': "DESCRIBE planilla;",
    'estructura_pagare': "DESCRIBE pagare;",
    'estructura_nota': "DESCRIBE nota;",
    'estructura_asistencia': "DESCRIBE asistencia;",
    'contar_estudiantes_por_sede': """
        SELECT id_sede, COUNT(*) as total 
        FROM estudiante 
        GROUP BY id_sede 
        ORDER BY id_sede;
    """,
    'verificar_datos_maestros': """
        SELECT 'sede' as tabla, COUNT(*) as registros FROM sede
        UNION ALL
        SELECT 'carrera' as tabla, COUNT(*) as registros FROM carrera  
        UNION ALL
        SELECT 'profesor' as tabla, COUNT(*) as registros FROM profesor;
    """
}