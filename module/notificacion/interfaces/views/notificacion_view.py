from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from modules.notificacion.interfaces.serializers.notificacion_serializer import (
    NotificacionOutputSerializer,
    ConfigurarPreferenciasSerializer,
)
from modules.notificacion.infrastructure.repositories.notificacion_repository_impl import DjangoNotificacionRepository
from modules.notificacion.application.use_cases.configurar_preferencias import ConfigurarPreferenciasUseCase
from modules.notificacion.application.dtos.notificacion_dto import ConfigurarPreferenciasInputDTO


class NotificacionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        solo_no_leidas = request.query_params.get("no_leidas", "false").lower() == "true"
        repo = DjangoNotificacionRepository()
        notificaciones = repo.get_by_usuario(
            usuario_id=request.usuario_id,
            solo_no_leidas=solo_no_leidas,
            page=int(request.query_params.get("page", 1)),
        )
        no_leidas = repo.count_no_leidas(request.usuario_id)

        from modules.notificacion.application.dtos.notificacion_dto import NotificacionOutputDTO
        outputs = [
            NotificacionOutputDTO(
                id=n.id, usuario_id=n.usuario_id, titulo=n.titulo,
                mensaje=n.mensaje, canal=n.canal, leida=n.leida,
                enviada=n.enviada, fecha_envio=n.fecha_envio,
                fecha_creacion=n.fecha_creacion,
            )
            for n in notificaciones
        ]
        return Response({
            "no_leidas": no_leidas,
            "results": NotificacionOutputSerializer(outputs, many=True).data,
        })


class NotificacionMarcarLeidaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notificacion_id):
        repo = DjangoNotificacionRepository()
        notificacion = repo.get_by_id(notificacion_id)
        if notificacion and notificacion.usuario_id == request.usuario_id:
            notificacion.marcar_como_leida()
            repo.save(notificacion)
        return Response({"status": "ok"})


class PreferenciasView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ConfigurarPreferenciasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        class _PrefRepo:
            def guardar(self, usuario_id, email_habilitado, push_habilitado):
                pass

        ConfigurarPreferenciasUseCase(_PrefRepo()).execute(
            ConfigurarPreferenciasInputDTO(
                usuario_id=request.usuario_id,
                **serializer.validated_data,
            )
        )
        return Response({"status": "ok"})