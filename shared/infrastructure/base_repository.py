from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

EntityType = TypeVar("EntityType")
IDType = TypeVar("IDType")


class BaseRepository(ABC, Generic[EntityType, IDType]):
    @abstractmethod
    def get_by_id(self, id: IDType) -> Optional[EntityType]:
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: EntityType) -> EntityType:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: IDType) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, id: IDType) -> bool:
        raise NotImplementedError