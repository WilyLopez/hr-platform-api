from django.urls import path
from modules.suscripcion.interfaces.views.plan_view import PlanListView, PlanDetailView
from modules.suscripcion.interfaces.views.suscripcion_view import SuscripcionDetailView, CambiarPlanView, SuperadminCambiarPlanView, SuperadminSuscripcionesView

urlpatterns = [
    path("planes/", PlanListView.as_view()),
    path("planes/<int:plan_id>/", PlanDetailView.as_view()),
    path("mi-suscripcion/", SuscripcionDetailView.as_view()),
    path("mi-suscripcion/cambiar-plan/", CambiarPlanView.as_view()),
    path("superadmin/empresas/<int:empresa_id>/cambiar-plan/", SuperadminCambiarPlanView.as_view()),
    path("superadmin/suscripciones/", SuperadminSuscripcionesView.as_view()),
]