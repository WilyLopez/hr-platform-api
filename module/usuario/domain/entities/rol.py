from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set
from shared.constants import RolesUsuario


@dataclass
class Rol:
    id: Optional[int]
    empresa_id: Optional[int]
    nombre: str
    permisos: Set[str]
    es_sistema: bool
    fecha_creacion: datetime

    def tiene_permiso(self, permiso: str) -> bool:
        return permiso in self.permisos

    def agregar_permiso(self, permiso: str) -> None:
        self.permisos.add(permiso)

    def remover_permiso(self, permiso: str) -> None:
        self.permisos.discard(permiso)

    def es_superadmin(self) -> bool:
        return self.nombre == RolesUsuario.SUPERADMIN

    def es_propietario(self) -> bool:
        return self.nombre == RolesUsuario.PROPIETARIO

    def es_admin(self) -> bool:
        return self.nombre == RolesUsuario.ADMIN

    def es_empleado(self) -> bool:
        return self.nombre == RolesUsuario.EMPLEADO

    def accede_plataforma_web(self) -> bool:
        return self.nombre in RolesUsuario.ROLES_PLATAFORMA_WEB

    def accede_app_movil(self) -> bool:
        return self.nombre in RolesUsuario.ROLES_APP_MOVIL