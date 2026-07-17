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
        asunto = "Bienvenido a NexusRH - Su plataforma de gestión de recursos humanos"
        cuerpo = (
            f"Estimado cliente,\n\n"
            f"Nos complace darle la bienvenida a NexusRH.\n"
            f"La empresa '{razon_social}' ha sido registrada exitosamente y su entorno corporativo está listo.\n"
            f"Su periodo de prueba premium ha comenzado. Ingrese a la plataforma para configurar su organización.\n\n"
            f"Atentamente,\nDirección Ejecutiva NexusRH"
        )
        
        html_cuerpo = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">NexusRH</h1>
                <p style="color: #bfdbfe; margin: 8px 0 0 0; font-size: 15px; font-weight: 300; letter-spacing: 0.5px;">Excelencia en Gestión del Talento</p>
            </div>
            
            <div style="padding: 40px 35px; color: #334155; background-color: #ffffff;">
                <h2 style="font-size: 22px; color: #0f172a; margin-top: 0; margin-bottom: 20px; text-align: center; font-weight: 600;">Bienvenido a su nueva plataforma</h2>
                
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 25px;">
                    Estimado equipo directivo,
                </p>
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 25px;">
                    Nos complace confirmar que la organización <strong>{razon_social}</strong> ha sido registrada exitosamente y su entorno corporativo ya se encuentra desplegado y listo para operar.
                </p>
                
                <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 20px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                    <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #1e40af;">Su entorno está listo</h3>
                    <p style="margin: 0; font-size: 15px; color: #475569; line-height: 1.6;">
                        A partir de este momento, su periodo de prueba ha comenzado. Hemos habilitado todas las herramientas para que experimente el control total sobre la asistencia, solicitudes y auditoría de su personal.
                    </p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 30px;">
                    En un correo separado, se le han enviado de manera segura las credenciales de acceso administrativo (Propietario). Le sugerimos ingresar a la plataforma a la brevedad para configurar las políticas de su empresa y dar de alta a sus primeros colaboradores.
                </p>
                
                <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
                    <a href="http://localhost:3000/admin/login" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-weight: 600; font-size: 16px; display: inline-block; transition: background-color 0.3s ease;">
                        Acceder al Panel de Control
                    </a>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 35px 0;">
                
                <p style="font-size: 15px; line-height: 1.6; color: #475569;">
                    Atentamente,<br>
                    <strong style="color: #0f172a;">Dirección Ejecutiva</strong><br>
                    <span style="font-size: 14px; color: #64748b;">NexusRH Technologies</span>
                </p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 20px; text-align: center;">
                <p style="font-size: 12px; color: #64748b; margin: 0; line-height: 1.5;">Este mensaje contiene información confidencial dirigida exclusivamente a los representantes de la empresa. Por favor no responda a esta dirección.</p>
                <p style="font-size: 12px; color: #64748b; margin: 10px 0 0 0;">&copy; 2026 NexusRH. Todos los derechos reservados.</p>
            </div>
        </div>
        """
        
        self.enviar(
            destinatario=correo,
            asunto=asunto,
            cuerpo=cuerpo,
            html_cuerpo=html_cuerpo,
        )

    def notificar_bienvenida_empleado(self, correo: str, codigo_unico: str, contrasena: str) -> None:
        asunto = "Credenciales de Acceso - NexusRH"
        cuerpo = (
            f"Bienvenido a NexusRH.\n\n"
            f"Su código de acceso es: {codigo_unico}\n"
            f"Su contraseña temporal es: {contrasena}\n"
            f"Por motivos de seguridad, el sistema le pedirá cambiar esta contraseña obligatoriamente la primera vez que inicie sesión.\n\n"
            f"Equipo NexusRH"
        )
        
        html_cuerpo = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">NexusRH</h1>
                <p style="color: #bfdbfe; margin: 8px 0 0 0; font-size: 15px; font-weight: 300; letter-spacing: 0.5px;">Excelencia en Gestión del Talento</p>
            </div>
            
            <div style="padding: 40px 35px; color: #334155; background-color: #ffffff;">
                <h2 style="font-size: 22px; color: #0f172a; margin-top: 0; margin-bottom: 20px; text-align: center; font-weight: 600;">Credenciales de Acceso</h2>
                
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 25px; text-align: center;">
                    Su cuenta en la plataforma ha sido habilitada exitosamente. A continuación, encontrará sus datos de acceso seguros:
                </p>
                
                <div style="background-color: #f8fafc; padding: 30px; border-radius: 8px; margin: 30px 0; border: 1px solid #e2e8f0; text-align: center;">
                    <p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">Código Único / Usuario</p>
                    <p style="margin: 0 0 25px 0; font-size: 24px; font-weight: 700; color: #0f172a; letter-spacing: 2px;">{codigo_unico}</p>
                    
                    <p style="margin: 0 0 8px 0; font-size: 14px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">Contraseña Temporal</p>
                    <p style="margin: 0; font-size: 24px; font-weight: 700; color: #0f172a; letter-spacing: 2px; font-family: monospace;">{contrasena}</p>
                </div>
                
                <div style="background-color: #fff1f2; border-left: 4px solid #e11d48; padding: 18px 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0;">
                    <h3 style="margin: 0 0 8px 0; font-size: 15px; color: #be123c;">Aviso de Seguridad Obligatorio</h3>
                    <p style="margin: 0; font-size: 14px; color: #9f1239; line-height: 1.6;">
                        Por políticas de privacidad, el sistema requerirá que <strong>cambie esta contraseña</strong> de manera obligatoria durante su primer inicio de sesión.
                    </p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 30px; text-align: center;">
                    Puede ingresar al portal administrativo web o descargar nuestra aplicación móvil para registrar su asistencia y gestionar solicitudes.
                </p>
                
                <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
                    <a href="http://localhost:3000/admin/login" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-weight: 600; font-size: 16px; display: inline-block; transition: background-color 0.3s ease;">
                        Iniciar Sesión
                    </a>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 35px 0;">
                
                <p style="font-size: 15px; line-height: 1.6; color: #475569;">
                    Atentamente,<br>
                    <strong style="color: #0f172a;">Soporte Técnico</strong><br>
                    <span style="font-size: 14px; color: #64748b;">NexusRH Technologies</span>
                </p>
            </div>
            
            <div style="background-color: #f1f5f9; padding: 20px; text-align: center;">
                <p style="font-size: 12px; color: #64748b; margin: 0; line-height: 1.5;">Este mensaje ha sido generado automáticamente de forma encriptada. Por favor no responda a esta dirección.</p>
                <p style="font-size: 12px; color: #64748b; margin: 10px 0 0 0;">&copy; 2026 NexusRH. Todos los derechos reservados.</p>
            </div>
        </div>
        """
        
        self.enviar(
            destinatario=correo,
            asunto=asunto,
            cuerpo=cuerpo,
            html_cuerpo=html_cuerpo,
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

    def notificar_suspension_empresa(self, correo: str, empresa_nombre: str, motivo: str) -> None:
        asunto = "Aviso Importante: Suspensión de su cuenta - NexusRH"
        cuerpo = (
            f"Estimado representante de {empresa_nombre},\n\n"
            f"Le informamos que su empresa ha sido suspendida de nuestra plataforma.\n"
            f"Motivo: {motivo}\n\n"
            f"Por favor contacte a su administrador o a soporte técnico para resolver esta situación.\n\n"
            f"Atentamente,\nDirección Ejecutiva NexusRH"
        )

        html_cuerpo = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            <div style="background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); padding: 35px 25px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">NexusRH</h1>
                <p style="color: #fda4af; margin: 8px 0 0 0; font-size: 15px; font-weight: 300; letter-spacing: 0.5px;">Aviso de Sistema</p>
            </div>
            <div style="padding: 40px 35px; color: #334155; background-color: #ffffff;">
                <h2 style="font-size: 22px; color: #0f172a; margin-top: 0; margin-bottom: 20px; text-align: center; font-weight: 600;">Cuenta Suspendida</h2>
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 25px;">
                    Estimado representante de <strong>{empresa_nombre}</strong>,
                </p>
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 25px;">
                    Le informamos que los servicios de su empresa en la plataforma han sido temporalmente suspendidos.
                </p>
                <div style="background-color: #fff1f2; border-left: 4px solid #e11d48; padding: 20px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                    <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #9f1239;">Detalles de la suspensión</h3>
                    <p style="margin: 0; font-size: 15px; color: #475569; line-height: 1.6;">
                        <strong>Motivo registrado:</strong> {motivo}
                    </p>
                </div>
                <p style="font-size: 16px; line-height: 1.7; color: #475569; margin-bottom: 30px;">
                    Para reactivar su acceso y el de sus empleados, le pedimos ponerse en contacto con nuestro equipo de soporte técnico a la mayor brevedad.
                </p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 35px 0;">
                <p style="font-size: 15px; line-height: 1.6; color: #475569;">
                    Atentamente,<br>
                    <strong style="color: #0f172a;">Dirección Ejecutiva</strong><br>
                    <span style="font-size: 14px; color: #64748b;">NexusRH Technologies</span>
                </p>
            </div>
        </div>
        """
        
        self.enviar(
            destinatario=correo,
            asunto=asunto,
            cuerpo=cuerpo,
            html_cuerpo=html_cuerpo,
        )