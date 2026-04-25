from django.conf import settings


class RolesUsuario:
    SUPERADMIN = "SUPERADMIN"
    PROPIETARIO = "PROPIETARIO"
    ADMIN = "ADMIN"
    EMPLEADO = "EMPLEADO"

    CHOICES = [
        (SUPERADMIN, "Super Administrador"),
        (PROPIETARIO, "Propietario"),
        (ADMIN, "Administrador"),
        (EMPLEADO, "Empleado"),
    ]

    ROLES_PLATAFORMA_WEB = {SUPERADMIN, PROPIETARIO, ADMIN}
    ROLES_APP_MOVIL = {EMPLEADO}


class EstadosEmpresa:
    ACTIVA = "ACTIVA"
    SUSPENDIDA = "SUSPENDIDA"
    EN_PRUEBA = "EN_PRUEBA"
    ELIMINADA = "ELIMINADA"

    CHOICES = [
        (ACTIVA, "Activa"),
        (SUSPENDIDA, "Suspendida"),
        (EN_PRUEBA, "En periodo de prueba"),
        (ELIMINADA, "Eliminada"),
    ]


class EstadosUsuario:
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"

    CHOICES = [
        (ACTIVO, "Activo"),
        (INACTIVO, "Inactivo"),
        (BLOQUEADO, "Bloqueado"),
    ]


class EstadosEmpleado:
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"

    CHOICES = [
        (ACTIVO, "Activo"),
        (INACTIVO, "Inactivo"),
    ]


class TiposMarcaje:
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"

    CHOICES = [
        (ENTRADA, "Entrada"),
        (SALIDA, "Salida"),
    ]


class MetodosMarcaje:
    QR = "QR"
    MANUAL = "MANUAL"

    CHOICES = [
        (QR, "Código QR"),
        (MANUAL, "Registro manual"),
    ]


class EstadosSolicitud:
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"

    CHOICES = [
        (PENDIENTE, "Pendiente"),
        (EN_REVISION, "En revisión"),
        (APROBADA, "Aprobada"),
        (RECHAZADA, "Rechazada"),
        (CANCELADA, "Cancelada"),
    ]

    TRANSICIONES_VALIDAS = {
        PENDIENTE: {EN_REVISION, CANCELADA},
        EN_REVISION: {APROBADA, RECHAZADA},
        APROBADA: set(),
        RECHAZADA: set(),
        CANCELADA: set(),
    }


class PlanesNombre:
    BASICO = "BASICO"
    PRO = "PRO"

    CHOICES = [
        (BASICO, "Plan Básico"),
        (PRO, "Plan Pro"),
    ]


class EstadosSuscripcion:
    TRIAL = "TRIAL"
    ACTIVA = "ACTIVA"
    VENCIDA = "VENCIDA"
    SUSPENDIDA = "SUSPENDIDA"

    CHOICES = [
        (TRIAL, "Periodo de prueba"),
        (ACTIVA, "Activa"),
        (VENCIDA, "Vencida"),
        (SUSPENDIDA, "Suspendida"),
    ]


class TiposEvento:
    INICIO_SESION = "INICIO_SESION"
    CIERRE_SESION = "CIERRE_SESION"
    INTENTO_FALLIDO = "INTENTO_FALLIDO"
    CREACION_USUARIO = "CREACION_USUARIO"
    MODIFICACION_USUARIO = "MODIFICACION_USUARIO"
    ELIMINACION_USUARIO = "ELIMINACION_USUARIO"
    CREACION_EMPLEADO = "CREACION_EMPLEADO"
    MODIFICACION_EMPLEADO = "MODIFICACION_EMPLEADO"
    REGISTRO_ASISTENCIA = "REGISTRO_ASISTENCIA"
    REGISTRO_MANUAL = "REGISTRO_MANUAL"
    CREACION_SOLICITUD = "CREACION_SOLICITUD"
    APROBACION_SOLICITUD = "APROBACION_SOLICITUD"
    RECHAZO_SOLICITUD = "RECHAZO_SOLICITUD"
    SUSPENSION_EMPRESA = "SUSPENSION_EMPRESA"
    ELIMINACION_EMPRESA = "ELIMINACION_EMPRESA"

    CHOICES = [
        (INICIO_SESION, "Inicio de sesión"),
        (CIERRE_SESION, "Cierre de sesión"),
        (INTENTO_FALLIDO, "Intento fallido"),
        (CREACION_USUARIO, "Creación de usuario"),
        (MODIFICACION_USUARIO, "Modificación de usuario"),
        (ELIMINACION_USUARIO, "Eliminación de usuario"),
        (CREACION_EMPLEADO, "Creación de empleado"),
        (MODIFICACION_EMPLEADO, "Modificación de empleado"),
        (REGISTRO_ASISTENCIA, "Registro de asistencia"),
        (REGISTRO_MANUAL, "Registro manual"),
        (CREACION_SOLICITUD, "Creación de solicitud"),
        (APROBACION_SOLICITUD, "Aprobación de solicitud"),
        (RECHAZO_SOLICITUD, "Rechazo de solicitud"),
        (SUSPENSION_EMPRESA, "Suspensión de empresa"),
        (ELIMINACION_EMPRESA, "Eliminación de empresa"),
    ]


class TiposDocumento:
    DNI = "DNI"
    CE = "CE"
    PASAPORTE = "PASAPORTE"
    RUC = "RUC"

    CHOICES = [
        (DNI, "DNI"),
        (CE, "Carné de Extranjería"),
        (PASAPORTE, "Pasaporte"),
        (RUC, "RUC"),
    ]


MAX_LOGIN_ATTEMPTS = getattr(settings, "MAX_LOGIN_ATTEMPTS", 5)
TRIAL_PERIOD_DAYS = getattr(settings, "TRIAL_PERIOD_DAYS", 30)
QR_EXPIRY_DEFAULT_MINUTES = getattr(settings, "QR_EXPIRY_DEFAULT_MINUTES", 480)
QR_EXPIRY_MIN_MINUTES = 1
QR_EXPIRY_MAX_MINUTES = 1440
SESSION_INACTIVITY_MINUTES = getattr(settings, "SESSION_INACTIVITY_MINUTES", 30)
AUDIT_RETENTION_MONTHS = getattr(settings, "AUDIT_RETENTION_MONTHS", 12)
TRIAL_ALERT_DAYS_BEFORE = 7
PAYMENT_GRACE_DAYS = 5