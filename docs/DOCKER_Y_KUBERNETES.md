# Docker y Kubernetes - Backend (hr-platform-api)

Este documento explica cómo se empaqueta el backend en una imagen Docker, cómo se publica automáticamente en Docker Hub y cómo se despliega en Kubernetes. También detalla un bug real que se encontró y corrigió durante las pruebas: varios módulos de Django no registraban sus modelos correctamente.

Para la visión general de todo el sistema (backend + frontend + base de datos, en local y en Kubernetes), ver [`docs/ORQUESTACION_Y_DESPLIEGUE.md`](../../docs/ORQUESTACION_Y_DESPLIEGUE.md) en la raíz del proyecto.

---

## 1. La imagen Docker

El [`Dockerfile`](../Dockerfile) usa una construcción en dos etapas (*multi-stage build*):

### Etapa 1: `builder`

- Parte de `python:3.11-slim`.
- Instala las librerías del sistema necesarias para compilar dependencias con partes en C (`psycopg2`, `Pillow`, etc.): `build-essential`, `libpq-dev`, `libffi-dev`, `libssl-dev`.
- Crea un entorno virtual en `/opt/venv` e instala ahí las dependencias de `requirements/production.txt`.

### Etapa 2: `runtime`

- Vuelve a partir de `python:3.11-slim`, pero esta vez **limpia**, sin herramientas de compilación.
- Copia únicamente el entorno virtual ya armado (`/opt/venv`) desde la etapa `builder`. Así la imagen final no carga con `gcc` ni con los paquetes `-dev`, que solo hacían falta para compilar.
- Instala solo `libpq5` (la librería cliente de PostgreSQL en tiempo de ejecución, sin las cabeceras de desarrollo).
- Copia el código de la aplicación.
- Crea un usuario sin privilegios (`appuser`) y cambia el dueño de `/app` a ese usuario, para no correr el proceso como `root` dentro del contenedor.
- Corre `collectstatic` en tiempo de build (con `|| true` para que un fallo ahí no rompa el build completo; los estáticos son opcionales si se sirven desde otro lado, como S3).
- Expone el puerto 8000 y arranca con **Gunicorn**, usando el worker de **Uvicorn** (`--worker-class uvicorn.workers.UvicornWorker`) en lugar del worker WSGI estándar, porque el proyecto usa Django Channels para WebSockets y necesita un servidor ASGI.

Este patrón de dos etapas es importante porque reduce bastante el tamaño final de la imagen y su superficie de ataque (menos herramientas instaladas, menos como qué explotar si hay una vulnerabilidad).

### Construir la imagen manualmente (sin `docker-compose`)

```bash
cd hr-platform-api
docker build -t hr-platform-api:local .
docker run --rm -p 8000:8000 --env-file .env hr-platform-api:local
```

---

## 2. Publicación automática en Docker Hub

