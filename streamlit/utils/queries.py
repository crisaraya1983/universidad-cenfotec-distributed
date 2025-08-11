FRAGMENTATION_QUERIES = {
    'horizontal_estudiantes': """
        SELECT s.nombre as sede, 
               COUNT(e.id_estudiante) as total_estudiantes
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        GROUP BY s.nombre
    """,
    
    'vertical_administrativa': """
        SELECT 'Planillas' as tipo_dato, COUNT(*) as registros
        FROM planilla
        UNION ALL
        SELECT 'Pagarés' as tipo_dato, COUNT(*) as registros
        FROM pagare
    """,
    
    'vertical_academica': """
        SELECT 'Estudiantes' as tipo_dato, COUNT(*) as registros
        FROM estudiante
        UNION ALL
        SELECT 'Matrículas' as tipo_dato, COUNT(*) as registros
        FROM matricula
        UNION ALL
        SELECT 'Notas' as tipo_dato, COUNT(*) as registros
        FROM nota
    """
}

REPLICATION_QUERIES = {
    'check_master_data': """
        SELECT 'Carreras' as tabla, COUNT(*) as registros, MAX(id_carrera) as max_id
        FROM carrera
        UNION ALL
        SELECT 'Profesores' as tabla, COUNT(*) as registros, MAX(id_profesor) as max_id
        FROM profesor
        UNION ALL
        SELECT 'Sedes' as tabla, COUNT(*) as registros, MAX(id_sede) as max_id
        FROM sede
    """,
    
    'compare_carreras': """
        SELECT c.id_carrera, c.nombre, s.nombre as sede
        FROM carrera c
        JOIN sede s ON c.id_sede = s.id_sede
        ORDER BY c.id_carrera
    """,
    
    'replication_lag': """
        SELECT 
            table_name,
            update_time,
            TIMESTAMPDIFF(SECOND, update_time, NOW()) as seconds_ago
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name IN ('carrera', 'profesor', 'sede')
        ORDER BY update_time DESC
    """
}

TRANSACTION_QUERIES = {
    'global_student_report': """
        SELECT 
            s.nombre as sede,
            COUNT(DISTINCT e.id_estudiante) as estudiantes,
            COUNT(DISTINCT m.id_matricula) as matriculas,
            COUNT(DISTINCT p.id_pago) as pagos,
            COALESCE(SUM(p.monto), 0) as total_pagos
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
        LEFT JOIN pago p ON e.id_estudiante = p.id_estudiante
        GROUP BY s.nombre
    """,
    
    'financial_summary': """
        SELECT 
            'Ingresos' as concepto,
            SUM(monto) as total,
            COUNT(*) as cantidad,
            AVG(monto) as promedio
        FROM pago
        WHERE MONTH(fecha) = MONTH(CURRENT_DATE)
        AND YEAR(fecha) = YEAR(CURRENT_DATE)
    """,
    
    'academic_performance': """
        SELECT 
            c.nombre as curso,
            COUNT(DISTINCT m.id_estudiante) as estudiantes,
            AVG(n.nota) as promedio,
            MIN(n.nota) as nota_minima,
            MAX(n.nota) as nota_maxima
        FROM curso c
        JOIN matricula m ON c.id_curso = m.id_curso
        LEFT JOIN nota n ON m.id_matricula = n.id_matricula
        GROUP BY c.id_curso, c.nombre
        ORDER BY promedio DESC
    """
}

