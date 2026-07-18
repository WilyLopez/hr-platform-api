# NexusRH - Backend API

API REST para la plataforma SaaS de Gestión de Recursos Humanos NexusRH. Construida con Django, Django REST Framework y arquitectura hexagonal.

## Tecnologias

* Python 3.11+ / Django 5.x
* Django REST Framework - API REST
* PostgreSQL - Base de datos principal
* Redis - Cache y broker de Celery
* Django Channels - WebSockets para notificaciones en tiempo real
* SimpleJWT - Autenticación JWT con tokens de acceso y refresco
* Celery - Tareas asíncronas (envío de correos, reportes)

---

## Requisitos Previos

* Python 3.11 o superior
* PostgreSQL 14+
* Redis 6+
* Administrador de paquetes pip y entorno virtual (venv o conda)

---

## Instalacion Local

### 1. Clonar y acceder al directorio

```bash
git clone <repositorio>
cd hr-platform-api
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
# En Windows (PowerShell)
.venv\Scripts\Activate.ps1
# En Windows (CMD)
.venv\Scripts\activate.bat
# En Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements/production.txt
# O bien, si estás en desarrollo:
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copie el archivo de ejemplo y configure los valores correspondientes a su entorno local:

```bash
cp .env.example .env
```

Variables obligatorias a configurar:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| SECRET_KEY | Clave secreta de Django | django-insecure-... |
| DEBUG | Modo de depuración | True (local) / False (producción) |
| ALLOWED_HOSTS | Hosts permitidos | localhost,127.0.0.1 |
| DB_NAME | Nombre de la base de datos | BD_RRHH |
| DB_USER | Usuario PostgreSQL | postgres |
| DB_PASSWORD | Contraseña de PostgreSQL | tu_contrasena |
| DB_HOST | Host de PostgreSQL | localhost |
| DB_PORT | Puerto de PostgreSQL | 5432 |
| REDIS_URL | URL del servidor Redis | redis://localhost:6379/0 |
| CORS_ALLOWED_ORIGINS | Orígenes permitidos por CORS | http://localhost:3000 |
| EMAIL_HOST_USER | Email remitente SMTP | correo@empresa.com |
| EMAIL_HOST_PASSWORD | Contraseña de aplicación SMTP | xxxx xxxx xxxx xxxx |

Variables opcionales:

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| JWT_ACCESS_LIFETIME_MINUTES | 60 | Minutos de vida del token de acceso |
| JWT_REFRESH_LIFETIME_DAYS | 7 | Días de vida del token de refresco |
| MAX_LOGIN_ATTEMPTS | 5 | Intentos fallidos antes de bloqueo temporal |
| TRIAL_PERIOD_DAYS | 30 | Días del periodo de prueba |
| QR_EXPIRY_DEFAULT_MINUTES | 480 | Minutos de expiración del token QR |
| SECURE_SSL_REDIRECT | True | Redirección forzosa a HTTPS |

### 5. Crear la base de datos PostgreSQL

Asegúrese de crear la base de datos en su servidor local de PostgreSQL:

```sql
CREATE DATABASE "BD_RRHH";
```

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

### 7. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

La API estará disponible localmente en: http://127.0.0.1:8000/api/v1/

---

## Actualizar el Proyecto (Para Compañeros de Equipo)

Cuando se integren nuevos cambios al repositorio, siga estos pasos para sincronizar su entorno local:

```bash
# 1. Traer los últimos cambios
git pull origin develop

# 2. Actualizar dependencias
pip install -r requirements.txt

