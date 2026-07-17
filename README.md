# NexusRH — Backend API

API REST para la plataforma SaaS de Gestión de Recursos Humanos NexusRH. Construida con Django, Django REST Framework y arquitectura limpia hexagonal.

## Tecnologías

- **Python 3.11+** / **Django 5.x**
- **Django REST Framework** — API REST
- **PostgreSQL** — Base de datos principal
- **Redis** — Cache y broker de Celery
- **Django Channels** — WebSockets para notificaciones en tiempo real
- **SimpleJWT** — Autenticación JWT con refresh tokens y blacklist
- **Celery** — Tareas asíncronas (emails, reportes)

---

## Requisitos previos

- Python 3.11 o superior
- PostgreSQL 14+
- Redis 6+
- `pip` y `virtualenv` o `conda`

---

## Instalación local

### 1. Clonar y entrar al directorio

```bash
git clone <repositorio>
cd hr-platform-api
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores locales
```

Variables obligatorias:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django | `django-insecure-...` |
| `DEBUG` | Modo depuración | `True` (local) / `False` (prod) |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DB_NAME` | Nombre de la base de datos | `BD_RRHH` |
| `DB_USER` | Usuario PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña PostgreSQL | `tu_password` |
| `DB_HOST` | Host PostgreSQL | `localhost` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `REDIS_URL` | URL de Redis | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS permitidos | `http://localhost:3000` |
| `EMAIL_HOST_USER` | Email remitente SMTP | `noreply@empresa.com` |
| `EMAIL_HOST_PASSWORD` | Contraseña App Gmail/SMTP | `xxxx xxxx xxxx xxxx` |

Variables opcionales (tienen valores por defecto):

| Variable | Default | Descripción |
|----------|---------|-------------|
| `JWT_ACCESS_LIFETIME_MINUTES` | `60` | Duración del access token |
| `JWT_REFRESH_LIFETIME_DAYS` | `7` | Duración del refresh token |
| `MAX_LOGIN_ATTEMPTS` | `5` | Intentos fallidos antes de bloqueo |
| `TRIAL_PERIOD_DAYS` | `30` | Días de periodo de prueba |
| `QR_EXPIRY_DEFAULT_MINUTES` | `480` | Expiración QR por defecto |
| `SECURE_SSL_REDIRECT` | `True` | Forzar HTTPS en producción |

### 5. Crear la base de datos PostgreSQL

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

La API estará disponible en: `http://127.0.0.1:8000/api/v1/`

---

## Estructura del Proyecto

```
hr-platform-api/
├── config/                    # Configuración Django
│   ├── settings/
│   │   ├── base.py           # Settings base (compartidos)
│   │   ├── development.py    # Settings de desarrollo
│   │   └── production.py     # Settings de producción
│   └── urls.py               # URLs raíz
├── modules/                   # Módulos de negocio (arquitectura hexagonal)
│   ├── empresa/              # Gestión de empresas y sedes
│   ├── usuario/              # Autenticación, usuarios, perfiles
│   ├── empleado/             # Empleados y directorio
│   ├── horario/              # Horarios laborales y turnos
│   ├── asistencia/           # Marcajes, tardanzas, horas extras
│   ├── solicitud/            # Permisos, vacaciones, licencias
│   ├── suscripcion/          # Planes y suscripciones (multiempresa)
│   ├── auditoria/            # Log de eventos del sistema
│   └── notificacion/         # Notificaciones y emails transaccionales
└── shared/                   # Código compartido entre módulos
    ├── constants.py           # Enums y constantes del sistema
    ├── domain/               # Excepciones de dominio
    └── infrastructure/       # Auth, pagination, permissions, error handler
```

Cada módulo sigue arquitectura hexagonal:
```
modulo/
├── domain/         # Entidades y contratos (repositorios)
├── application/    # Casos de uso y DTOs
├── infrastructure/ # Modelos Django, repositorios concretos, migraciones
└── interfaces/     # Vistas DRF, serializers, URLs
```

---

## Endpoints principales

| Prefijo | Módulo |
|---------|--------|
| `/api/v1/usuarios/` | Autenticación (login, logout, refresh, recuperar contraseña, perfil) |
| `/api/v1/empresas/` | Empresas y sedes |
| `/api/v1/empleados/` | Gestión de empleados |
| `/api/v1/horarios/` | Horarios y asignaciones |
| `/api/v1/asistencia/` | Marcajes y monitor de asistencia |
| `/api/v1/solicitudes/` | Permisos y vacaciones |
| `/api/v1/suscripcion/` | Suscripción de la empresa |
| `/api/v1/superadmin/` | Panel superadmin (empresas, planes, suscripciones) |
| `/api/v1/auditoria/` | Log de auditoría |
| `/api/v1/notificaciones/` | Centro de notificaciones |

---

## Comandos útiles

```bash
# Crear superusuario de Django
python manage.py createsuperuser

# Generar nuevas migraciones (tras modificar modelos)
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Correr tests
python manage.py test

# Shell interactivo de Django
python manage.py shell

# Colectar archivos estáticos (producción)
python manage.py collectstatic --noinput
```

---

## Despliegue en Producción

### Variables de entorno adicionales para producción

```env
DEBUG=False
SECRET_KEY=<clave-aleatoria-muy-larga>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://tudominio.com
SECURE_SSL_REDIRECT=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=noreply@tudominio.com
EMAIL_HOST_PASSWORD=<app-password>
```

### Con Gunicorn (servidor WSGI para producción)

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Configurar el archivo de settings

```bash
# Usar el settings de producción
export DJANGO_SETTINGS_MODULE=config.settings.production
```

---

## Seguridad

- Contraseñas hasheadas con PBKDF2 SHA256 (Django default)
- JWT con refresh token rotation y blacklist automática
- Middleware de tenant isolation (cada empresa solo ve sus datos)
- Middleware de cambio de contraseña obligatorio (bloquea API si `estado_seguridad = PASSWORD_CHANGE_REQUIRED`)
- Headers de seguridad HTTP activados en producción (HSTS, XSS filter, X-Frame)
- Custom exception handler que oculta stack traces en producción

---

## Licencia

Proyecto privado — NexusRH © 2026
