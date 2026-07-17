from django.db import models


class TokenQrModel(models.Model):
    empresa_id = models.IntegerField()
    sede_id = models.IntegerField()
    token = models.CharField(max_length=128, unique=True)
    nonce = models.CharField(max_length=64, default="")
    firma = models.CharField(max_length=128, default="")
    expira_en = models.DateTimeField()
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "asistencia"
        db_table = "tokens_qr"
        indexes = [
            models.Index(fields=["sede_id", "es_activo"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"QR sede {self.sede_id} - {'activo' if self.es_activo else 'inactivo'}"