MONITORING_QUERIES = {
    'table_sizes': """
        SELECT 
            table_name,
            table_rows,
            ROUND(data_length/1024/1024, 2) as data_mb,
            ROUND(index_length/1024/1024, 2) as index_mb,
            ROUND((data_length + index_length)/1024/1024, 2) as total_mb
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY total_mb DESC
    """,
    
    'connection_status': """
        SELECT 
            user,
            host,
            db,
            command,
            time as seconds,
            state
        FROM information_schema.processlist
        WHERE db = %s
        ORDER BY time DESC
    """,
    
    'slow_queries': """
        SELECT 
            start_time,
            user_host,
            query_time,
            lock_time,
            rows_sent,
            rows_examined,
            db,
            LEFT(sql_text, 100) as query_preview
        FROM mysql.slow_log
        WHERE db = %s
        ORDER BY start_time DESC
        LIMIT 10
    """,
    
    'index_usage': """
        SELECT 
            table_name,
            index_name,
            cardinality,
            CASE 
                WHEN cardinality = 0 THEN 'Unused'
                WHEN cardinality < 100 THEN 'Low Usage'
                WHEN cardinality < 1000 THEN 'Medium Usage'
                ELSE 'High Usage'
            END as usage_level
        FROM information_schema.statistics
        WHERE table_schema = %s
        ORDER BY cardinality DESC
    """
}

ANALYSIS_QUERIES = {
    'student_distribution': """
        SELECT 
            s.nombre as sede,
            ca.nombre as carrera,
            COUNT(DISTINCT e.id_estudiante) as estudiantes
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        JOIN matricula m ON e.id_estudiante = m.id_estudiante
        JOIN curso cu ON m.id_curso = cu.id_curso
        JOIN carrera ca ON cu.id_carrera = ca.id_carrera
        GROUP BY s.nombre, ca.nombre
        ORDER BY s.nombre, estudiantes DESC
    """,
    
    'payment_trends': """
        SELECT 
            DATE_FORMAT(fecha, '%Y-%m') as mes,
            COUNT(*) as numero_pagos,
            SUM(monto) as total,
            AVG(monto) as promedio,
            concepto
        FROM pago
        WHERE fecha >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY mes, concepto
        ORDER BY mes DESC
    """,
    
    'attendance_analysis': """
        SELECT 
            c.nombre as curso,
            COUNT(DISTINCT a.id_asistencia) as clases_totales,
            SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) as presentes,
            ROUND(SUM(CASE WHEN a.presente = 1 THEN 1 ELSE 0 END) * 100.0 / 
                  COUNT(DISTINCT a.id_asistencia), 2) as porcentaje_asistencia
        FROM asistencia a
        JOIN matricula m ON a.id_matricula = m.id_matricula
        JOIN curso c ON m.id_curso = c.id_curso
        GROUP BY c.id_curso, c.nombre
        HAVING clases_totales > 0
        ORDER BY porcentaje_asistencia DESC
    """
}

USER_VIEW_QUERIES = {
    'student_view': """
        CREATE OR REPLACE VIEW vista_estudiante AS
        SELECT 
            e.id_estudiante,
            e.nombre,
            e.email,
            s.nombre as sede,
            COUNT(DISTINCT m.id_curso) as cursos_activos,
            AVG(n.nota) as promedio_general
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
        LEFT JOIN nota n ON m.id_matricula = n.id_matricula
        WHERE e.id_estudiante = %s
        GROUP BY e.id_estudiante
    """,
    
    'professor_view': """
        CREATE OR REPLACE VIEW vista_profesor AS
        SELECT 
            p.id_profesor,
            p.nombre,
            p.email,
            s.nombre as sede,
            COUNT(DISTINCT c.id_curso) as cursos_impartidos,
            COUNT(DISTINCT m.id_estudiante) as total_estudiantes
        FROM profesor p
        JOIN sede s ON p.id_sede = s.id_sede
        LEFT JOIN curso c ON p.id_profesor = c.id_profesor
        LEFT JOIN matricula m ON c.id_curso = m.id_curso
        WHERE p.id_profesor = %s
        GROUP BY p.id_profesor
    """,
    
    'admin_view': """
        CREATE OR REPLACE VIEW vista_administrativa AS
        SELECT 
            'Total Estudiantes' as metrica,
            COUNT(DISTINCT e.id_estudiante) as valor
        FROM estudiante e
        UNION ALL
        SELECT 
            'Total Profesores' as metrica,
            COUNT(DISTINCT p.id_profesor) as valor
        FROM profesor p
        UNION ALL
        SELECT 
            'Ingresos del Mes' as metrica,
            COALESCE(SUM(monto), 0) as valor
        FROM pago
        WHERE MONTH(fecha) = MONTH(CURRENT_DATE)
    """
}

