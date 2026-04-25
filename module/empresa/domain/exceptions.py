from shared.domain.exceptions import DomainException, BusinessRuleViolationException


class EmpresaYaRegistradaException(BusinessRuleViolationException):
    def __init__(self, ruc: str):
        super().__init__(message=f"La empresa con RUC '{ruc}' ya se encuentra registrada en el sistema.")
        self.code = "empresa_ya_registrada"


class RucInvalidoException(DomainException):
    def __init__(self, ruc: str):
        super().__init__(
            message=f"El RUC '{ruc}' no corresponde a una empresa activa y habilitada en SUNAT.",
            code="ruc_invalido",
        )


class EmpresaNoEncontradaException(DomainException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"La empresa con identificador '{identifier}' no fue encontrada.",
            code="empresa_no_encontrada",
        )


class SedeNoEncontradaException(DomainException):
    def __init__(self, identifier: str):
        super().__init__(
            message=f"La sede con identificador '{identifier}' no fue encontrada.",
            code="sede_no_encontrada",
        )


class EmpresaSuspendidaException(DomainException):
    def __init__(self):
        super().__init__(
            message="La empresa se encuentra suspendida y no puede realizar esta operación.",
            code="empresa_suspendida",
        )


class ModificacionRucNoPermitidaException(BusinessRuleViolationException):
    def __init__(self):
        super().__init__(message="El número de RUC de una empresa no puede ser modificado.")
        self.code = "modificacion_ruc_no_permitida"