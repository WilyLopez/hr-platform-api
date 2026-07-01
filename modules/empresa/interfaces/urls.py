from django.urls import path
from modules.empresa.interfaces.views.empresa_view import (
    ValidarRucView, RegistrarEmpresaView, EmpresaDetailView, SuspenderEmpresaView, ListarEmpresasView, EmpresaMetricasView, ReactivarEmpresaView
)
from modules.empresa.interfaces.views.dashboard_view import SuperadminDashboardView
from modules.empresa.interfaces.views.sede_view import SedeListView, SedeDetailView
from modules.empresa.interfaces.views.administrador_view import AdministradoresView

urlpatterns = [
    path("dashboard-superadmin/", SuperadminDashboardView.as_view()),
    path("", ListarEmpresasView.as_view()),
    path("validar-ruc/<str:ruc>/", ValidarRucView.as_view()),
    path("registro/", RegistrarEmpresaView.as_view()),
    path("<int:empresa_id>/", EmpresaDetailView.as_view()),
    path("<int:empresa_id>/metricas/", EmpresaMetricasView.as_view()),
    path("<int:empresa_id>/suspender/", SuspenderEmpresaView.as_view()),
    path("<int:empresa_id>/reactivar/", ReactivarEmpresaView.as_view()),
    path("<int:empresa_id>/sedes/", SedeListView.as_view()),
    path("<int:empresa_id>/sedes/<int:sede_id>/", SedeDetailView.as_view()),
    path("<int:empresa_id>/administradores/", AdministradoresView.as_view()),
]