TRANSFER_QUERIES = {
    'validate_student_eligibility': """
    SELECT e.*, 
           COUNT(m.id_matricula) as materias_activas,
           COALESCE(SUM(CASE WHEN p.monto < 0 THEN 1 ELSE 0 END), 0) as deudas_pendientes
    FROM estudiante e
    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante  
    LEFT JOIN pago p ON e.id_estudiante = p.id_estudiante
    WHERE e.id_estudiante = %s
    GROUP BY e.id_estudiante
    """,
    
    'check_career_compatibility': """
    SELECT c1.nombre as carrera_origen, c2.nombre as carrera_destino
    FROM carrera c1, carrera c2 
    WHERE c1.id_sede = %s AND c2.id_sede = %s 
    AND c1.nombre = c2.nombre
    """
}

def build_date_filter(start_date=None, end_date=None, date_column='fecha'):
    conditions = []
    
    if start_date:
        conditions.append(f"{date_column} >= '{start_date}'")
    
    if end_date:
        conditions.append(f"{date_column} <= '{end_date}'")
    
    if conditions:
        return f"WHERE {' AND '.join(conditions)}"
    
    return ""

def build_pagination(page=1, per_page=50):
    offset = (page - 1) * per_page
    return f"LIMIT {per_page} OFFSET {offset}"

# Queries dinámicas para reportes
class ReportQueries:
    
    @staticmethod
    def student_report(sede_id=None, carrera_id=None):
        base_query = """
        SELECT 
            e.nombre as estudiante,
            e.email,
            s.nombre as sede,
            ca.nombre as carrera,
            COUNT(DISTINCT m.id_curso) as cursos_matriculados,
            AVG(n.nota) as promedio
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
        LEFT JOIN curso cu ON m.id_curso = cu.id_curso
        LEFT JOIN carrera ca ON cu.id_carrera = ca.id_carrera
        LEFT JOIN nota n ON m.id_matricula = n.id_matricula
        """
        
        conditions = []
        if sede_id:
            conditions.append(f"e.id_sede = {sede_id}")
        if carrera_id:
            conditions.append(f"ca.id_carrera = {carrera_id}")
        
        if conditions:
            base_query += f"WHERE {' AND '.join(conditions)} "
        
        base_query += """
        GROUP BY e.id_estudiante, e.nombre, e.email, s.nombre, ca.nombre
        ORDER BY promedio DESC
        """
        
        return base_query
    
    @staticmethod
    def financial_report(start_date=None, end_date=None, concepto=None):
        base_query = """
        SELECT 
            DATE_FORMAT(p.fecha, '%Y-%m-%d') as fecha,
            s.nombre as sede,
            p.concepto,
            COUNT(*) as numero_pagos,
            SUM(p.monto) as total,
            AVG(p.monto) as promedio,
            MIN(p.monto) as minimo,
            MAX(p.monto) as maximo
        FROM pago p
        JOIN estudiante e ON p.id_estudiante = e.id_estudiante
        JOIN sede s ON e.id_sede = s.id_sede
        """
        
        conditions = []
        if start_date:
            conditions.append(f"p.fecha >= '{start_date}'")
        if end_date:
            conditions.append(f"p.fecha <= '{end_date}'")
        if concepto:
            conditions.append(f"p.concepto = '{concepto}'")
        
        if conditions:
            base_query += f"WHERE {' AND '.join(conditions)} "
        
        base_query += """
        GROUP BY fecha, s.nombre, p.concepto
        ORDER BY fecha DESC
        """
        
        return base_query

__all__ = [
    'FRAGMENTATION_QUERIES',
    'REPLICATION_QUERIES',
    'TRANSACTION_QUERIES',
    'MONITORING_QUERIES',
    'ANALYSIS_QUERIES',
    'USER_VIEW_QUERIES',
    'build_date_filter',
    'build_pagination',
    'ReportQueries'
]