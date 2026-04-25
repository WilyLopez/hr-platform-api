from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from modules.solicitud.domain.entities.tipo_permiso import TipoPermiso
from modules.solicitud.domain.repositories.tipo_permiso_repository import TipoPermisoRepository
from modules.solicitud.domain.exceptions import TipoPermisoNoEncontradoException
from modules.solicitud.application.dtos.tipo_permiso_dto import (
    CrearTipoPermisoInputDTO,
    ActualizarTipoPermisoInputDTO,
    TipoPermisoOutputDTO,
)


class CrearTipoPermisoUseCase(BaseUseCase[CrearTipoPermisoInputDTO, TipoPermisoOutputDTO]):
    def __init__(self, tipo_permiso_repository: TipoPermisoRepository):
        self._tipo_permiso_repository = tipo_permiso_repository

    def execute(self, input_dto: CrearTipoPermisoInputDTO) -> TipoPermisoOutputDTO:
        tipo = TipoPermiso(
            id=None,
            empresa_id=input_dto.empresa_id,
            nombre=input_dto.nombre,
            descripcion=input_dto.descripcion,
            requiere_adjunto=input_dto.requiere_adjunto,
            es_activo=True,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=None,
        )
        tipo = self._tipo_permiso_repository.save(tipo)
        return TipoPermisoOutputDTO(
            id=tipo.id,
            empresa_id=tipo.empresa_id,
            nombre=tipo.nombre,
            descripcion=tipo.descripcion,
            requiere_adjunto=tipo.requiere_adjunto,
            es_activo=tipo.es_activo,
        )


class ActualizarTipoPermisoUseCase(BaseUseCase[ActualizarTipoPermisoInputDTO, TipoPermisoOutputDTO]):
    def __init__(self, tipo_permiso_repository: TipoPermisoRepository):
        self._tipo_permiso_repository = tipo_permiso_repository

    def execute(self, input_dto: ActualizarTipoPermisoInputDTO) -> TipoPermisoOutputDTO:
        tipo = self._tipo_permiso_repository.get_by_id(input_dto.tipo_permiso_id)
        if not tipo or tipo.empresa_id != input_dto.empresa_id:
            raise TipoPermisoNoEncontradoException(str(input_dto.tipo_permiso_id))
        tipo.actualizar(input_dto.nombre, input_dto.descripcion, input_dto.requiere_adjunto)
        tipo = self._tipo_permiso_repository.save(tipo)
        return TipoPermisoOutputDTO(
            id=tipo.id,
            empresa_id=tipo.empresa_id,
            nombre=tipo.nombre,
            descripcion=tipo.descripcion,
            requiere_adjunto=tipo.requiere_adjunto,
            es_activo=tipo.es_activo,
        )