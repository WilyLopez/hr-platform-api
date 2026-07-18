from typing import Optional
from datetime import datetime
from modules.asistencia.domain.entities.token_qr import TokenQr
from modules.asistencia.domain.repositories.qr_repository import QrRepository
from modules.asistencia.infrastructure.models.qr_model import TokenQrModel


class DjangoQrRepository(QrRepository):
    def get_by_token(self, token: str) -> Optional[TokenQr]:
        try:
            return self._to_entity(TokenQrModel.objects.get(token=token))
        except TokenQrModel.DoesNotExist:
            return None

    def get_vigente_by_sede(self, sede_id: int) -> Optional[TokenQr]:
        from django.utils import timezone
        model = (
            TokenQrModel.objects
            .filter(sede_id=sede_id, es_activo=True, expira_en__gt=timezone.now())
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, token_qr: TokenQr) -> TokenQr:
        if token_qr.id:
            model = TokenQrModel.objects.get(pk=token_qr.id)
        else:
            model = TokenQrModel()

        model.empresa_id = token_qr.empresa_id
        model.sede_id = token_qr.sede_id
        model.token = token_qr.token
        model.nonce = token_qr.nonce
        model.firma = token_qr.firma
        model.expira_en = token_qr.expira_en
        model.es_activo = token_qr.es_activo
        model.save()

        token_qr.id = model.pk
        return token_qr

    def desactivar_por_sede(self, sede_id: int) -> None:
        TokenQrModel.objects.filter(sede_id=sede_id, es_activo=True).update(es_activo=False)

    def _to_entity(self, model: TokenQrModel) -> TokenQr:
        return TokenQr(
            id=model.pk,
            empresa_id=model.empresa_id,
            sede_id=model.sede_id,
            token=model.token,
            nonce=model.nonce,
            firma=model.firma,
            expira_en=model.expira_en,
            es_activo=model.es_activo,
            fecha_creacion=model.fecha_creacion,
        )