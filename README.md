# Sistema de Base de Datos Distribuida - Universidad Cenfotec

## Instalación

### Requisitos
- Docker Desktop instalado y corriendo
- Git

### Pasos de instalación

1. Clonar el proyecto
```bash
git clone https://github.com/crisaraya1983/universidad-cenfotec-distributed.git
cd universidad-cenfotec-distributed
```

2. Ejecutar setup automático (opcion 1)
```bash
# Windows
setup.bat
```
# Linux/Mac
Paso 3

3. Ejecutar setup (opcion 2)
```bash
docker-compose build
docker-compose up -d
```

4. Verificar instalación
```bash
docker-compose ps
```

Todos los servicios deben mostrar estado "Up".

5. En caso de un Reset
```bash
docker-compose down -v
git pull
docker-compose up -d
```

6. En caso de hacer cambios en Streamlit y necesitar refrescar
```bash
docker-compose restart streamlit-app
```

## Acceso al sistema

### URLs principales
- Streamlit (Interfaz principal): http://localhost:8501
- phpMyAdmin: http://localhost:8080

### Credenciales
- **Usuario**: root
- **Contraseña**: admin123

## Resultado esperado
Después de la instalación debe verse:
- Interfaz web Streamlit
- 3 bases de datos MySQL (Central, San Carlos, Heredia) con datos de prueba
- Sistema de load balancing con NGINX
- Cache Redis

## Solución de problemas

Si algo falla:
```bash
docker-compose down
docker-compose up -d
```

Para ver logs:
```bash
docker-compose logs
```

## En Caso de Problemas con las Vistas
Abrir phpMyAdmin: http://localhost:8080 o bien un gestor de Bases de Datos como DBeaver y correr en cada servidor los archivos de vistas en el folder de vistas
