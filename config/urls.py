from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shared.interfaces.health import health_check

api_v1_patterns = [
    path('auth/', include('modules.usuario.interfaces.urls')),
    path('empresas/', include('modules.empresa.interfaces.urls')),
    path('empleados/', include('modules.empleado.interfaces.urls')),
    path('asistencia/', include('modules.asistencia.interfaces.urls')),
    path('solicitudes/', include('modules.solicitud.interfaces.urls')),
    path('auditoria/', include('modules.auditoria.interfaces.urls')),
    path('notificaciones/', include('modules.notificacion.interfaces.urls')),
    path('suscripciones/', include('modules.suscripcion.interfaces.urls')),
    path('horarios/', include('modules.horario.interfaces.urls')),
]

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
