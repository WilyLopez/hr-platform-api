from shared.application.base_use_case import BaseUseCase
from modules.usuario.domain.exceptions import TokenInvalidoException
from modules.usuario.application.dtos.token_dto import RefrescarTokenInputDTO, RefrescarTokenOutputDTO


class RefrescarTokenUseCase(BaseUseCase[RefrescarTokenInputDTO, RefrescarTokenOutputDTO]):
    def __init__(self, jwt_service):
        self._jwt_service = jwt_service

    def execute(self, input_dto: RefrescarTokenInputDTO) -> RefrescarTokenOutputDTO:
        nuevo_access = self._jwt_service.refrescar_access_token(input_dto.refresh)
        if not nuevo_access:
            raise TokenInvalidoException()
        return RefrescarTokenOutputDTO(access=nuevo_access)