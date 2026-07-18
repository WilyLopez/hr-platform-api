from django.urls import path
from modules.horario.interfaces.views.horario_view import HorarioListView, HorarioDetailView
from modules.horario.interfaces.views.asignacion_view import AsignarHorarioView, AsignacionEmpleadoListView

urlpatterns = [
    path('horarios/', HorarioListView.as_view(), name='horario-list'),
    path('horarios/<int:horario_id>/', HorarioDetailView.as_view(), name='horario-detail'),
    path('asignaciones/', AsignarHorarioView.as_view(), name='asignacion-create'),
    path('empleados/<int:empleado_id>/asignaciones/', AsignacionEmpleadoListView.as_view(), name='asignacion-empleado-list'),
]