El workflow [`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml) se dispara con cada `push` a la rama `main`. Hace lo siguiente:

1. Descarga el código (`actions/checkout`).
2. Configura Docker Buildx (el motor de build extendido de Docker, necesario para usar caché remota).
3. Inicia sesión en Docker Hub usando los secretos `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` del repositorio.
4. Construye la imagen y la publica con dos etiquetas:
   - `wily12/hr-platform-api:latest`
   - `wily12/hr-platform-api:<sha-del-commit>` (permite volver atrás a una versión exacta si hace falta)
5. Usa caché de GitHub Actions (`cache-from`/`cache-to: type=gha`) para que builds sucesivos con pocos cambios sean más rápidos.

Este repositorio **no** tiene protegida la rama `main`, así que un `git push origin main` alcanza para disparar el workflow. No hace falta abrir Pull Request (aunque sigue siendo buena práctica hacerlo para revisión de código).

Hay un segundo workflow, `django.yml`, que corre las pruebas del proyecto contra varias versiones de Python (3.7, 3.8, 3.9). Actualmente el job de 3.7 falla al instalar dependencias porque esa versión ya no tiene soporte, y por la configuración `fail-fast` de la matriz cancela los jobs de 3.8 y 3.9 también. Esto es independiente del workflow de Docker (no lo bloquea), pero sería bueno actualizar esa matriz para reflejar la versión real usada en producción (Python 3.11, según el `Dockerfile`).

---

## 3. Despliegue en Kubernetes

El manifiesto [`k8s/05-backend.yaml`](../../k8s/05-backend.yaml) (en la raíz del proyecto) define:

- Un `Deployment` con **2 réplicas**, estrategia `RollingUpdate` (`maxSurge: 1`, `maxUnavailable: 0`): al actualizar, primero se crea el Pod nuevo y se espera a que esté listo antes de apagar uno viejo, así nunca hay menos de 2 réplicas sanas.
- Un **`initContainer`** llamado `migrate` que corre `python manage.py migrate --noinput` **antes** de que el contenedor principal arranque. Al ser un `initContainer`, Kubernetes garantiza que termine (exitosamente) antes de iniciar el contenedor de la aplicación. Es idempotente, así que no hay problema en que corra en cada una de las réplicas.
- `readinessProbe` y `livenessProbe` por TCP sobre el puerto 8000.
- Límites de recursos (`resources.requests` / `resources.limits`) para CPU y memoria, para que un solo Pod no pueda acaparar todo el nodo.
- Un `Service` de tipo `ClusterIP` que expone el Deployment dentro del clúster en el puerto 8000.

La configuración no sensible (nombre de base de datos, host de Redis, etc.) llega desde el `ConfigMap` `nexushr-config`, y los valores sensibles (`SECRET_KEY`, `DB_PASSWORD`) desde el `Secret` `nexushr-secrets`. Ambos se definen en `k8s/02-configmap.yaml` y `k8s/01-secret.yaml` respectivamente.

---

## 4. Bug corregido: modelos de Django no registrados

### Síntoma

Al correr `python manage.py migrate` dentro del contenedor, Django fallaba con errores de este tipo:

```
horario.AsignacionHorarioModel.creado_por: (fields.E300) Field defines a relation with model
'usuario.UsuarioModel', which is either not installed, or is abstract.
horario.AsignacionHorarioModel.empleado: (fields.E300) Field defines a relation with model
'empleado.EmpleadoModel', which is either not installed, or is abstract.
horario.HorarioModel.empresa: (fields.E300) Field defines a relation with model
'empresa.EmpresaModel', which is either not installed, or is abstract.
```

Esto pasaba a pesar de que los modelos `UsuarioModel`, `EmpleadoModel` y `EmpresaModel` sí existían en el código y sí estaban bien escritos.

### Causa raíz

El proyecto sigue una arquitectura hexagonal: cada módulo de negocio (`modules/usuario`, `modules/empresa`, etc.) define sus modelos de Django dentro de `infrastructure/models/`, no directamente en la raíz del módulo.

El problema es que **Django, al arrancar (`django.setup()`), solo importa automáticamente el archivo `<nombre_del_app>/models.py`** de cada aplicación listada en `INSTALLED_APPS`. Si ese archivo no existe, Django simplemente no encuentra ningún modelo para esa aplicación durante el arranque, y por lo tanto no los registra en su "app registry" interno.

Al revisar el proyecto, se encontró que **ocho de los nueve módulos locales no tenían ese archivo `models.py`**:

| Módulo | ¿Tenía `models.py`? |
|--------|:---:|
| `empresa` | No |
| `usuario` | No |
| `suscripcion` | No |
| `empleado` | No |
| `asistencia` | No |
| `solicitud` | No |
| `auditoria` | No |
| `notificacion` | No |
| `horario` | Sí (era el único correcto) |

Como `horario` sí tenía su `models.py` bien armado, sus modelos (`HorarioModel`, `TurnoModel`, `AsignacionHorarioModel`) eran los únicos que quedaban registrados al arrancar. Y como esos modelos tienen claves foráneas (`ForeignKey`) hacia modelos de otros módulos (`"empresa.EmpresaModel"`, `"usuario.UsuarioModel"`, `"empleado.EmpleadoModel"`), el verificador interno de Django (`manage.py check`, que corre automáticamente antes de `migrate`) intentaba resolver esas referencias y no las encontraba, porque esos otros módulos nunca habían llegado a registrar ningún modelo.

En otras palabras: el bug siempre estuvo ahí de forma latente (los otros ocho módulos nunca se auto-registraban), pero solo se volvía un error visible cuando otro módulo (`horario`) intentaba apuntarles con una relación. Antes de que existiera `horario`, es probable que el sistema funcionara "por accidente": los modelos igual terminaban registrándose en algún momento porque otro archivo del proyecto (una vista, un serializador, un repositorio) los importaba directamente en algún punto de la ejecución, pero eso pasaba después de que el chequeo de arranque de Django ya había corrido, por lo que el `check`/`migrate` inicial podía fallar igual dependiendo del orden de importación.

### Solución aplicada

Se replicó, para los ocho módulos que no lo tenían, el mismo patrón que ya usaba `horario` correctamente:

1. En `modules/<app>/infrastructure/models/__init__.py` (que estaba vacío), se agregaron las importaciones explícitas de cada clase de modelo del módulo. Por ejemplo, para `usuario`:

   ```python
   from .usuario_model import UsuarioModel
   from .rol_model import RolModel
   ```

2. Se creó el archivo `modules/<app>/models.py` (que no existía) re-exportando esos modelos desde la ruta que Django sí revisa automáticamente:

   ```python
   from .infrastructure.models import UsuarioModel, RolModel
   ```

Con esto, en cuanto Django arranca e importa `modules.usuario.models`, esa importación dispara en cadena la importación de `infrastructure/models/__init__.py`, que a su vez importa las clases reales de los archivos `usuario_model.py` y `rol_model.py`. Al importarse, cada clase se registra automáticamente en el sistema de aplicaciones de Django (esto lo hace el metaclass `ModelBase` en el momento en que se define la clase). Resultado: todos los modelos quedan disponibles desde el arranque, sin importar el orden en que después se importen otros archivos.

Los módulos corregidos fueron: `empresa`, `usuario`, `suscripcion`, `empleado`, `asistencia`, `solicitud`, `auditoria` y `notificacion`.

### Cómo evitar este bug en módulos nuevos

Al crear un módulo nuevo bajo `modules/`, siempre se debe crear el archivo `modules/<nombre_del_modulo>/models.py` que re-exporte los modelos reales desde `infrastructure/models/`, siguiendo el mismo patrón que los módulos existentes. Sin ese archivo, el módulo puede parecer que funciona en desarrollo (porque otros archivos lo importan indirectamente en algún momento) pero fallará de forma intermitente en comandos que dependen del registro temprano de modelos, como `migrate`, `makemigrations` o `check`.

### Cómo se detectó y se verificó la corrección

1. Al correr `docker compose up`, el contenedor del backend entraba en un ciclo de reinicios (`restart: unless-stopped`) porque `manage.py migrate` fallaba antes de que Gunicorn pudiera arrancar.
2. Se revisaron los logs con `docker compose logs backend` y se identificó el error `fields.E300`.
3. Se comparó la estructura de `horario` (que funcionaba) contra la de los demás módulos, encontrando la diferencia del archivo `models.py` faltante.
4. Tras aplicar la corrección, se reconstruyó la imagen (`docker compose build backend`) y se reinició el contenedor (`docker compose up -d backend`). Los logs mostraron todas las migraciones aplicándose correctamente y Gunicorn arrancando sin errores.
5. Se confirmó adicionalmente que el panel de administración de Django respondía (`GET /admin/` devolvía un `302`, la redirección normal hacia el login), lo cual solo es posible si todas las vistas y sus modelos relacionados cargan sin errores.
