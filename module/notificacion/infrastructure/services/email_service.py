from django.core.mail import send_mail
from django.conf import settings
from shared.domain.exceptions import ExternalServiceException


class EmailService:
    def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinatario],
                fail_silently=False,
            )
        except Exception as exc:
            raise ExternalServiceException("Email", str(exc))

    def notificar_registro_empresa(self, correo: str, razon_social: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Bienvenido a SisRRHH",
            cuerpo=(
                f"Estimado cliente,\n\n"
                f"La empresa '{razon_social}' ha sido registrada exitosamente en SisRRHH.\n"
                f"Su periodo de prueba ha comenzado. Ingrese a la plataforma para configurar su cuenta.\n\n"
                f"Equipo SisRRHH"
            ),
        )

    def notificar_bienvenida_empleado(self, correo: str, codigo_unico: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Tu cuenta SisRRHH ha sido creada",
            cuerpo=(
                f"Bienvenido a SisRRHH.\n\n"
                f"Tu código de acceso es: {codigo_unico}\n"
                f"Descarga la aplicación móvil e ingresa con tu código para registrar tu asistencia.\n\n"
                f"Equipo SisRRHH"
            ),
        )

    def notificar_contrasena_temporal(self, correo: str, contrasena_temporal: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Contraseña temporal SisRRHH",
            cuerpo=(
                f"Tu contraseña temporal es: {contrasena_temporal}\n"
                f"Por favor, cámbiala después de iniciar sesión.\n\n"
                f"Equipo SisRRHH"
            ),
        )

    def notificar_nueva_solicitud(
        self, correo_admin: str, empleado_nombre: str, tipo_permiso: str, fecha_inicio, fecha_fin
    ) -> None:
        self.enviar(
            destinatario=correo_admin,
            asunto=f"Nueva solicitud de {tipo_permiso}",
            cuerpo=(
                f"El empleado {empleado_nombre} ha creado una solicitud de {tipo_permiso}.\n"
                f"Período: {fecha_inicio} al {fecha_fin}.\n"
                f"Ingrese a la plataforma para aprobar o rechazar.\n\n"
                f"Equipo SisRRHH"
            ),
        )

    def notificar_resultado_solicitud(
        self, correo: str, tipo_permiso: str, resultado: str, comentario: str = None
    ) -> None:
        self.enviar(
            destinatario=correo,
            asunto=f"Tu solicitud de {tipo_permiso} fue {resultado}",
            cuerpo=(
                f"Tu solicitud de {tipo_permiso} ha sido {resultado}.\n"
                + (f"Comentario del evaluador: {comentario}\n" if comentario else "")
                + "\nEquipo SisRRHH"
            ),
        )

    def notificar_suspension_por_pago(self, correo: str, empresa_nombre: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Suscripción suspendida — SisRRHH",
            cuerpo=(
                f"Estimado cliente de {empresa_nombre},\n\n"
                f"Su suscripción ha sido suspendida por falta de pago.\n"
                f"Por favor, regularice su situación para reactivar el acceso.\n\n"
                f"Equipo SisRRHH"
            ),
        )