# 3. Aplicar nuevas migraciones de base de datos
python manage.py migrate
```

---

## Estructura del Proyecto

El código está estructurado bajo principios de arquitectura hexagonal para mantener la mantenibilidad del software:

```
hr-platform-api/
├── config/                    # Configuración raíz de Django
│   ├── settings/
│   │   ├── base.py           # Configuración común
│   │   ├── development.py    # Configuración de desarrollo
│   │   └── production.py     # Configuración de producción
│   └── urls.py               # URLs principales del proyecto
├── modules/                   # Módulos de dominio y lógica de negocio
│   ├── empresa/              # Empresas, sedes y geovallas
│   ├── usuario/              # Usuarios, autenticación y perfiles
│   ├── empleado/             # Expediente del empleado
│   ├── horario/              # Turnos, horarios y asignaciones
│   ├── asistencia/           # Marcaje de asistencia, QR, horas extras
│   ├── solicitud/            # Solicitudes de vacaciones y permisos
│   ├── suscripcion/          # Planes y suscripciones SaaS
│   ├── auditoria/            # Logs de auditoría de seguridad
│   └── notificacion/         # Emailing y notificaciones del sistema
└── shared/                   # Componentes transversales
    ├── constants.py          # Enums y constantes globales
    ├── domain/               # Clases base del dominio
    └── infrastructure/       # Middlewares, autorizaciones y helpers
```

Cada módulo sigue internamente la estructura de capas:
* **domain**: Entidades de negocio y definiciones de interfaz (puertos).
* **application**: Casos de uso y transferencia de datos (DTOs).
* **infrastructure**: Implementaciones concretas (modelos Django, servicios externos).
* **interfaces**: Controladores HTTP, serializadores y rutas API.

---

## Endpoints Principales

| Prefijo de Ruta | Responsabilidad |
|-----------------|-----------------|
| /api/v1/usuarios/ | Autenticación, registro, perfil y contraseñas |
| /api/v1/empresas/ | Gestión de empresas y configuración de sedes |
| /api/v1/empleados/ | Directorio y datos de colaboradores |
| /api/v1/horarios/ | Definición de horarios laborales |
| /api/v1/asistencia/ | Registro manual y automático de asistencia |
| /api/v1/solicitudes/ | Peticiones de licencias, permisos y vacaciones |
| /api/v1/suscripcion/ | Gestión de planes y facturación de empresas |
| /api/v1/superadmin/ | Administración global de la plataforma SaaS |
| /api/v1/auditoria/ | Consulta de logs de auditoría (solo administradores) |

---

## Comandos Utiles

```bash
# Crear un usuario administrador de Django
python manage.py createsuperuser

# Generar nuevas migraciones después de modificar modelos
python manage.py makemigrations

# Aplicar las migraciones creadas
python manage.py migrate

# Ejecutar las pruebas unitarias
python manage.py test

# Iniciar la terminal interactiva de Django
python manage.py shell

# Recopilar archivos estáticos para el despliegue
python manage.py collectstatic --noinput
```

---

## Despliegue en Produccion

### Variables de entorno adicionales para produccion

```env
DEBUG=False
SECRET_KEY=su-clave-secreta-altamente-segura-y-unica
ALLOWED_HOSTS=tudominio.com,api.tudominio.com
DATABASE_URL=postgres://usuario:contrasena@servidor:5432/bdname
CORS_ALLOWED_ORIGINS=https://tudominio.com
SECURE_SSL_REDIRECT=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=notificaciones@tudominio.com
EMAIL_HOST_PASSWORD=contrasena-de-aplicacion
```

### Ejecutar con Gunicorn (servidor WSGI de grado de producción)

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Configurar el entorno de ejecucion

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

---

## Seguridad

* Hasheo de contraseñas mediante algoritmo PBKDF2 con SHA256.
* Autenticación con JWT usando rotación de tokens y lista de bloqueo para cierre de sesión.
* Aislamiento estricto a nivel de base de datos de datos por inquilino (SaaS multi-tenant).
* Requerimiento obligatorio de cambio de contraseña inicial para cuentas recién creadas.
* Cabeceras de seguridad HTTP robustas habilitadas en producción.
* Manejador de excepciones centralizado para prevenir la fuga de trazas en entornos públicos.

---

## Licencia

NexusRH. Todos los derechos reservados.
