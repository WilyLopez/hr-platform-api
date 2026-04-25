from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class BaseUseCase(ABC, Generic[InputDTO, OutputDTO]):
    @abstractmethod
    def execute(self, input_dto: InputDTO) -> OutputDTO:
        raise NotImplementedError


class BaseQueryUseCase(ABC, Generic[InputDTO, OutputDTO]):
    @abstractmethod
    def execute(self, input_dto: InputDTO) -> OutputDTO:
        raise NotImplementedError


class BaseCommandUseCase(ABC, Generic[InputDTO, OutputDTO]):
    @abstractmethod
    def execute(self, input_dto: InputDTO) -> OutputDTO:
        raise NotImplementedError