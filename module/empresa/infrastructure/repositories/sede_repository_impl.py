from typing import Optional, List
from shared.domain.value_objects import Coordenadas, RadioMetros
from modules.empresa.domain.entities.sede import Sede
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.empresa.infrastructure.models.sede_model import SedeModel


class DjangoSedeRepository(SedeRepository):
    def get_by_id(self, id: int) -> Optional[Sede]:
        try:
            return self._to_entity(SedeModel.objects.get(pk=id))
        except SedeModel.DoesNotExist:
            return None

    def get_by_empresa(self, empresa_id: int) -> List[Sede]:
        return [
            self._to_entity(m)
            for m in SedeModel.objects.filter(empresa_id=empresa_id)
        ]

    def save(self, sede: Sede) -> Sede:
        if sede.id:
            model = SedeModel.objects.get(pk=sede.id)
        else:
            model = SedeModel()

        model.empresa_id = sede.empresa_id
        model.nombre = sede.nombre
        model.direccion = sede.direccion
        model.latitud = sede.coordenadas.latitud
        model.longitud = sede.coordenadas.longitud
        model.radio_metros = sede.radio_metros.value
        model.es_activa = sede.es_activa
        model.fecha_actualizacion = sede.fecha_actualizacion
        model.save()

        sede.id = model.pk
        return sede

    def delete(self, id: int) -> None:
        SedeModel.objects.filter(pk=id).delete()

    def exists(self, id: int) -> bool:
        return SedeModel.objects.filter(pk=id).exists()

    def _to_entity(self, model: SedeModel) -> Sede:
        return Sede(
            id=model.pk,
            empresa_id=model.empresa_id,
            nombre=model.nombre,
            direccion=model.direccion,
            coordenadas=Coordenadas(float(model.latitud), float(model.longitud)),
            radio_metros=RadioMetros(model.radio_metros),
            es_activa=model.es_activa,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )