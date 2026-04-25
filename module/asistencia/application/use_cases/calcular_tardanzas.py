from datetime import date
from typing import List
from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposMarcaje
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository


class CalcularTardanzasUseCase(BaseUseCase[dict, List[dict]]):
    def __init__(self, asistencia_repository: AsistenciaRepository):
        self._asistencia_repository = asistencia_repository

    def execute(self, input_dto: dict) -> List[dict]:
        registros = self._asistencia_repository.get_by_empresa(
            empresa_id=input_dto["empresa_id"],
            fecha=input_dto.get("fecha"),
        )

        hora_entrada_esperada = input_dto["hora_entrada_esperada"]
        resultado = []

        for registro in registros:
            if registro.tipo != TiposMarcaje.ENTRADA:
                continue
            es_tardanza = RegistroAsistencia.calcular_tardanza(
                registro.timestamp.time(), hora_entrada_esperada
            )
            if es_tardanza != registro.es_tardanza:
                registro.es_tardanza = es_tardanza
                self._asistencia_repository.save(registro)

            resultado.append({
                "registro_id": registro.id,
                "empleado_id": registro.empleado_id,
                "es_tardanza": es_tardanza,
                "timestamp": registro.timestamp,
            })

        return resultado