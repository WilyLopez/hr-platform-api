from django.core.mail import send_mail
from django.conf import settings
from shared.domain.exceptions import ExternalServiceException


class EmailService:
    def enviar(self, destinatario: str, asunto: str, cuerpo: str, html_cuerpo: str = None) -> None:
        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinatario],
                fail_silently=False,
                html_message=html_cuerpo,
            )
        except Exception as exc:
            raise ExternalServiceException("Email", str(exc))

    def notificar_registro_empresa(self, correo: str, razon_social: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Bienvenido a NexusRH",
            cuerpo=(
                f"Estimado cliente,\n\n"
                f"La empresa '{razon_social}' ha sido registrada exitosamente en NexusRH.\n"
                f"Su periodo de prueba ha comenzado. Ingrese a la plataforma para configurar su cuenta.\n\n"
                f"Equipo NexusRH"
            ),
        )

    def notificar_bienvenida_empleado(self, correo: str, codigo_unico: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Tu cuenta NexusRH ha sido creada",
            cuerpo=(
                f"Bienvenido a NexusRH.\n\n"
                f"Tu código de acceso es: {codigo_unico}\n"
                f"Descarga la aplicación móvil e ingresa con tu código para registrar tu asistencia.\n\n"
                f"Equipo NexusRH"
            ),
        )

    def notificar_contrasena_temporal(self, correo: str, contrasena_temporal: str) -> None:
        asunto = "Recuperación de contraseña — NexusRH"
        cuerpo = (
            f"Tu contraseña temporal es: {contrasena_temporal}\n"
            f"Por favor, cámbiala después de iniciar sesión.\n\n"
            f"Equipo NexusRH"
        )
        
        html_cuerpo = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #eaeaea; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #2563eb; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px; font-weight: bold;">NexusRH</h1>
            </div>
            <div style="padding: 30px; color: #333;">
                <h2 style="font-size: 20px; color: #111; margin-top: 0;">Recuperación de contraseña</h2>
                <p style="font-size: 15px; line-height: 1.5;">Hola,</p>
                <p style="font-size: 15px; line-height: 1.5;">Hemos recibido una solicitud para restablecer tu contraseña. Tu nueva clave de acceso temporal es:</p>
                
                <div style="background-color: #f4f4f5; padding: 20px; border-radius: 6px; text-align: center; margin: 25px 0;">
                    <span style="font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #111;">{contrasena_temporal}</span>
                </div>
                
                <p style="font-size: 15px; line-height: 1.5;">Por motivos de seguridad, te recomendamos iniciar sesión lo antes posible y <strong>cambiar esta contraseña</strong> desde la sección de tu perfil en la plataforma.</p>
                
                <br>
                <p style="font-size: 15px; line-height: 1.5;">Saludos cordiales,<br><strong>El equipo de NexusRH</strong></p>
            </div>
            <div style="background-color: #f9fafb; padding: 15px; text-align: center; border-top: 1px solid #eaeaea;">
                <p style="font-size: 12px; color: #6b7280; margin: 0;">© 2026 NexusRH. Todos los derechos reservados.</p>
            </div>
        </div>
        """
        
        self.enviar(
            destinatario=correo,
            asunto=asunto,
            cuerpo=cuerpo,
            html_cuerpo=html_cuerpo,
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
                f"Equipo NexusRH"
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
                + "\nEquipo NexusRH"
            ),
        )

    def notificar_suspension_por_pago(self, correo: str, empresa_nombre: str) -> None:
        self.enviar(
            destinatario=correo,
            asunto="Suscripción suspendida — NexusRH",
            cuerpo=(
                f"Estimado cliente de {empresa_nombre},\n\n"
                f"Su suscripción ha sido suspendida por falta de pago.\n"
                f"Por favor, regularice su situación para reactivar el acceso.\n\n"
                f"Equipo NexusRH"
            ),
        )