from typing import Dict, Any

class SuspensionPolicyResult:
    def __init__(self, permitido: bool, motivo: str = "", accion_requerida: str = ""):
        self.permitido = permitido
        self.motivo = motivo
        self.accion_requerida = accion_requerida


class SuspensionPolicyService:
    @staticmethod
    def evaluar(empresa_estado: str, suscripcion: Any) -> SuspensionPolicyResult:
        """
        Evalúa si una empresa puede ser suspendida basándose en las reglas de negocio empresariales.
        :param empresa_estado: El estado actual de la empresa.
        :param suscripcion: El objeto suscripción activo de la empresa.
        :return: SuspensionPolicyResult
        """
        if empresa_estado == "SUSPENDIDA":
            return SuspensionPolicyResult(
                permitido=False,
                motivo="La empresa ya se encuentra suspendida.",
                accion_requerida="Ninguna acción requerida."
            )

        # Si no hay suscripción, asumimos que es el plan básico o algo falló, se permite pero es raro.
        if not suscripcion:
            return SuspensionPolicyResult(permitido=True)

        # Asumimos que el plan gratuito tiene costo 0 o se llama 'Básico'
        # Podríamos usar el nombre del plan o el precio para determinar si es de pago.
        # En nuestro sistema, el plan Básico cuesta 0.00
        # Verificamos por el nombre del plan, ya que la entidad de dominio no contiene el precio.
        es_plan_pago = suscripcion.plan_nombre and "básico" not in suscripcion.plan_nombre.lower() and "basico" not in suscripcion.plan_nombre.lower()
        if es_plan_pago:
            return SuspensionPolicyResult(
                permitido=False,
                motivo=f"La empresa posee una suscripción activa de pago ({suscripcion.plan_nombre}).",
                accion_requerida="Cambie primero al plan Básico o cancele la suscripción antes de suspenderla."
            )

        return SuspensionPolicyResult(permitido=True)
