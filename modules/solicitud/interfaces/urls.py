from django.urls import path
from modules.solicitud.interfaces.views.solicitud_view import (
    SolicitudListView,
    SolicitudDetailView,
    SolicitudAprobarView,
    SolicitudDetailView,
    SolicitudRechazarView,
    SolicitudCancelarView,
    ArchivoUploadView,
)
from modules.solicitud.interfaces.views.tipo_permiso_view import TipoPermisoListView, TipoPermisoDetailView


urlpatterns = [
    path("", SolicitudListView.as_view()),
    path("upload/", ArchivoUploadView.as_view()),
    path('<int:solicitud_id>/', SolicitudDetailView.as_view(), name='solicitud-detail'),
    path("<int:solicitud_id>/aprobar/", SolicitudAprobarView.as_view()),
    path("<int:solicitud_id>/rechazar/", SolicitudRechazarView.as_view()),
    path("<int:solicitud_id>/cancelar/", SolicitudCancelarView.as_view()),
    path("tipos-permiso/", TipoPermisoListView.as_view()),
    path("tipos-permiso/<int:tipo_id>/", TipoPermisoDetailView.as_view()),
]